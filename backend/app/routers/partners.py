from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.partner import Partner
from ..models.package import Package
from ..models.booking import Booking
from ..schemas.package import PackageOut
from ..schemas.booking import BookingOut
from ..core.security import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/partners", tags=["partners"])

class PartnerApply(BaseModel):
    company_name: str
    legal_info: str
    partner_type: str = "agency"

@router.post("/apply", status_code=201)
def apply_partner(data: PartnerApply, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(Partner).filter(Partner.user_id == current_user.id).first()
    if existing:
        raise HTTPException(400, "Already applied")
    if not data.legal_info:
        raise HTTPException(400, "Legal information required")
    partner = Partner(user_id=current_user.id, company_name=data.company_name, legal_info=data.legal_info, partner_type=data.partner_type)
    db.add(partner)
    # Role stays "tourist" until admin approves; set in admin.approve_partner
    db.commit()
    return {"message": "Application submitted — pending admin approval"}

@router.get("/me/packages", response_model=List[PackageOut])
def my_packages(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    partner = db.query(Partner).filter(Partner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(404, "Partner profile not found")
    return db.query(Package).filter(Package.partner_id == partner.id).all()

@router.get("/me/bookings", response_model=List[BookingOut])
def partner_bookings(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    partner = db.query(Partner).filter(Partner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(404, "Partner profile not found")
    pkg_ids = [p.id for p in db.query(Package).filter(Package.partner_id == partner.id).all()]
    return db.query(Booking).filter(Booking.package_id.in_(pkg_ids)).order_by(Booking.created_at.desc()).all()

@router.get("/me/stats")
def partner_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    partner = db.query(Partner).filter(Partner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(404, "Partner profile not found")
    pkg_ids = [p.id for p in db.query(Package).filter(Package.partner_id == partner.id).all()]
    bookings = db.query(Booking).filter(Booking.package_id.in_(pkg_ids)).all()
    confirmed = [b for b in bookings if b.status in ("confirmed", "completed")]
    gmv = sum(b.total_price for b in confirmed)
    commission = gmv * (partner.commission_rate / 100)
    return {
        "total_packages": len(pkg_ids),
        "total_bookings": len(bookings),
        "confirmed_bookings": len(confirmed),
        "gmv": round(gmv, 2),
        "commission_owed": round(commission, 2),
        "payout": round(gmv - commission, 2),
    }
