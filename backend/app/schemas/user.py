from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    interests: Optional[str] = None
    travel_style: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    languages: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None

class UserPublic(BaseModel):
    """Public user profile — no contacts, no email."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    age: Optional[int] = None
    city: Optional[str] = None
    bio: str
    photo_url: str
    interests: str
    travel_style: str
    budget_min: float
    budget_max: float
    languages: str
    status: str
    role: str
    created_at: datetime

class UserMe(UserPublic):
    """Own profile — includes email and contacts."""
    email: str
    phone: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None

class MatchedUserOut(BaseModel):
    """User shown inside a Match — contacts included (mutual match only)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    photo_url: str
    city: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None

class MatchOut(BaseModel):
    match_id: int
    user: MatchedUserOut
    created_at: str

class IncomingLikeOut(BaseModel):
    """Incoming like entry — user data has NO contacts until mutual match."""
    like_id: int
    liked_at: datetime
    user: UserPublic
