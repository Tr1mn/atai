from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


class TravelRequestCreate(BaseModel):
    origin: str = Field(min_length=2, max_length=80)
    days: str
    companions: str
    interests: List[str] = Field(default_factory=list)
    travel_format: str
    mood: str = ""
    difficulty: str
    budget: str
    season: str
    accommodation: str = ""
    transport: str = ""
    activities: List[str] = Field(default_factory=list)
    preferred_places: List[str] = Field(default_factory=list)
    distance: str = ""
    priority: str
    notes: str = ""


class TravelOfferCreate(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    description: str = ""
    price_total: float = Field(gt=0)
    price_per_person: Optional[float] = Field(default=None, gt=0)
    duration_days: Optional[int] = Field(default=None, ge=1)
    included: str = ""
    message: str = ""


class TravelOfferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    partner_id: int
    partner_company: str
    title: str
    description: str
    price_total: float
    price_per_person: Optional[float]
    duration_days: Optional[int]
    included: str
    message: str
    status: str
    created_at: datetime


class TravelRequestOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    origin: str
    days: str
    companions: str
    interests: List[str]
    travel_format: str
    mood: str
    difficulty: str
    budget: str
    season: str
    accommodation: str
    transport: str
    activities: List[str]
    preferred_places: List[str]
    distance: str
    priority: str
    notes: str
    status: str
    created_at: datetime
    offers: List[TravelOfferOut] = Field(default_factory=list)
