from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, Text
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from app.database.database import Base

class LearningContent(Base):
    __tablename__ = "learning_content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    subject = Column(String, index=True)
    topic = Column(String, index=True)
    content_type = Column(String)  # text, video, audio, interactive, quiz
    difficulty_level = Column(Float)  # 0.0 to 1.0
    estimated_duration = Column(Integer)  # minutes
    content_data = Column(JSON)  # Actual content structure
    learning_objectives = Column(JSON)  # What should be learned
    prerequisites = Column(JSON)  # Required prior knowledge
    tags = Column(JSON)  # Searchable tags
    accessibility_features = Column(JSON)  # Features for neurodivergent learners
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    subject = Column(String)
    topic = Column(String)
    difficulty_level = Column(Float)
    questions = Column(JSON)  # List of questions with answers
    adaptive_parameters = Column(JSON)  # Parameters for adaptive questioning
    time_limit = Column(Integer)  # seconds, optional
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class AdaptiveRecommendation(Base):
    __tablename__ = "adaptive_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content_id = Column(Integer)
    recommendation_type = Column(String)  # next_topic, review, practice, challenge
    confidence_score = Column(Float)  # AI confidence in recommendation
    reasoning = Column(JSON)  # Why this was recommended
    personalization_factors = Column(JSON)  # What factors influenced this
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_used = Column(Boolean, default=False)
    user_rating = Column(Float)  # User feedback on recommendation

# Pydantic models
class LearningContentCreate(BaseModel):
    title: str
    subject: str
    topic: str
    content_type: str
    difficulty_level: float
    estimated_duration: int
    content_data: Dict
    learning_objectives: List[str]
    prerequisites: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    accessibility_features: Optional[Dict] = None

class LearningContentResponse(BaseModel):
    id: int
    title: str
    subject: str
    topic: str
    content_type: str
    difficulty_level: float
    estimated_duration: int
    content_data: Dict
    learning_objectives: List[str]
    prerequisites: Optional[List[str]]
    tags: Optional[List[str]]
    accessibility_features: Optional[Dict]
    created_at: datetime
    is_active: bool

class QuizCreate(BaseModel):
    title: str
    subject: str
    topic: str
    difficulty_level: float
    questions: List[Dict]
    adaptive_parameters: Optional[Dict] = None
    time_limit: Optional[int] = None

class QuizResponse(BaseModel):
    id: int
    title: str
    subject: str
    topic: str
    difficulty_level: float
    questions: List[Dict]
    time_limit: Optional[int]
    created_at: datetime

class RecommendationRequest(BaseModel):
    user_id: int
    current_topic: Optional[str] = None
    session_performance: Optional[float] = None
    time_available: Optional[int] = None  # minutes
    learning_goal: Optional[str] = None

class RecommendationResponse(BaseModel):
    content_id: int
    recommendation_type: str
    confidence_score: float
    reasoning: Dict
    estimated_benefit: float
    content_preview: Dict