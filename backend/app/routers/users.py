from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.social import Like, Match, Complaint, UserSkip
from ..schemas.user import IncomingLikeOut, MatchOut, UserPublic, UserMe, UserUpdate
from ..core.security import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserMe)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserMe)
def update_me(update: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

def _match_pair(user_a: int, user_b: int) -> tuple[int, int]:
    return min(user_a, user_b), max(user_a, user_b)


def _match_exists(db: Session, user_a: int, user_b: int) -> bool:
    u1, u2 = _match_pair(user_a, user_b)
    return db.query(Match).filter(Match.user1_id == u1, Match.user2_id == u2).first() is not None


@router.get("/me/matches", response_model=List[MatchOut])
def get_matches(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    matches = db.query(Match).filter(
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
    ).all()
    result = []
    for m in matches:
        other_id = m.user2_id if m.user1_id == current_user.id else m.user1_id
        other = db.query(User).filter(User.id == other_id).first()
        if other:
            result.append({
                "match_id": m.id,
                "user": {
                    "id": other.id,
                    "full_name": other.full_name,
                    "photo_url": other.photo_url,
                    "city": other.city,
                    "phone": other.phone,
                    "telegram": other.telegram,
                    "whatsapp": other.whatsapp,
                    "instagram": other.instagram,
                },
                "created_at": m.created_at.isoformat(),
            })
    return result

@router.get("/me/incoming-likes", response_model=List[IncomingLikeOut])
def incoming_likes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    incoming = (
        db.query(Like)
        .join(User, Like.from_user_id == User.id)
        .filter(
            Like.to_user_id == current_user.id,
            User.role == "tourist",
            User.status.in_(["active", "verified"]),
        )
        .order_by(Like.created_at.desc())
        .all()
    )

    result = []
    for like in incoming:
        from_user = like.from_user
        if not from_user:
            continue
        already_liked_back = db.query(Like).filter(
            Like.from_user_id == current_user.id,
            Like.to_user_id == from_user.id,
        ).first()
        skipped = db.query(UserSkip).filter(
            UserSkip.from_user_id == current_user.id,
            UserSkip.to_user_id == from_user.id,
        ).first()
        if already_liked_back or skipped or _match_exists(db, current_user.id, from_user.id):
            continue

        result.append({
            "like_id": like.id,
            "liked_at": like.created_at,
            "user": from_user,
        })
    return result

@router.get("/individual", response_model=List[UserPublic])
def get_individual_candidates(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    liked_ids = [l.to_user_id for l in db.query(Like).filter(Like.from_user_id == current_user.id).all()]
    skipped_ids = [s.to_user_id for s in db.query(UserSkip).filter(UserSkip.from_user_id == current_user.id).all()]
    excluded = set(liked_ids) | set(skipped_ids) | {current_user.id}

    q = db.query(User).filter(
        User.id.notin_(excluded),
        User.status.in_(["active", "verified"]),
        User.role == "tourist",
    )
    return q.limit(20).all()

@router.get("/", response_model=List[UserPublic])
def browse_users(
    travel_style: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    liked_ids = [l.to_user_id for l in db.query(Like).filter(Like.from_user_id == current_user.id).all()]
    skipped_ids = [s.to_user_id for s in db.query(UserSkip).filter(UserSkip.from_user_id == current_user.id).all()]
    excluded = set(liked_ids) | set(skipped_ids) | {current_user.id}

    q = db.query(User).filter(
        User.id.notin_(excluded),
        User.status.in_(["active", "verified"]),
        User.role == "tourist",
    )
    if travel_style:
        q = q.filter(User.travel_style == travel_style)
    if city:
        q = q.filter(User.city.ilike(f"%{city}%"))

    return q.limit(50).all()

@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/{user_id}/like", status_code=201)
def like_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot like yourself")
    existing = db.query(Like).filter(Like.from_user_id == current_user.id, Like.to_user_id == user_id).first()
    if existing:
        raise HTTPException(400, "Already liked")

    like = Like(from_user_id=current_user.id, to_user_id=user_id)
    db.add(like)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Already liked")

    # Check mutual like → create match.
    # Normalize user order (min, max) so concurrent threads attempt the same row,
    # letting the DB unique constraint catch the duplicate instead of creating two Match rows.
    reverse = db.query(Like).filter(Like.from_user_id == user_id, Like.to_user_id == current_user.id).first()
    matched = False
    match_id = None
    if reverse:
        u1, u2 = _match_pair(current_user.id, user_id)
        existing_match = db.query(Match).filter(Match.user1_id == u1, Match.user2_id == u2).first()
        if not existing_match:
            try:
                with db.begin_nested():  # savepoint — rollback here won't undo the Like above
                    match = Match(user1_id=u1, user2_id=u2)
                    db.add(match)
                    db.flush()
                match_id = match.id
                matched = True
            except IntegrityError:
                # Concurrent thread won the race; recover the match it created
                existing_match = db.query(Match).filter(Match.user1_id == u1, Match.user2_id == u2).first()
                match_id = existing_match.id if existing_match else None
                matched = match_id is not None

    db.commit()
    return {"matched": matched, "match_id": match_id, "contact_unlocked": matched}

@router.post("/{user_id}/skip", status_code=201)
def skip_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot skip yourself")

    skip = UserSkip(from_user_id=current_user.id, to_user_id=user_id)
    db.add(skip)
    try:
        db.flush()
        db.commit()
    except IntegrityError:
        db.rollback()
    return {"skipped": True}

@router.post("/{user_id}/report")
def report_user(user_id: int, reason: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(Complaint).filter(
        Complaint.reporter_id == current_user.id,
        Complaint.target_user_id == user_id,
        Complaint.status == "pending",
    ).first()
    if existing:
        raise HTTPException(400, "You already have a pending complaint against this user")
    complaint = Complaint(reporter_id=current_user.id, target_user_id=user_id, reason=reason)
    db.add(complaint)
    db.commit()
    return {"message": "Complaint filed"}
