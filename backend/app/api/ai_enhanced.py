"""
Enhanced AI API Routes with OpenAI Integration
Provides advanced AI capabilities with fallback to local implementations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio

from app.services.openai_service import OpenAIService
from app.ai.learning_style_analyzer import LearningStyleAnalyzer
from app.ai.content_generator import ContentGenerator
from app.ai.recommendation_engine import RecommendationEngine

router = APIRouter()

# Initialize services
openai_service = OpenAIService()
fallback_analyzer = LearningStyleAnalyzer()
fallback_generator = ContentGenerator()
fallback_recommender = RecommendationEngine()

# Request/Response Models
class LearningStyleRequest(BaseModel):
    user_responses: List[str]
    user_id: Optional[str] = None

class ContentGenerationRequest(BaseModel):
    topic: str
    learning_style: str
    difficulty_level: str
    user_preferences: Optional[List[str]] = []

class RecommendationRequest(BaseModel):
    user_id: str
    user_profile: Optional[Dict[str, Any]] = {}
    performance_data: Optional[Dict[str, Any]] = {}
    current_topic: Optional[str] = None

class QuizGenerationRequest(BaseModel):
    topic: str
    difficulty_level: str
    learning_style: str
    num_questions: Optional[int] = 5

@router.get("/ai/status")
async def get_ai_status():
    """Get the status of AI services"""
    return {
        "openai_available": openai_service.is_available(),
        "fallback_available": True,
        "model": openai_service.model if openai_service.is_available() else "local",
        "capabilities": {
            "learning_style_analysis": True,
            "content_generation": True,
            "recommendations": True,
            "quiz_generation": openai_service.is_available()
        }
    }

@router.post("/ai/analyze-learning-style-enhanced")
async def analyze_learning_style_enhanced(request: LearningStyleRequest):
    """Enhanced learning style analysis with OpenAI + fallback"""
    
    # Try OpenAI first if available
    if openai_service.is_available():
        try:
            result = await openai_service.analyze_learning_style(request.user_responses)
            result["enhanced"] = True
            return result
        except Exception as e:
            # Log the error but continue with fallback
            print(f"OpenAI analysis failed: {e}")
    
    # Fallback to original implementation
    try:
        result = fallback_analyzer.analyze_responses(request.user_responses)
        result["source"] = "fallback"
        result["enhanced"] = False
        result["note"] = "Using local AI (OpenAI unavailable)"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/ai/generate-content-enhanced")
async def generate_content_enhanced(request: ContentGenerationRequest):
    """Enhanced content generation with OpenAI + fallback"""
    
    # Try OpenAI first if available
    if openai_service.is_available():
        try:
            result = await openai_service.generate_personalized_content(
                request.topic,
                request.learning_style,
                request.difficulty_level,
                request.user_preferences
            )
            result["enhanced"] = True
            return result
        except Exception as e:
            # Log the error but continue with fallback
            print(f"OpenAI content generation failed: {e}")
    
    # Fallback to original implementation
    try:
        result = fallback_generator.generate_personalized_content(
            request.topic,
            request.learning_style,
            request.difficulty_level,
            request.user_preferences
        )
        result["source"] = "fallback"
        result["enhanced"] = False
        result["note"] = "Using local AI (OpenAI unavailable)"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/ai/recommendations-enhanced")
async def get_recommendations_enhanced(request: RecommendationRequest):
    """Enhanced recommendations with OpenAI + fallback"""
    
    # Try OpenAI first if available
    if openai_service.is_available():
        try:
            recommendations = await openai_service.get_smart_recommendations(
                request.user_profile,
                request.performance_data
            )
            return {
                "recommendations": recommendations,
                "enhanced": True,
                "source": "openai"
            }
        except Exception as e:
            # Log the error but continue with fallback
            print(f"OpenAI recommendations failed: {e}")
    
    # Fallback to original implementation
    try:
        # Create a mock user profile for the fallback
        user_profile = {
            "learning_style": request.user_profile.get("learning_style", "visual"),
            "current_level": request.performance_data.get("accuracy", 0.75),
            "knowledge_gaps": ["functions", "loops"],
            "completed_content": ["variables", "data_types"],
            "performance_history": [0.8, 0.7, 0.9]
        }
        
        recommendations = fallback_recommender.get_personalized_recommendations(
            user_profile,
            []  # available_content - empty for now
        )
        
        return {
            "recommendations": recommendations,
            "enhanced": False,
            "source": "fallback",
            "note": "Using local AI (OpenAI unavailable)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

@router.post("/ai/generate-quiz")
async def generate_quiz(request: QuizGenerationRequest):
    """Generate adaptive quiz questions (OpenAI only feature)"""
    
    if not openai_service.is_available():
        raise HTTPException(
            status_code=503, 
            detail="Quiz generation requires OpenAI integration. Please configure OPENAI_API_KEY."
        )
    
    try:
        questions = await openai_service.generate_quiz_questions(
            request.topic,
            request.difficulty_level,
            request.learning_style,
            request.num_questions
        )
        
        return {
            "questions": questions,
            "topic": request.topic,
            "difficulty_level": request.difficulty_level,
            "learning_style": request.learning_style,
            "total_questions": len(questions),
            "source": "openai"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

@router.post("/ai/batch-analysis")
async def batch_analysis(request: Dict[str, Any]):
    """Perform multiple AI operations in batch for efficiency"""
    
    results = {}
    
    # Learning style analysis
    if "user_responses" in request:
        try:
            if openai_service.is_available():
                results["learning_style"] = await openai_service.analyze_learning_style(
                    request["user_responses"]
                )
            else:
                results["learning_style"] = fallback_analyzer.analyze_responses(
                    request["user_responses"]
                )
                results["learning_style"]["source"] = "fallback"
        except Exception as e:
            results["learning_style"] = {"error": str(e)}
    
    # Content generation
    if all(key in request for key in ["topic", "learning_style", "difficulty_level"]):
        try:
            if openai_service.is_available():
                results["content"] = await openai_service.generate_personalized_content(
                    request["topic"],
                    request["learning_style"],
                    request["difficulty_level"],
                    request.get("user_preferences", [])
                )
            else:
                results["content"] = fallback_generator.generate_personalized_content(
                    request["topic"],
                    request["learning_style"],
                    request["difficulty_level"],
                    request.get("user_preferences", [])
                )
                results["content"]["source"] = "fallback"
        except Exception as e:
            results["content"] = {"error": str(e)}
    
    # Recommendations
    if "user_profile" in request or "performance_data" in request:
        try:
            if openai_service.is_available():
                results["recommendations"] = await openai_service.get_smart_recommendations(
                    request.get("user_profile", {}),
                    request.get("performance_data", {})
                )
            else:
                # Fallback recommendations
                user_profile = {
                    "learning_style": request.get("user_profile", {}).get("learning_style", "visual"),
                    "current_level": request.get("performance_data", {}).get("accuracy", 0.75),
                    "knowledge_gaps": ["functions", "loops"],
                    "completed_content": ["variables", "data_types"],
                    "performance_history": [0.8, 0.7, 0.9]
                }
                results["recommendations"] = fallback_recommender.get_personalized_recommendations(
                    user_profile, []
                )
                for rec in results["recommendations"]:
                    rec["source"] = "fallback"
        except Exception as e:
            results["recommendations"] = {"error": str(e)}
    
    return {
        "results": results,
        "openai_available": openai_service.is_available(),
        "timestamp": "2025-07-07T10:16:00Z"
    }

@router.get("/ai/capabilities")
async def get_ai_capabilities():
    """Get detailed information about AI capabilities"""
    
    capabilities = {
        "learning_style_analysis": {
            "available": True,
            "enhanced": openai_service.is_available(),
            "features": [
                "Visual, auditory, kinesthetic, reading/writing classification",
                "Confidence scoring",
                "Personalized adaptations",
                "Neurodivergent considerations" if openai_service.is_available() else "Basic adaptations"
            ]
        },
        "content_generation": {
            "available": True,
            "enhanced": openai_service.is_available(),
            "features": [
                "Topic-specific content",
                "Learning style adaptation",
                "Difficulty level adjustment",
                "Interactive exercises",
                "Assessment questions" if openai_service.is_available() else "Basic exercises"
            ]
        },
        "recommendations": {
            "available": True,
            "enhanced": openai_service.is_available(),
            "features": [
                "Personalized learning paths",
                "Performance-based suggestions",
                "Confidence scoring",
                "Time estimates" if openai_service.is_available() else "Basic recommendations"
            ]
        },
        "quiz_generation": {
            "available": openai_service.is_available(),
            "enhanced": openai_service.is_available(),
            "features": [
                "Adaptive question generation",
                "Multiple question types",
                "Learning style specific questions",
                "Detailed explanations"
            ] if openai_service.is_available() else []
        }
    }
    
    return {
        "capabilities": capabilities,
        "openai_status": {
            "available": openai_service.is_available(),
            "model": openai_service.model if openai_service.is_available() else None
        },
        "fallback_status": {
            "available": True,
            "description": "Local AI implementations always available"
        }
    }