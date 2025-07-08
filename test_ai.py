#!/usr/bin/env python3
"""
Test script to verify AI components are working
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.ai.learning_style_analyzer import LearningStyleAnalyzer
from app.ai.content_generator import ContentGenerator
from app.ai.recommendation_engine import RecommendationEngine

def test_learning_style_analyzer():
    print("🧠 Testing Learning Style Analyzer...")
    analyzer = LearningStyleAnalyzer()
    
    # Create sample session data
    session_data = {
        'time_spent': 1800,
        'interactions': ['click_diagram', 'take_notes', 'practice_exercise'],
        'engagement_score': 0.8,
        'completion_rate': 0.9,
        'help_requests': 2
    }
    
    try:
        result = analyzer.analyze_session_behavior(session_data)
        print(f"✅ Visual Score: {result.get('visual', 0):.2f}")
        print(f"✅ Auditory Score: {result.get('auditory', 0):.2f}")
        print(f"✅ Kinesthetic Score: {result.get('kinesthetic', 0):.2f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_content_generator():
    print("\n🎨 Testing Content Generator...")
    generator = ContentGenerator()
    
    try:
        content = generator.generate_personalized_content(
            topic="Python Functions",
            learning_style="visual",
            difficulty_level=0.3,  # beginner level
            user_preferences=["interactive_examples", "visual_aids"]
        )
        print(f"✅ Content Type: {content.get('content_type', 'N/A')}")
        print(f"✅ Difficulty: {content.get('difficulty_level', 'N/A')}")
        print(f"✅ Content Preview: {str(content)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_recommendation_engine():
    print("\n🎯 Testing Recommendation Engine...")
    engine = RecommendationEngine()
    
    try:
        # Create sample user profile
        user_profile = {
            'learning_style': 'visual',
            'current_level': 0.5,
            'knowledge_gaps': ['functions', 'loops'],
            'completed_content': ['variables', 'data_types'],
            'performance_history': [0.8, 0.7, 0.9]
        }
        
        recommendations = engine.get_personalized_recommendations(
            user_profile=user_profile,
            available_content=[
                {'id': 1, 'title': 'Python Functions', 'difficulty': 0.4, 'topics': ['functions']},
                {'id': 2, 'title': 'For Loops', 'difficulty': 0.3, 'topics': ['loops']},
                {'id': 3, 'title': 'Advanced OOP', 'difficulty': 0.8, 'topics': ['classes']}
            ],
            num_recommendations=3
        )
        print(f"✅ Recommendations: {len(recommendations)}")
        if recommendations:
            rec = recommendations[0]
            print(f"✅ Top Recommendation: {rec.get('title', 'N/A')}")
            print(f"✅ Score: {rec.get('score', 0):.2f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Testing AI Components\n")
    
    tests = [
        test_learning_style_analyzer,
        test_content_generator,
        test_recommendation_engine
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All AI components are working correctly!")
    else:
        print("⚠️ Some components need attention")

if __name__ == "__main__":
    main()