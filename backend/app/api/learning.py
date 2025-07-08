from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import json
from datetime import datetime

from app.database.database import get_db
from app.models.user import User, LearningSessionCreate
from app.models.content import RecommendationRequest, RecommendationResponse
from app.api.auth import get_current_user
from app.services.learning_service import LearningService

router = APIRouter(prefix="/learning", tags=["learning"])
learning_service = LearningService()

# WebSocket connection manager for real-time adaptations
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.get("/style-analysis/{user_id}")
async def analyze_learning_style(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze user's learning style based on session history."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        learning_profile = learning_service.analyze_user_learning_style(db, user_id)
        return {
            "user_id": user_id,
            "learning_profile": learning_profile,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/generate-content")
async def generate_personalized_content(
    topic: str,
    content_type: str = "auto",
    difficulty: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized learning content for the user."""
    try:
        content = learning_service.generate_personalized_content(
            db=db,
            user_id=current_user.id,
            topic=topic,
            content_type=content_type,
            difficulty=difficulty
        )
        return content
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized content recommendations."""
    context = {
        "current_topic": request.current_topic,
        "session_performance": request.session_performance,
        "time_available": request.time_available,
        "learning_goal": request.learning_goal
    }
    
    try:
        recommendations = learning_service.get_personalized_recommendations(
            db=db,
            user_id=request.user_id if request.user_id else current_user.id,
            context=context,
            num_recommendations=5
        )
        
        # Convert to response format
        response_recommendations = []
        for rec in recommendations:
            response_rec = RecommendationResponse(
                content_id=rec['content_id'],
                recommendation_type='personalized',
                confidence_score=rec['confidence'],
                reasoning=rec['reasoning'],
                estimated_benefit=rec['estimated_benefit'],
                content_preview={
                    'title': rec['content']['title'],
                    'type': rec['content'].get('content_type', 'unknown'),
                    'difficulty': rec['content'].get('difficulty_level', 0.5),
                    'duration': rec['content'].get('estimated_duration', 30)
                }
            )
            response_recommendations.append(response_rec)
        
        return response_recommendations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/record")
async def record_learning_session(
    session_data: LearningSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a completed learning session."""
    session_dict = {
        "content_type": session_data.session_type,
        "content_id": session_data.content_id,
        "duration": session_data.duration,
        "performance_score": session_data.performance_score,
        "engagement_score": session_data.engagement_score,
        "difficulty_level": session_data.difficulty_level,
        "adaptations_made": session_data.adaptations_made or {},
        "ai_feedback": session_data.feedback_given or {},
        "user_feedback": session_data.user_feedback or {}
    }
    
    try:
        session_id = learning_service.record_learning_session(
            db=db,
            user_id=current_user.id,
            session_data=session_dict
        )
        return {
            "session_id": session_id,
            "message": "Session recorded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording session: {str(e)}")

@router.get("/analytics")
async def get_learning_analytics(
    time_range: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive learning analytics for the user."""
    try:
        analytics = learning_service.get_learning_analytics(
            db=db,
            user_id=current_user.id,
            time_range=time_range
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@router.post("/adapt-realtime")
async def adapt_content_realtime(
    session_id: str,
    performance_data: Dict,
    user_feedback: Optional[Dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adapt content in real-time based on user performance."""
    try:
        adaptation_result = learning_service.adapt_content_realtime(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            current_performance=performance_data,
            user_feedback=user_feedback
        )
        
        # Send real-time update via WebSocket if connected
        if current_user.id in manager.user_connections:
            await manager.send_personal_message(
                json.dumps({
                    "type": "adaptation",
                    "data": adaptation_result,
                    "timestamp": datetime.now().isoformat()
                }),
                current_user.id
            )
        
        return adaptation_result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adapting content: {str(e)}")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time learning adaptations."""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "performance_update":
                # Handle real-time performance updates
                performance_data = message_data.get("data", {})
                session_id = message_data.get("session_id")
                
                if session_id:
                    try:
                        # Get real-time adaptation
                        adaptation_result = learning_service.adapt_content_realtime(
                            db=db,
                            user_id=user_id,
                            session_id=session_id,
                            current_performance=performance_data
                        )
                        
                        # Send adaptation back to client
                        await websocket.send_text(json.dumps({
                            "type": "adaptation_response",
                            "data": adaptation_result,
                            "timestamp": datetime.now().isoformat()
                        }))
                    except Exception as e:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Adaptation error: {str(e)}",
                            "timestamp": datetime.now().isoformat()
                        }))
            
            elif message_data.get("type") == "heartbeat":
                # Respond to heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat_response",
                    "timestamp": datetime.now().isoformat()
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

@router.get("/progress/{topic}")
async def get_topic_progress(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress in a specific topic."""
    from app.models.user import LearningProgress
    
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.topic == topic
    ).first()
    
    if not progress:
        return {
            "topic": topic,
            "skill_level": 0.0,
            "completion_rate": 0.0,
            "time_spent": 0,
            "knowledge_gaps": [],
            "strengths": [],
            "last_accessed": None
        }
    
    return {
        "topic": progress.topic,
        "skill_level": progress.skill_level,
        "completion_rate": progress.completion_rate,
        "time_spent": progress.time_spent,
        "knowledge_gaps": progress.knowledge_gaps or [],
        "strengths": progress.strengths or [],
        "last_accessed": progress.last_accessed.isoformat() if progress.last_accessed else None
    }

@router.get("/learning-path")
async def get_learning_path(
    learning_goals: str,  # Comma-separated list
    time_available: int = 60,  # minutes
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning path recommendations."""
    goals_list = [goal.strip() for goal in learning_goals.split(",")]
    
    # Get user profile
    user_profile = learning_service._build_user_profile(db, current_user.id)
    
    # Get current progress
    from app.models.user import LearningProgress
    progress_records = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    current_progress = {}
    for progress in progress_records:
        current_progress[progress.topic] = {
            'skill_level': progress.skill_level,
            'completion_rate': progress.completion_rate,
            'knowledge_gaps': progress.knowledge_gaps or [],
            'strengths': progress.strengths or []
        }
    
    try:
        learning_path = learning_service.recommendation_engine.get_next_learning_path(
            user_id=current_user.id,
            user_profile=user_profile,
            current_progress=current_progress,
            learning_goals=goals_list,
            time_available=time_available
        )
        
        return learning_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")

@router.get("/review-recommendations")
async def get_review_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommendations for content that needs review."""
    from app.models.user import LearningProgress
    from datetime import datetime, timedelta
    
    # Get user's progress records
    progress_records = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    # Calculate time since last review for each topic
    time_since_last_review = {}
    for progress in progress_records:
        if progress.last_accessed:
            days_since = (datetime.now() - progress.last_accessed).days
            time_since_last_review[progress.topic] = days_since
    
    if not time_since_last_review:
        return {"review_recommendations": [], "message": "No content available for review"}
    
    # Get user's performance history
    from app.models.user import LearningSession
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id
    ).order_by(LearningSession.created_at.desc()).limit(50).all()
    
    performance_history = []
    for session in sessions:
        performance_history.append({
            'topic': session.content_id,  # Simplified - would map to actual topic
            'score': session.performance_score,
            'date': session.created_at.isoformat()
        })
    
    # Get user profile
    user_profile = learning_service._build_user_profile(db, current_user.id)
    
    try:
        review_recommendations = learning_service.recommendation_engine.recommend_review_content(
            user_id=current_user.id,
            user_profile=user_profile,
            performance_history=performance_history,
            time_since_last_review=time_since_last_review
        )
        
        return {"review_recommendations": review_recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating review recommendations: {str(e)}")