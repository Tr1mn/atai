from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class UserSkip(Base):
    __tablename__ = "user_skips"
    __table_args__ = (UniqueConstraint("from_user_id", "to_user_id", name="uq_skip_from_to"),)

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="skips_given")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="skips_received")

class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("from_user_id", "to_user_id", name="uq_like_from_to"),)

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="likes_given")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="likes_received")

class Match(Base):
    __tablename__ = "matches"
    # user1_id is always min(user_a, user_b) so (user1_id, user2_id) is unique per pair
    __table_args__ = (UniqueConstraint("user1_id", "user2_id", name="uq_match_users"),)

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"))
    user2_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="match")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="messages")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    package_id = Column(Integer, ForeignKey("packages.id"))
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True)
    rating = Column(Float, nullable=False)
    text = Column(Text, default="")
    status = Column(String, default="pending")  # pending | published
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    package = relationship("Package", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default="pending")  # pending | reviewed | dismissed | action_taken
    created_at = Column(DateTime, default=datetime.utcnow)

    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="complaints_filed")
