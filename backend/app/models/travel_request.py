from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class TravelRequest(Base):
    __tablename__ = "travel_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    origin = Column(String, nullable=False)
    days = Column(String, nullable=False)
    companions = Column(String, nullable=False)
    interests = Column(Text, default="[]")
    travel_format = Column(String, nullable=False)
    mood = Column(String, default="")
    difficulty = Column(String, nullable=False)
    budget = Column(String, nullable=False)
    season = Column(String, nullable=False)
    accommodation = Column(String, default="")
    transport = Column(String, default="")
    activities = Column(Text, default="[]")
    preferred_places = Column(Text, default="[]")
    distance = Column(String, default="")
    priority = Column(String, nullable=False)
    notes = Column(Text, default="")
    status = Column(String, default="open")  # open | matched | closed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="travel_requests")
    offers = relationship("TravelOffer", back_populates="request", cascade="all, delete-orphan")


class TravelOffer(Base):
    __tablename__ = "travel_offers"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("travel_requests.id"), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    price_total = Column(Float, nullable=False)
    price_per_person = Column(Float, nullable=True)
    duration_days = Column(Integer, nullable=True)
    included = Column(Text, default="")
    message = Column(Text, default="")
    status = Column(String, default="submitted")  # submitted | accepted | declined
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("TravelRequest", back_populates="offers")
    partner = relationship("Partner", back_populates="travel_offers")
