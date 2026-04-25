from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update, func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from ..database import get_db
from ..models.booking import Booking, WaitingList
from ..models.package import Package, PackageDate
from ..models.partner import Partner
from ..schemas.booking import BookingCreate, BookingOut, WaitingListOut
from ..core.security import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["bookings"])

def _calc_family_discount(num_travelers: int, package: Package) -> float:
    if not package.family_rates_enabled:
        return 0.0
    if num_travelers >= 4:
        return 30.0
    if num_travelers >= 2:
        return 20.0
    return 0.0

@router.post("/", response_model=BookingOut, status_code=201)
def create_booking(data: BookingCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    pkg = db.query(Package).filter(Package.id == data.package_id, Package.status == "published").first()
    if not pkg:
        raise HTTPException(404, "Package not available")

    pkg_date = db.query(PackageDate).filter(
        PackageDate.id == data.package_date_id,
        PackageDate.package_id == data.package_id,
    ).first()
    if not pkg_date:
        raise HTTPException(404, "Date not found")

    # Duplicate booking check
    existing = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.package_id == data.package_id,
        Booking.package_date_id == data.package_date_id,
        Booking.status.in_(["pending_payment", "paid", "pending_confirmation", "confirmed"]),
    ).first()
    if existing:
        raise HTTPException(400, "You already have an active booking for this date")

    # Atomic inventory decrement — a single UPDATE WHERE available_slots > 0
    # prevents double-booking under concurrent requests without application-level locks.
    # rowcount == 0 means another request won the race or there were never any slots.
    result = db.execute(
        update(PackageDate)
        .where(PackageDate.id == data.package_date_id, PackageDate.available_slots > 0)
        .values(available_slots=PackageDate.available_slots - 1)
        .execution_options(synchronize_session=False)
    )
    db.flush()
    if result.rowcount == 0:
        raise HTTPException(400, "No slots available — join the waiting list")

    db.refresh(pkg_date)
    if pkg_date.available_slots == 0:
        pkg_date.status = "full"

    discount = 0.0
    if data.is_family_booking:
        discount = _calc_family_discount(data.num_travelers, pkg)

    base_price = pkg.price * data.num_travelers
    total_price = base_price * (1 - discount / 100)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    booking = Booking(
        user_id=current_user.id,
        package_id=data.package_id,
        package_date_id=data.package_date_id,
        status="pending_payment",
        num_travelers=data.num_travelers,
        is_family_booking=data.is_family_booking,
        family_discount_pct=discount,
        base_price=base_price,
        total_price=total_price,
        expires_at=expires_at,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{booking_id}/pay", response_model=BookingOut)
def mock_pay(booking_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.status != "pending_payment":
        raise HTTPException(400, f"Cannot pay — booking is {booking.status}")
    if booking.expires_at and datetime.utcnow() > booking.expires_at:
        booking.status = "expired"
        db.commit()
        raise HTTPException(400, "Booking expired")
    booking.status = "paid"
    booking.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{booking_id}/confirm", response_model=BookingOut)
def confirm_booking(booking_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if current_user.role not in ("admin", "partner"):
        raise HTTPException(403, "Only partner or admin can confirm")
    if current_user.role == "partner":
        partner = db.query(Partner).filter(Partner.user_id == current_user.id).first()
        if not partner:
            raise HTTPException(403, "Partner profile not found")
        pkg = db.query(Package).filter(
            Package.id == booking.package_id,
            Package.partner_id == partner.id,
        ).first()
        if not pkg:
            raise HTTPException(403, "You can only confirm bookings for your own packages")
    if booking.status != "paid":
        raise HTTPException(400, "Booking must be paid first")
    booking.status = "confirmed"
    booking.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.status not in ("pending_payment", "paid", "confirmed"):
        raise HTTPException(400, f"Cannot cancel — booking is {booking.status}")

    booking.status = "cancelled_by_user"
    # Free inventory
    pkg_date = db.query(PackageDate).filter(PackageDate.id == booking.package_date_id).first()
    if pkg_date:
        pkg_date.available_slots += 1
        pkg_date.status = "available"

    db.commit()
    db.refresh(booking)
    return booking

@router.get("/me", response_model=List[BookingOut])
def my_bookings(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Booking).filter(Booking.user_id == current_user.id).order_by(Booking.created_at.desc()).all()

@router.post("/{package_date_id}/waitlist", response_model=WaitingListOut, status_code=201)
def join_waitlist(package_date_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(WaitingList).filter(
        WaitingList.user_id == current_user.id,
        WaitingList.package_date_id == package_date_id,
        WaitingList.status == "waiting",
    ).first()
    if existing:
        raise HTTPException(400, "Already on waiting list")
    # MAX(position)+1 is correct even when entries are removed (no gaps/duplicates).
    # count()+1 would break if any entry was cancelled.
    max_pos = db.query(func.max(WaitingList.position)).filter(
        WaitingList.package_date_id == package_date_id
    ).scalar() or 0
    entry = WaitingList(user_id=current_user.id, package_date_id=package_date_id, position=max_pos + 1)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
