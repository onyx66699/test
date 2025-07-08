from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    learning_style = Column(JSON)  # Visual, Auditory, Kinesthetic preferences
    neurodivergent_accommodations = Column(JSON)  # Specific accommodations needed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    subject = Column(String)
    topic = Column(String)
    skill_level = Column(Float)  # 0.0 to 1.0
    completion_rate = Column(Float)  # 0.0 to 1.0
    time_spent = Column(Integer)  # minutes
    last_accessed = Column(DateTime(timezone=True))
    knowledge_gaps = Column(JSON)  # Identified gaps
    strengths = Column(JSON)  # Identified strengths
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_type = Column(String)  # quiz, exercise, reading, video
    content_id = Column(String)
    duration = Column(Integer)  # seconds
    performance_score = Column(Float)  # 0.0 to 1.0
    engagement_score = Column(Float)  # 0.0 to 1.0
    difficulty_level = Column(Float)  # 0.0 to 1.0
    adaptations_made = Column(JSON)  # What adaptations were applied
    feedback_given = Column(JSON)  # AI feedback provided
    user_feedback = Column(JSON)  # User's feedback on the session
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic models for API
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    learning_style: Optional[Dict] = None
    neurodivergent_accommodations: Optional[Dict] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    learning_style: Optional[Dict]
    neurodivergent_accommodations: Optional[Dict]
    created_at: datetime
    is_active: bool

class LearningProgressCreate(BaseModel):
    subject: str
    topic: str
    skill_level: float
    completion_rate: float
    time_spent: int
    knowledge_gaps: Optional[List[str]] = None
    strengths: Optional[List[str]] = None

class LearningSessionCreate(BaseModel):
    session_type: str
    content_id: str
    duration: int
    performance_score: float
    engagement_score: float
    difficulty_level: float
    adaptations_made: Optional[Dict] = None
    feedback_given: Optional[Dict] = None
    user_feedback: Optional[Dict] = None