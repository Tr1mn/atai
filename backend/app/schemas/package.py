from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class PackageDateCreate(BaseModel):
    start_date: datetime
    total_slots: int

class PackageCreate(BaseModel):
    title: str
    description: str = ""
    destination: str
    region: str = ""
    price: float
    duration_days: int
    min_group_size: int = 1
    max_group_size: int = 20
    inclusions: str = "[]"
    exclusions: str = "[]"
    cancellation_policy: str = ""
    itinerary: str = "[]"
    photo_url: str = ""
    difficulty: str = "easy"
    travel_style: str = "mixed"
    family_friendly: bool = True
    family_rates_enabled: bool = False
    dates: List[PackageDateCreate] = []

class PackageUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    photo_url: Optional[str] = None
    featured: Optional[bool] = None

class PackageDateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    start_date: datetime
    total_slots: int
    available_slots: int
    status: str

class PackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    partner_id: Optional[int]
    title: str
    description: str
    destination: str
    region: str
    price: float
    duration_days: int
    min_group_size: int
    max_group_size: int
    inclusions: str
    exclusions: str
    cancellation_policy: str
    itinerary: str
    photo_url: str
    difficulty: str
    travel_style: str
    family_friendly: bool
    family_rates_enabled: bool
    status: str
    featured: bool
    created_at: datetime
    dates: List[PackageDateOut] = []
