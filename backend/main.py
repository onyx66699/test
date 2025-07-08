from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from app.database.database import create_tables
from app.api import auth, learning, ai_enhanced

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="Adaptive Learning & Skill Development API",
    description="AI-powered adaptive learning platform with personalized content generation and real-time adaptations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(learning.router)
app.include_router(ai_enhanced.router)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Adaptive Learning & Skill Development API",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Learning Style Analysis",
            "Personalized Content Generation",
            "Real-time Adaptations",
            "AI-powered Recommendations",
            "Progress Tracking",
            "Neurodivergent Support"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-07-07T10:16:00Z"}

# AI Endpoints
@app.post("/ai/analyze-learning-style")
async def analyze_learning_style(request: dict):
    """Analyze user learning style from responses"""
    try:
        from app.ai.learning_style_analyzer import LearningStyleAnalyzer
        analyzer = LearningStyleAnalyzer()
        
        # Create mock session data from user responses
        user_responses = request.get('user_responses', [])
        
        # Analyze responses to determine content preferences
        content_type = 'text'  # default
        if any('visual' in resp.lower() or 'diagram' in resp.lower() for resp in user_responses):
            content_type = 'diagram'
        elif any('audio' in resp.lower() or 'listen' in resp.lower() for resp in user_responses):
            content_type = 'audio'
        elif any('hands-on' in resp.lower() or 'practice' in resp.lower() for resp in user_responses):
            content_type = 'interactive'
        
        session_data = {
            'time_spent': 1800,
            'content_type': content_type,
            'interactions': {
                'note_taking': any('notes' in resp.lower() for resp in user_responses),
                'audio_playback': 1 if content_type == 'audio' else 0,
                'interactive_elements': 5 if content_type == 'interactive' else 2
            },
            'engagement_score': 0.8,
            'completion_rate': 0.9,
            'help_requests': 2
        }
        
        result = analyzer.analyze_session_behavior(session_data)
        
        # Determine primary style from scores
        style_scores = {
            'visual': result.get('visual_score', 0.3),
            'auditory': result.get('auditory_score', 0.3),
            'kinesthetic': result.get('kinesthetic_score', 0.3)
        }
        
        primary_style = max(style_scores, key=style_scores.get)
        confidence = max(style_scores.values())
        
        return {
            "primary_style": primary_style,
            "confidence": confidence,
            "adaptations": [
                f"Use {primary_style} learning materials",
                "Provide interactive examples",
                "Include progress tracking"
            ],
            "scores": style_scores
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.post("/ai/generate-content")
async def generate_content(request: dict):
    """Generate personalized learning content"""
    try:
        from app.ai.content_generator import ContentGenerator
        generator = ContentGenerator()
        
        topic = request.get('topic', 'Python Basics')
        learning_style = request.get('learning_style', 'visual')
        difficulty = request.get('difficulty_level', 'beginner')
        
        # Convert difficulty to float
        difficulty_map = {'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.9}
        difficulty_float = difficulty_map.get(difficulty, 0.3)
        
        content = generator.generate_personalized_content(
            topic=topic,
            learning_objectives=[f"Understand {topic}", f"Apply {topic} concepts"],
            learning_style=learning_style,
            difficulty=difficulty_float,
            user_background={"experience_level": difficulty}
        )
        
        return {
            "content_type": content.get('content_type', 'lesson'),
            "difficulty_level": difficulty,
            "content": content.get('main_content', f"Personalized {topic} content for {learning_style} learners"),
            "exercises": content.get('exercises', []),
            "adaptations": content.get('style_adaptations', [])
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.post("/ai/recommendations")
async def get_recommendations(request: dict):
    """Get AI-powered learning recommendations"""
    try:
        from app.ai.recommendation_engine import RecommendationEngine
        engine = RecommendationEngine()
        
        user_id = request.get('user_id', 'demo_user')
        current_topic = request.get('current_topic', 'Python Basics')
        performance = request.get('performance_data', {})
        
        # Create user profile
        user_profile = {
            'learning_style': 'visual',
            'current_level': performance.get('accuracy', 0.7),
            'knowledge_gaps': ['functions', 'loops'],
            'completed_content': ['variables', 'data_types'],
            'performance_history': [0.8, 0.7, 0.9]
        }
        
        # Available content
        available_content = [
            {'id': 1, 'title': 'Python Functions', 'difficulty': 0.4, 'topics': ['functions']},
            {'id': 2, 'title': 'For Loops', 'difficulty': 0.3, 'topics': ['loops']},
            {'id': 3, 'title': 'Object-Oriented Programming', 'difficulty': 0.6, 'topics': ['classes']},
            {'id': 4, 'title': 'Error Handling', 'difficulty': 0.5, 'topics': ['exceptions']},
        ]
        
        recommendations = engine.get_personalized_recommendations(
            user_id=1,  # Mock user ID
            user_profile=user_profile,
            available_content=available_content,
            num_recommendations=3
        )
        
        # Format recommendations
        formatted_recs = []
        for rec in recommendations[:3]:
            formatted_recs.append({
                "title": rec.get('title', 'Recommended Content'),
                "confidence": rec.get('score', 0.8),
                "reason": rec.get('reasoning', {}).get('explanation', 'Matches your learning style and fills knowledge gaps'),
                "difficulty": rec.get('difficulty', 0.5),
                "topics": rec.get('topics', [])
            })
        
        return {
            "recommendations": formatted_recs,
            "user_profile": user_profile
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 12000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )