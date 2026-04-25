from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.partner import Partner
from ..models.package import Package
from ..models.booking import Booking
from ..models.social import Complaint
from ..schemas.user import UserPublic
from ..core.security import require_admin

_CONFIRMED = ("confirmed", "completed")

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _=Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_partners = db.query(func.count(Partner.id)).scalar() or 0
    total_packages = db.query(func.count(Package.id)).scalar() or 0
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0

    confirmed_bookings = (
        db.query(func.count(Booking.id))
        .filter(Booking.status.in_(_CONFIRMED))
        .scalar() or 0
    )
    gmv = (
        db.query(func.sum(Booking.total_price))
        .filter(Booking.status.in_(_CONFIRMED))
        .scalar() or 0.0
    )
    # Commission uses each partner's actual commission_rate, not a hardcoded 12%.
    platform_commission = (
        db.query(func.sum(Booking.total_price * Partner.commission_rate / 100))
        .join(Package, Booking.package_id == Package.id)
        .join(Partner, Package.partner_id == Partner.id)
        .filter(Booking.status.in_(_CONFIRMED))
        .scalar() or 0.0
    )

    pending_complaints = (
        db.query(func.count(Complaint.id)).filter(Complaint.status == "pending").scalar() or 0
    )
    pending_partners = (
        db.query(func.count(Partner.id)).filter(Partner.status == "pending").scalar() or 0
    )
    pending_packages = (
        db.query(func.count(Package.id)).filter(Package.status == "under_moderation").scalar() or 0
    )

    return {
        "total_users": total_users,
        "total_partners": total_partners,
        "total_packages": total_packages,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "gmv": round(gmv, 2),
        "platform_commission": round(platform_commission, 2),
        "pending_complaints": pending_complaints,
        "pending_partners": pending_partners,
        "pending_packages": pending_packages,
    }

@router.get("/users", response_model=List[UserPublic])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.put("/users/{user_id}/status")
def set_user_status(user_id: int, status: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    allowed = {"active", "verified", "warned", "restricted", "blocked"}
    if status not in allowed:
        raise HTTPException(400, f"Invalid status. Allowed: {allowed}")
    user.status = status
    db.commit()
    return {"message": f"User status set to {status}"}

@router.get("/partners")
def list_partners(db: Session = Depends(get_db), _=Depends(require_admin)):
    partners = db.query(Partner).all()
    return [
        {
            "id": p.id,
            "company_name": p.company_name,
            "partner_type": p.partner_type,
            "status": p.status,
            "user_id": p.user_id,
            "commission_rate": p.commission_rate,
            "created_at": p.created_at.isoformat(),
        }
        for p in partners
    ]

@router.put("/partners/{partner_id}/approve")
def approve_partner(partner_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(404, "Partner not found")
    partner.status = "active"
    user = db.query(User).filter(User.id == partner.user_id).first()
    if user:
        user.role = "partner"
    db.commit()
    return {"message": "Partner approved"}

@router.put("/partners/{partner_id}/suspend")
def suspend_partner(partner_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(404, "Partner not found")
    partner.status = "suspended"
    db.commit()
    return {"message": "Partner suspended"}

@router.get("/packages/pending")
def pending_packages(db: Session = Depends(get_db), _=Depends(require_admin)):
    pkgs = db.query(Package).filter(Package.status == "under_moderation").all()
    return [{"id": p.id, "title": p.title, "destination": p.destination, "price": p.price, "partner_id": p.partner_id} for p in pkgs]

@router.put("/packages/{package_id}/approve")
def approve_package(package_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    pkg.status = "published"
    db.commit()
    return {"message": "Package published"}

@router.put("/packages/{package_id}/reject")
def reject_package(package_id: int, reason: str = "Does not meet requirements", db: Session = Depends(get_db), _=Depends(require_admin)):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    pkg.status = "archived"
    db.commit()
    return {"message": f"Package rejected: {reason}"}

@router.get("/complaints")
def list_complaints(db: Session = Depends(get_db), _=Depends(require_admin)):
    complaints = db.query(Complaint).filter(Complaint.status == "pending").all()
    return [
        {"id": c.id, "reporter_id": c.reporter_id, "target_user_id": c.target_user_id, "reason": c.reason, "created_at": c.created_at.isoformat()}
        for c in complaints
    ]

_COMPLAINT_ACTIONS = {"warn", "dismiss", "block"}

@router.put("/complaints/{complaint_id}/resolve")
def resolve_complaint(complaint_id: int, action: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    if action not in _COMPLAINT_ACTIONS:
        raise HTTPException(400, f"Invalid action. Allowed: {sorted(_COMPLAINT_ACTIONS)}")
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    target = db.query(User).filter(User.id == complaint.target_user_id).first()
    if action == "dismiss":
        complaint.status = "dismissed"
    elif action == "warn":
        complaint.status = "action_taken"
        if target:
            target.complaint_count += 1
            if target.complaint_count >= 5:
                target.status = "blocked"
            elif target.complaint_count >= 3:
                target.status = "restricted"
            else:
                target.status = "warned"
    elif action == "block":
        complaint.status = "action_taken"
        if target:
            target.status = "blocked"
    db.commit()
    return {"message": f"Complaint resolved with action: {action}"}
