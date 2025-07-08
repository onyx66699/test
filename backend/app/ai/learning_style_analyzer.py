import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime, timedelta

class LearningStyleAnalyzer:
    """
    Analyzes user behavior and preferences to determine learning style.
    Identifies Visual, Auditory, and Kinesthetic learning preferences.
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Learning style indicators
        self.visual_indicators = [
            'prefers_diagrams', 'uses_highlighting', 'takes_notes_visually',
            'remembers_faces', 'good_with_maps', 'likes_charts'
        ]
        
        self.auditory_indicators = [
            'prefers_lectures', 'talks_through_problems', 'remembers_names',
            'enjoys_discussions', 'learns_from_audio', 'thinks_out_loud'
        ]
        
        self.kinesthetic_indicators = [
            'prefers_hands_on', 'fidgets_while_learning', 'uses_gestures',
            'learns_by_doing', 'needs_breaks', 'physical_activities'
        ]
    
    def analyze_session_behavior(self, session_data: Dict) -> Dict[str, float]:
        """
        Analyze a learning session to extract learning style indicators.
        """
        indicators = {
            'visual_score': 0.0,
            'auditory_score': 0.0,
            'kinesthetic_score': 0.0
        }
        
        # Analyze content type preferences
        content_type = session_data.get('content_type', '')
        if content_type in ['diagram', 'chart', 'infographic', 'video']:
            indicators['visual_score'] += 0.3
        elif content_type in ['audio', 'podcast', 'lecture']:
            indicators['auditory_score'] += 0.3
        elif content_type in ['interactive', 'simulation', 'hands_on']:
            indicators['kinesthetic_score'] += 0.3
        
        # Analyze engagement patterns
        engagement = session_data.get('engagement_score', 0.5)
        duration = session_data.get('duration', 0)
        
        # Visual learners often engage well with visual content
        if content_type in ['video', 'diagram'] and engagement > 0.7:
            indicators['visual_score'] += 0.2
        
        # Kinesthetic learners may have shorter attention spans for passive content
        if content_type in ['text', 'lecture'] and duration < 300:  # less than 5 minutes
            indicators['kinesthetic_score'] += 0.1
        
        # Analyze interaction patterns
        interactions = session_data.get('interactions', {})
        if interactions.get('note_taking', False):
            indicators['visual_score'] += 0.1
        if interactions.get('audio_playback', 0) > 1:
            indicators['auditory_score'] += 0.1
        if interactions.get('interactive_elements', 0) > 3:
            indicators['kinesthetic_score'] += 0.1
        
        return indicators
    
    def analyze_performance_patterns(self, user_sessions: List[Dict]) -> Dict[str, float]:
        """
        Analyze performance patterns across multiple sessions to identify learning style.
        """
        style_scores = {'visual': 0.0, 'auditory': 0.0, 'kinesthetic': 0.0}
        content_performance = {'visual': [], 'auditory': [], 'kinesthetic': []}
        
        for session in user_sessions:
            content_type = session.get('content_type', '')
            performance = session.get('performance_score', 0.5)
            
            # Categorize content types
            if content_type in ['video', 'diagram', 'chart', 'infographic', 'image']:
                content_performance['visual'].append(performance)
            elif content_type in ['audio', 'podcast', 'lecture', 'discussion']:
                content_performance['auditory'].append(performance)
            elif content_type in ['interactive', 'simulation', 'hands_on', 'exercise']:
                content_performance['kinesthetic'].append(performance)
        
        # Calculate average performance for each style
        for style, performances in content_performance.items():
            if performances:
                avg_performance = np.mean(performances)
                style_scores[style] = avg_performance
        
        return style_scores
    
    def detect_neurodivergent_patterns(self, user_sessions: List[Dict]) -> Dict[str, any]:
        """
        Detect patterns that might indicate neurodivergent learning needs.
        """
        accommodations = {
            'needs_breaks': False,
            'prefers_structure': False,
            'sensitive_to_distractions': False,
            'needs_extra_time': False,
            'benefits_from_repetition': False,
            'prefers_clear_instructions': False
        }
        
        if not user_sessions:
            return accommodations
        
        # Analyze session durations
        durations = [s.get('duration', 0) for s in user_sessions]
        avg_duration = np.mean(durations) if durations else 0
        
        # Short sessions might indicate need for breaks
        if avg_duration < 600:  # less than 10 minutes average
            accommodations['needs_breaks'] = True
        
        # Analyze performance consistency
        performances = [s.get('performance_score', 0.5) for s in user_sessions]
        if performances:
            performance_std = np.std(performances)
            if performance_std > 0.3:  # high variability
                accommodations['sensitive_to_distractions'] = True
        
        # Analyze time patterns
        completion_times = []
        for session in user_sessions:
            estimated_time = session.get('estimated_duration', 0)
            actual_time = session.get('duration', 0)
            if estimated_time > 0:
                completion_times.append(actual_time / estimated_time)
        
        if completion_times:
            avg_completion_ratio = np.mean(completion_times)
            if avg_completion_ratio > 1.5:  # takes 50% longer than estimated
                accommodations['needs_extra_time'] = True
        
        # Analyze repetition patterns
        repeated_content = {}
        for session in user_sessions:
            content_id = session.get('content_id', '')
            if content_id:
                repeated_content[content_id] = repeated_content.get(content_id, 0) + 1
        
        if repeated_content:
            max_repetitions = max(repeated_content.values())
            if max_repetitions > 3:
                accommodations['benefits_from_repetition'] = True
        
        return accommodations
    
    def generate_learning_profile(self, user_sessions: List[Dict]) -> Dict[str, any]:
        """
        Generate a comprehensive learning profile for a user.
        """
        if not user_sessions:
            return self._default_profile()
        
        # Analyze learning style preferences
        style_scores = self.analyze_performance_patterns(user_sessions)
        
        # Analyze behavioral patterns
        behavior_indicators = {'visual': 0.0, 'auditory': 0.0, 'kinesthetic': 0.0}
        for session in user_sessions:
            session_indicators = self.analyze_session_behavior(session)
            behavior_indicators['visual'] += session_indicators['visual_score']
            behavior_indicators['auditory'] += session_indicators['auditory_score']
            behavior_indicators['kinesthetic'] += session_indicators['kinesthetic_score']
        
        # Normalize behavior indicators
        total_sessions = len(user_sessions)
        for style in behavior_indicators:
            behavior_indicators[style] /= total_sessions
        
        # Combine performance and behavior scores
        combined_scores = {}
        for style in ['visual', 'auditory', 'kinesthetic']:
            performance_weight = 0.7
            behavior_weight = 0.3
            combined_scores[style] = (
                style_scores.get(style, 0.5) * performance_weight +
                behavior_indicators[style] * behavior_weight
            )
        
        # Determine primary learning style
        primary_style = max(combined_scores, key=combined_scores.get)
        
        # Detect neurodivergent accommodations
        accommodations = self.detect_neurodivergent_patterns(user_sessions)
        
        # Calculate confidence based on data quality
        confidence = min(1.0, len(user_sessions) / 20.0)  # Full confidence after 20 sessions
        
        profile = {
            'primary_learning_style': primary_style,
            'style_scores': combined_scores,
            'confidence': confidence,
            'neurodivergent_accommodations': accommodations,
            'recommendations': self._generate_style_recommendations(primary_style, accommodations),
            'last_updated': datetime.now().isoformat()
        }
        
        return profile
    
    def _default_profile(self) -> Dict[str, any]:
        """Return a default profile for new users."""
        return {
            'primary_learning_style': 'visual',  # Most common default
            'style_scores': {'visual': 0.4, 'auditory': 0.3, 'kinesthetic': 0.3},
            'confidence': 0.1,
            'neurodivergent_accommodations': {
                'needs_breaks': False,
                'prefers_structure': True,  # Generally helpful
                'sensitive_to_distractions': False,
                'needs_extra_time': False,
                'benefits_from_repetition': False,
                'prefers_clear_instructions': True  # Generally helpful
            },
            'recommendations': self._generate_style_recommendations('visual', {}),
            'last_updated': datetime.now().isoformat()
        }
    
    def _generate_style_recommendations(self, primary_style: str, accommodations: Dict) -> List[str]:
        """Generate recommendations based on learning style and accommodations."""
        recommendations = []
        
        if primary_style == 'visual':
            recommendations.extend([
                "Use diagrams and charts to understand concepts",
                "Take visual notes with colors and highlighting",
                "Watch educational videos and animations",
                "Create mind maps for complex topics"
            ])
        elif primary_style == 'auditory':
            recommendations.extend([
                "Listen to educational podcasts and lectures",
                "Discuss topics with others or explain them aloud",
                "Use text-to-speech for reading materials",
                "Record yourself explaining concepts"
            ])
        elif primary_style == 'kinesthetic':
            recommendations.extend([
                "Use hands-on activities and simulations",
                "Take frequent breaks during study sessions",
                "Use physical objects to understand abstract concepts",
                "Practice skills through real-world applications"
            ])
        
        # Add accommodation-based recommendations
        if accommodations.get('needs_breaks'):
            recommendations.append("Take 5-10 minute breaks every 20-30 minutes")
        
        if accommodations.get('needs_extra_time'):
            recommendations.append("Allow extra time for completing assignments")
        
        if accommodations.get('benefits_from_repetition'):
            recommendations.append("Review material multiple times using different methods")
        
        if accommodations.get('sensitive_to_distractions'):
            recommendations.append("Study in a quiet, distraction-free environment")
        
        return recommendations
    
    def update_profile_from_session(self, current_profile: Dict, new_session: Dict) -> Dict:
        """
        Update an existing learning profile with new session data.
        """
        # Analyze new session
        session_indicators = self.analyze_session_behavior(new_session)
        
        # Update style scores with exponential moving average
        alpha = 0.1  # Learning rate
        current_scores = current_profile.get('style_scores', {})
        
        for style in ['visual', 'auditory', 'kinesthetic']:
            current_score = current_scores.get(style, 0.33)
            new_indicator = session_indicators.get(f'{style}_score', 0)
            
            # Update with exponential moving average
            updated_score = (1 - alpha) * current_score + alpha * new_indicator
            current_scores[style] = updated_score
        
        # Update primary style
        primary_style = max(current_scores, key=current_scores.get)
        
        # Increase confidence gradually
        current_confidence = current_profile.get('confidence', 0.1)
        updated_confidence = min(1.0, current_confidence + 0.05)
        
        # Update profile
        updated_profile = current_profile.copy()
        updated_profile.update({
            'primary_learning_style': primary_style,
            'style_scores': current_scores,
            'confidence': updated_confidence,
            'last_updated': datetime.now().isoformat()
        })
        
        return updated_profile