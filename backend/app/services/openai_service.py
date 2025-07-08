"""
OpenAI Service for Enhanced AI Capabilities
Provides advanced learning style analysis, content generation, and recommendations
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

class OpenAIService:
    """Enhanced AI service using OpenAI GPT models with fallback support"""
    
    def __init__(self):
        self.openai_available = OPENAI_AVAILABLE and bool(os.getenv("OPENAI_API_KEY"))
        
        if self.openai_available:
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
            self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        else:
            self.client = None
            self.model = None
            self.max_tokens = 1000
            self.temperature = 0.7
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.openai_available
    
    async def analyze_learning_style(self, user_responses: List[str]) -> Dict[str, Any]:
        """Enhanced learning style analysis using OpenAI"""
        
        if not self.openai_available:
            raise Exception("OpenAI not available")
        
        prompt = f"""
        Analyze the following user responses to determine their learning style preferences.
        Classify them as: visual, auditory, kinesthetic, or reading/writing.
        
        User responses:
        {chr(10).join(f"- {response}" for response in user_responses)}
        
        Provide a JSON response with:
        - primary_style: the main learning style (visual/auditory/kinesthetic/reading_writing)
        - secondary_style: secondary preference (if any)
        - confidence: confidence score (0-1)
        - adaptations: list of specific recommendations
        - neurodivergent_considerations: any special considerations for neurodivergent learners
        - scores: breakdown of scores for each learning style
        
        Format as valid JSON only, no additional text.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an educational psychologist specializing in learning styles and neurodivergent learners. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            result["source"] = "openai"
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI analysis failed: {str(e)}")
    
    async def generate_personalized_content(self, topic: str, learning_style: str, 
                                          difficulty_level: str, user_preferences: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate educational content using OpenAI"""
        
        if not self.openai_available:
            raise Exception("OpenAI not available")
        
        preferences_text = ', '.join(user_preferences) if user_preferences else "None specified"
        
        prompt = f"""
        Create personalized learning content for:
        - Topic: {topic}
        - Learning Style: {learning_style}
        - Difficulty Level: {difficulty_level}
        - User Preferences: {preferences_text}
        
        Generate comprehensive learning content with:
        1. A clear explanation adapted to the learning style
        2. 3 practical exercises with step-by-step instructions
        3. Visual/interactive elements suggestions
        4. Assessment questions (3-5 questions)
        5. Neurodivergent-friendly adaptations
        6. Additional resources or next steps
        
        Return as JSON with fields: 
        - content: main learning content
        - exercises: array of exercise objects with title and instructions
        - visual_elements: suggestions for visual aids
        - assessment: array of assessment questions
        - adaptations: neurodivergent-friendly modifications
        - resources: additional learning resources
        
        Format as valid JSON only, no additional text.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an adaptive learning content creator specializing in personalized education. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens * 2,  # More tokens for content generation
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            result["content_type"] = "ai_generated"
            result["difficulty_level"] = difficulty_level
            result["source"] = "openai"
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI content generation failed: {str(e)}")
    
    async def get_smart_recommendations(self, user_profile: Dict[str, Any], 
                                      performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get AI-powered learning recommendations"""
        
        if not self.openai_available:
            raise Exception("OpenAI not available")
        
        prompt = f"""
        Based on this user profile and performance data, provide personalized learning recommendations:
        
        User Profile: {json.dumps(user_profile, indent=2)}
        Performance Data: {json.dumps(performance_data, indent=2)}
        
        Generate 3-5 specific learning recommendations with:
        - title: specific learning topic/activity
        - description: detailed description of the recommendation
        - reason: why this is recommended based on the data
        - confidence: how confident you are in this recommendation (0-1)
        - difficulty: estimated difficulty level (beginner/intermediate/advanced)
        - time_estimate: estimated time to complete (in minutes)
        - learning_style_adaptation: how to adapt for their learning style
        - prerequisites: any prerequisites needed
        - expected_outcomes: what the user will learn/achieve
        
        Return as JSON array only, no additional text.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI tutor that provides personalized learning recommendations. Respond only with valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(result, list):
                result = [result]
            
            # Add source to each recommendation
            for rec in result:
                rec["source"] = "openai"
            
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI recommendations failed: {str(e)}")
    
    async def generate_quiz_questions(self, topic: str, difficulty_level: str, 
                                    learning_style: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate adaptive quiz questions using OpenAI"""
        
        if not self.openai_available:
            raise Exception("OpenAI not available")
        
        prompt = f"""
        Generate {num_questions} quiz questions for:
        - Topic: {topic}
        - Difficulty Level: {difficulty_level}
        - Learning Style: {learning_style}
        
        Create questions adapted to the learning style:
        - Visual learners: include diagram descriptions, visual scenarios
        - Auditory learners: include sound-based or verbal scenarios
        - Kinesthetic learners: include hands-on, practical scenarios
        - Reading/Writing learners: include text analysis, written scenarios
        
        For each question provide:
        - question: the question text
        - type: multiple_choice, true_false, short_answer, or practical
        - options: array of answer choices (for multiple choice)
        - correct_answer: the correct answer
        - explanation: detailed explanation of why this is correct
        - learning_style_hint: specific hint adapted to the learning style
        
        Return as JSON array only, no additional text.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an educational assessment expert. Create adaptive quiz questions. Respond only with valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(result, list):
                result = [result]
            
            # Add metadata to each question
            for question in result:
                question["source"] = "openai"
                question["topic"] = topic
                question["difficulty"] = difficulty_level
                question["learning_style"] = learning_style
            
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI quiz generation failed: {str(e)}")