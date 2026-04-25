from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.package import Package, PackageDate
from ..models.partner import Partner
from ..schemas.package import PackageCreate, PackageUpdate, PackageOut
from ..core.security import get_current_user, require_partner

router = APIRouter(prefix="/api/packages", tags=["packages"])

@router.get("/", response_model=List[PackageOut])
def list_packages(
    destination: Optional[str] = None,
    travel_style: Optional[str] = None,
    difficulty: Optional[str] = None,
    family_friendly: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    max_duration: Optional[int] = None,
    featured_only: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Package).filter(Package.status == "published")
    if destination:
        q = q.filter(Package.destination.ilike(f"%{destination}%"))
    if travel_style:
        q = q.filter(Package.travel_style == travel_style)
    if difficulty:
        q = q.filter(Package.difficulty == difficulty)
    if family_friendly is not None:
        q = q.filter(Package.family_friendly == family_friendly)
    if min_price is not None:
        q = q.filter(Package.price >= min_price)
    if max_price is not None:
        q = q.filter(Package.price <= max_price)
    if max_duration is not None:
        q = q.filter(Package.duration_days <= max_duration)
    if featured_only:
        q = q.filter(Package.featured == True)
    return q.order_by(Package.featured.desc(), Package.created_at.desc()).all()

@router.get("/{package_id}", response_model=PackageOut)
def get_package(package_id: int, db: Session = Depends(get_db)):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    return pkg

@router.post("/", response_model=PackageOut, status_code=201)
def create_package(data: PackageCreate, db: Session = Depends(get_db), current_user=Depends(require_partner)):
    partner = db.query(Partner).filter(Partner.user_id == current_user.id).first()
    if not partner or partner.status != "active":
        raise HTTPException(403, "Partner account not active")
    if not data.cancellation_policy:
        raise HTTPException(400, "cancellation_policy is required")

    pkg = Package(
        partner_id=partner.id,
        title=data.title,
        description=data.description,
        destination=data.destination,
        region=data.region,
        price=data.price,
        duration_days=data.duration_days,
        min_group_size=data.min_group_size,
        max_group_size=data.max_group_size,
        inclusions=data.inclusions,
        exclusions=data.exclusions,
        cancellation_policy=data.cancellation_policy,
        itinerary=data.itinerary,
        photo_url=data.photo_url,
        difficulty=data.difficulty,
        travel_style=data.travel_style,
        family_friendly=data.family_friendly,
        family_rates_enabled=data.family_rates_enabled,
        status="under_moderation",
    )
    db.add(pkg)
    db.flush()

    for d in data.dates:
        pd = PackageDate(package_id=pkg.id, start_date=d.start_date, total_slots=d.total_slots, available_slots=d.total_slots)
        db.add(pd)

    db.commit()
    db.refresh(pkg)
    return pkg

@router.put("/{package_id}", response_model=PackageOut)
def update_package(package_id: int, data: PackageUpdate, db: Session = Depends(get_db), current_user=Depends(require_partner)):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    partner = db.query(Partner).filter(Partner.user_id == current_user.id).first()
    if current_user.role != "admin" and (not partner or pkg.partner_id != partner.id):
        raise HTTPException(403, "Not your package")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(pkg, field, value)
    db.commit()
    db.refresh(pkg)
    return pkg
