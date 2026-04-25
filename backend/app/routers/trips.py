from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.trip import Trip, TripMember
from ..schemas.trip import TripCreate, TripOut
from ..core.security import get_current_user

router = APIRouter(prefix="/api/trips", tags=["trips"])

@router.get("/", response_model=List[TripOut])
def list_trips(
    destination: Optional[str] = None,
    travel_style: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Trip).filter(Trip.status.in_(["open", "group_formed"]))
    if destination:
        q = q.filter(Trip.destination.ilike(f"%{destination}%"))
    if travel_style:
        q = q.filter(Trip.travel_style == travel_style)
    return q.order_by(Trip.created_at.desc()).all()

@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    return trip

@router.post("/", response_model=TripOut, status_code=201)
def create_trip(data: TripCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if data.end_date <= data.start_date:
        raise HTTPException(400, "end_date must be after start_date")
    if data.max_size < data.min_size:
        raise HTTPException(400, "max_size must be >= min_size")

    trip = Trip(
        organizer_id=current_user.id,
        title=data.title,
        destination=data.destination,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        min_size=data.min_size,
        max_size=data.max_size,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
        travel_style=data.travel_style,
        photo_url=data.photo_url,
        current_size=1,
        status="open",
    )
    db.add(trip)
    db.flush()

    # Organizer is auto-accepted member
    member = TripMember(trip_id=trip.id, user_id=current_user.id, status="accepted")
    db.add(member)
    db.commit()
    db.refresh(trip)
    return trip

@router.post("/{trip_id}/join", status_code=201)
def join_trip(trip_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.status == "open").first()
    if not trip:
        raise HTTPException(404, "Trip not found or not open")
    if trip.current_size >= trip.max_size:
        raise HTTPException(400, "Trip is full")

    existing = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(400, "Already applied or member")

    member = TripMember(trip_id=trip_id, user_id=current_user.id, status="pending")
    db.add(member)
    db.commit()
    return {"message": "Join request sent"}

@router.post("/{trip_id}/members/{user_id}/accept")
def accept_member(trip_id: int, user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.organizer_id == current_user.id).first()
    if not trip:
        raise HTTPException(403, "Not your trip")
    if trip.current_size >= trip.max_size:
        raise HTTPException(400, "Trip is full")

    member = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == user_id,
        TripMember.status == "pending",
    ).first()
    if not member:
        raise HTTPException(404, "Pending member not found")

    member.status = "accepted"
    trip.current_size += 1

    if trip.current_size >= trip.min_size:
        trip.status = "group_formed"

    db.commit()
    return {"message": "Member accepted", "trip_status": trip.status}
