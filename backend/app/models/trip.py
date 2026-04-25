from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    description = Column(Text, default="")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    min_size = Column(Integer, default=2)
    max_size = Column(Integer, default=10)
    current_size = Column(Integer, default=1)
    budget_min = Column(Float, default=0)
    budget_max = Column(Float, default=999999)
    travel_style = Column(String, default="mixed")
    status = Column(String, default="open")
    # open | group_formed | active | completed | cancelled | emergency
    photo_url = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    organizer = relationship("User", back_populates="trips_organized")
    members = relationship("TripMember", back_populates="trip", cascade="all, delete-orphan")

class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")  # pending | accepted | rejected
    joined_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")
