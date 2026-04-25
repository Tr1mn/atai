from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    package_id = Column(Integer, ForeignKey("packages.id"))
    package_date_id = Column(Integer, ForeignKey("package_dates.id"))
    status = Column(String, default="pending_payment")
    # pending_payment | paid | pending_confirmation | confirmed
    # cancelled_by_user | cancelled_by_partner | completed | expired | disputed | resolved
    num_travelers = Column(Integer, default=1)
    is_family_booking = Column(Boolean, default=False)
    family_discount_pct = Column(Float, default=0.0)
    base_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    paid_at = Column(DateTime)
    confirmed_at = Column(DateTime)
    cancellation_reason = Column(String, default="")

    user = relationship("User", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")
    package_date = relationship("PackageDate", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)

class WaitingList(Base):
    __tablename__ = "waiting_list"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    package_date_id = Column(Integer, ForeignKey("package_dates.id"))
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    offer_expires_at = Column(DateTime)
    status = Column(String, default="waiting")  # waiting | offered | accepted | expired

    package_date = relationship("PackageDate", back_populates="waiting_list")
