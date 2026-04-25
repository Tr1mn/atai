from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String, nullable=False)
    legal_info = Column(Text, default="")
    partner_type = Column(String, default="agency")  # agency | hotel | transport
    status = Column(String, default="pending")  # pending | active | suspended | terminated
    commission_rate = Column(Float, default=12.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="partner")
    packages = relationship("Package", back_populates="partner")
    travel_offers = relationship("TravelOffer", back_populates="partner", cascade="all, delete-orphan")
