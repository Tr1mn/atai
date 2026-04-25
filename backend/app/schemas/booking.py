from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BookingCreate(BaseModel):
    package_id: int
    package_date_id: int
    num_travelers: int = 1
    is_family_booking: bool = False

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    package_id: int
    package_date_id: int
    status: str
    num_travelers: int
    is_family_booking: bool
    family_discount_pct: float
    base_price: float
    total_price: float
    created_at: datetime
    expires_at: Optional[datetime]
    paid_at: Optional[datetime]
    confirmed_at: Optional[datetime]

class WaitingListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    package_date_id: int
    position: int
    status: str
    created_at: datetime
