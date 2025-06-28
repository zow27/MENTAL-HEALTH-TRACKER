# models.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email    = Column(String, unique=True, index=True)
    password = Column(String)  # hashed!

    moods    = relationship("MoodEntry", back_populates="user")
    journals = relationship("JournalEntry", back_populates="user")

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    score     = Column(Float)        # e.g., 1–10
    category  = Column(String)       # e.g., “anxious”, “happy”

    user      = relationship("User", back_populates="moods")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    content   = Column(Text)

    user      = relationship("User", back_populates="journals")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    timestamp  = Column(DateTime, default=datetime.utcnow)
    strategy   = Column(String)      # e.g., “take a walk”, “deep breathing”
    success    = Column(Integer)     # e.g., 0 = didn’t help, 1 = helped

    user       = relationship("User")
