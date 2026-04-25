from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"))
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    destination = Column(String, nullable=False)
    region = Column(String, default="")
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    min_group_size = Column(Integer, default=1)
    max_group_size = Column(Integer, default=20)
    inclusions = Column(Text, default="")   # JSON string: ["Accommodation","Meals"]
    exclusions = Column(Text, default="")   # JSON string
    cancellation_policy = Column(Text, default="")
    itinerary = Column(Text, default="")    # JSON string: [{"day":1,"title":"...","description":"..."}]
    photo_url = Column(String, default="")
    difficulty = Column(String, default="easy")   # easy | moderate | hard
    travel_style = Column(String, default="mixed") # adventure | relax | culture | mixed
    family_friendly = Column(Boolean, default=True)
    family_rates_enabled = Column(Boolean, default=False)
    status = Column(String, default="draft")  # draft | under_moderation | published | archived | suspended
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    partner = relationship("Partner", back_populates="packages")
    dates = relationship("PackageDate", back_populates="package", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="package")
    reviews = relationship("Review", back_populates="package")

class PackageDate(Base):
    __tablename__ = "package_dates"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"))
    start_date = Column(DateTime, nullable=False)
    total_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    status = Column(String, default="available")  # available | full | past

    package = relationship("Package", back_populates="dates")
    bookings = relationship("Booking", back_populates="package_date")
    waiting_list = relationship("WaitingList", back_populates="package_date")
