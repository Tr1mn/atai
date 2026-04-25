from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class TripCreate(BaseModel):
    title: str
    destination: str
    description: str = ""
    start_date: datetime
    end_date: datetime
    min_size: int = 2
    max_size: int = 10
    budget_min: float = 0
    budget_max: float = 999999
    travel_style: str = "mixed"
    photo_url: str = ""

class TripMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    joined_at: datetime

class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    title: str
    destination: str
    description: str
    start_date: datetime
    end_date: datetime
    min_size: int
    max_size: int
    current_size: int
    budget_min: float
    budget_max: float
    travel_style: str
    status: str
    photo_url: str
    created_at: datetime
    members: List[TripMemberOut] = []
