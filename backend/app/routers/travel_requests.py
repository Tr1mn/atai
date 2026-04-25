import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.partner import Partner
from ..models.travel_request import TravelOffer, TravelRequest
from ..schemas.travel_request import TravelOfferCreate, TravelOfferOut, TravelRequestCreate, TravelRequestOut
from ..core.security import get_current_user, require_partner

router = APIRouter(prefix="/api/travel-requests", tags=["travel-requests"])


def _dump(values: List[str]) -> str:
    return json.dumps(values or [], ensure_ascii=False)


def _load(raw: str) -> List[str]:
    try:
        value = json.loads(raw or "[]")
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def _partner_for_user(db: Session, user_id: int) -> Partner:
    partner = db.query(Partner).filter(Partner.user_id == user_id).first()
    if not partner or partner.status != "active":
        raise HTTPException(403, "Active partner account required")
    return partner


def _offer_out(offer: TravelOffer) -> TravelOfferOut:
    return TravelOfferOut(
        id=offer.id,
        request_id=offer.request_id,
        partner_id=offer.partner_id,
        partner_company=offer.partner.company_name if offer.partner else "Партнер",
        title=offer.title,
        description=offer.description,
        price_total=offer.price_total,
        price_per_person=offer.price_per_person,
        duration_days=offer.duration_days,
        included=offer.included,
        message=offer.message,
        status=offer.status,
        created_at=offer.created_at,
    )


def _request_out(req: TravelRequest, offers: List[TravelOffer] | None = None) -> TravelRequestOut:
    return TravelRequestOut(
        id=req.id,
        user_id=req.user_id,
        user_name=req.user.full_name if req.user else "Турист",
        origin=req.origin,
        days=req.days,
        companions=req.companions,
        interests=_load(req.interests),
        travel_format=req.travel_format,
        mood=req.mood,
        difficulty=req.difficulty,
        budget=req.budget,
        season=req.season,
        accommodation=req.accommodation,
        transport=req.transport,
        activities=_load(req.activities),
        preferred_places=_load(req.preferred_places),
        distance=req.distance,
        priority=req.priority,
        notes=req.notes,
        status=req.status,
        created_at=req.created_at,
        offers=[_offer_out(o) for o in (offers if offers is not None else req.offers)],
    )


@router.post("/", response_model=TravelRequestOut, status_code=201)
def create_travel_request(
    data: TravelRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    req = TravelRequest(
        user_id=current_user.id,
        origin=data.origin,
        days=data.days,
        companions=data.companions,
        interests=_dump(data.interests),
        travel_format=data.travel_format,
        mood=data.mood,
        difficulty=data.difficulty,
        budget=data.budget,
        season=data.season,
        accommodation=data.accommodation,
        transport=data.transport,
        activities=_dump(data.activities),
        preferred_places=_dump(data.preferred_places),
        distance=data.distance,
        priority=data.priority,
        notes=data.notes,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return _request_out(req)


@router.get("/me", response_model=List[TravelRequestOut])
def my_travel_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    requests = (
        db.query(TravelRequest)
        .filter(TravelRequest.user_id == current_user.id)
        .order_by(TravelRequest.created_at.desc())
        .all()
    )
    return [_request_out(req) for req in requests]


@router.get("/open", response_model=List[TravelRequestOut])
def open_travel_requests(db: Session = Depends(get_db), current_user=Depends(require_partner)):
    partner = _partner_for_user(db, current_user.id)
    requests = (
        db.query(TravelRequest)
        .filter(TravelRequest.status == "open")
        .order_by(TravelRequest.created_at.desc())
        .all()
    )
    result = []
    for req in requests:
        own_offers = [offer for offer in req.offers if offer.partner_id == partner.id]
        result.append(_request_out(req, offers=own_offers))
    return result


@router.post("/{request_id}/offers", response_model=TravelOfferOut, status_code=201)
def create_offer(
    request_id: int,
    data: TravelOfferCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_partner),
):
    partner = _partner_for_user(db, current_user.id)
    req = db.query(TravelRequest).filter(TravelRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Travel request not found")
    if req.status != "open":
        raise HTTPException(400, "This request is no longer open")

    existing = db.query(TravelOffer).filter(
        TravelOffer.request_id == request_id,
        TravelOffer.partner_id == partner.id,
    ).first()
    if existing:
        raise HTTPException(400, "You already sent an offer for this request")

    offer = TravelOffer(
        request_id=request_id,
        partner_id=partner.id,
        title=data.title,
        description=data.description,
        price_total=data.price_total,
        price_per_person=data.price_per_person,
        duration_days=data.duration_days,
        included=data.included,
        message=data.message,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return _offer_out(offer)


@router.put("/offers/{offer_id}/accept", response_model=TravelOfferOut)
def accept_offer(offer_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    offer = db.query(TravelOffer).filter(TravelOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(404, "Offer not found")
    if offer.request.user_id != current_user.id:
        raise HTTPException(403, "You can only accept offers for your own request")
    if offer.request.status != "open":
        raise HTTPException(400, "This request is already closed")

    offer.status = "accepted"
    offer.request.status = "matched"
    for other in offer.request.offers:
        if other.id != offer.id and other.status == "submitted":
            other.status = "declined"
    db.commit()
    db.refresh(offer)
    return _offer_out(offer)
