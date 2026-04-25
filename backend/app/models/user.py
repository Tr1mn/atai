from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    age = Column(Integer)
    city = Column(String)
    bio = Column(Text, default="")
    photo_url = Column(String, default="")
    role = Column(String, default="tourist")  # tourist | partner | admin
    status = Column(String, default="active")  # active | verified | hidden | warned | restricted | blocked | deleted
    interests = Column(Text, default="")       # comma-separated
    travel_style = Column(String, default="")  # adventure | relax | culture | mixed
    budget_min = Column(Float, default=0)
    budget_max = Column(Float, default=999999)
    languages = Column(Text, default="ru")     # comma-separated
    complaint_count = Column(Integer, default=0)
    phone = Column(String, nullable=True)
    telegram = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    instagram = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")
    trips_organized = relationship("Trip", back_populates="organizer")
    trip_memberships = relationship("TripMember", back_populates="user")
    likes_given = relationship("Like", foreign_keys="Like.from_user_id", back_populates="from_user")
    likes_received = relationship("Like", foreign_keys="Like.to_user_id", back_populates="to_user")
    skips_given = relationship("UserSkip", foreign_keys="UserSkip.from_user_id", back_populates="from_user")
    skips_received = relationship("UserSkip", foreign_keys="UserSkip.to_user_id", back_populates="to_user")
    reviews = relationship("Review", back_populates="user")
    complaints_filed = relationship("Complaint", foreign_keys="Complaint.reporter_id", back_populates="reporter")
    partner = relationship("Partner", back_populates="user", uselist=False)
    travel_requests = relationship("TravelRequest", back_populates="user", cascade="all, delete-orphan")
