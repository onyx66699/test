from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, LearningProgress, LearningSession
from app.models.content import LearningContent, Quiz, AdaptiveRecommendation
from app.ai.learning_style_analyzer import LearningStyleAnalyzer
from app.ai.content_generator import ContentGenerator
from app.ai.recommendation_engine import RecommendationEngine
from app.ai.reinforcement_learning import AdaptiveLearningAgent
from datetime import datetime, timedelta
import json

class LearningService:
    """
    Main service that orchestrates all AI components for adaptive learning.
    """
    
    def __init__(self):
        self.style_analyzer = LearningStyleAnalyzer()
        self.content_generator = ContentGenerator()
        self.recommendation_engine = RecommendationEngine()
        self.rl_agent = AdaptiveLearningAgent()
    
    def analyze_user_learning_style(
        self, 
        db: Session, 
        user_id: int, 
        session_data: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze and update user's learning style based on session data.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get user's session history
        sessions = db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).order_by(LearningSession.created_at.desc()).limit(50).all()
        
        # Convert to dict format for analysis
        session_dicts = []
        for session in sessions:
            session_dict = {
                'content_type': session.session_type,
                'duration': session.duration,
                'performance_score': session.performance_score,
                'engagement_score': session.engagement_score,
                'difficulty_level': session.difficulty_level,
                'content_id': session.content_id,
                'adaptations_made': session.adaptations_made or {},
                'interactions': {}  # Would be populated from detailed session data
            }
            session_dicts.append(session_dict)
        
        # Add current session if provided
        if session_data:
            session_dicts.insert(0, session_data)
        
        # Generate learning profile
        if len(session_dicts) > 0:
            learning_profile = self.style_analyzer.generate_learning_profile(session_dicts)
        else:
            learning_profile = self.style_analyzer._default_profile()
        
        # Update user's learning style in database
        user.learning_style = learning_profile.get('style_scores', {})
        user.neurodivergent_accommodations = learning_profile.get('neurodivergent_accommodations', {})
        db.commit()
        
        return learning_profile
    
    def generate_personalized_content(
        self,
        db: Session,
        user_id: int,
        topic: str,
        content_type: str = 'auto',
        difficulty: Optional[float] = None
    ) -> Dict:
        """
        Generate personalized learning content for a user.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get user's learning profile
        learning_style = user.learning_style or {}
        primary_style = max(learning_style, key=learning_style.get) if learning_style else 'visual'
        accommodations = user.neurodivergent_accommodations or {}
        
        # Get user's progress in this topic
        progress = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.topic == topic
        ).first()
        
        # Determine difficulty level
        if difficulty is None:
            if progress:
                difficulty = progress.skill_level
            else:
                difficulty = 0.3  # Start with easier content for new topics
        
        # Get user background for personalization
        user_background = {
            'completed_topics': self._get_completed_topics(db, user_id),
            'knowledge_gaps': progress.knowledge_gaps if progress else [],
            'strengths': progress.strengths if progress else []
        }
        
        # Generate learning objectives
        learning_objectives = self._generate_learning_objectives(topic, difficulty)
        
        # Generate personalized content
        if content_type == 'auto':
            content_type = self._determine_optimal_content_type(primary_style, difficulty)
        
        if content_type == 'quiz':
            content = self.content_generator.generate_personalized_quiz(
                topic=topic,
                difficulty=difficulty,
                learning_style=primary_style,
                user_knowledge={'gaps': user_background['knowledge_gaps'], 'strengths': user_background['strengths']},
                num_questions=10
            )
        elif content_type == 'exercise':
            content = self.content_generator.generate_adaptive_exercise(
                topic=topic,
                learning_style=primary_style,
                difficulty=difficulty,
                time_available=30,  # 30 minutes default
                user_accommodations=accommodations
            )
        else:
            content = self.content_generator.generate_personalized_content(
                topic=topic,
                learning_objectives=learning_objectives,
                learning_style=primary_style,
                difficulty=difficulty,
                user_background=user_background
            )
        
        # Store content in database
        db_content = LearningContent(
            title=content['title'],
            subject=topic.split('_')[0] if '_' in topic else 'General',
            topic=topic,
            content_type=content_type,
            difficulty_level=difficulty,
            estimated_duration=content.get('estimated_duration', content.get('estimated_time', 30)),
            content_data=content,
            learning_objectives=learning_objectives,
            accessibility_features=accommodations
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        
        return {
            'content_id': db_content.id,
            'content': content,
            'personalization_applied': {
                'learning_style': primary_style,
                'accommodations': list(accommodations.keys()),
                'difficulty_level': difficulty
            }
        }
    
    def get_personalized_recommendations(
        self,
        db: Session,
        user_id: int,
        context: Optional[Dict] = None,
        num_recommendations: int = 5
    ) -> List[Dict]:
        """
        Get personalized content recommendations for a user.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Build user profile
        user_profile = self._build_user_profile(db, user_id)
        
        # Get available content
        available_content = db.query(LearningContent).filter(
            LearningContent.is_active == True
        ).all()
        
        # Convert to dict format
        content_dicts = []
        for content in available_content:
            content_dict = {
                'id': content.id,
                'title': content.title,
                'subject': content.subject,
                'topic': content.topic,
                'content_type': content.content_type,
                'difficulty_level': content.difficulty_level,
                'estimated_duration': content.estimated_duration,
                'topics': [content.topic],  # Simplified
                'interactive_elements': content.content_data.get('interactive_elements', 0) if content.content_data else 0,
                'media_types': content.content_data.get('media_types', []) if content.content_data else []
            }
            content_dicts.append(content_dict)
        
        # Get recommendations
        recommendations = self.recommendation_engine.get_personalized_recommendations(
            user_id=user_id,
            user_profile=user_profile,
            available_content=content_dicts,
            current_session_context=context,
            num_recommendations=num_recommendations
        )
        
        # Store recommendations in database
        for rec in recommendations:
            db_recommendation = AdaptiveRecommendation(
                user_id=user_id,
                content_id=rec['content_id'],
                recommendation_type='personalized',
                confidence_score=rec['confidence'],
                reasoning=rec['reasoning'],
                personalization_factors={
                    'learning_style': user_profile.get('primary_learning_style'),
                    'difficulty_match': True,
                    'context': context or {}
                }
            )
            db.add(db_recommendation)
        
        db.commit()
        
        return recommendations
    
    def adapt_content_realtime(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        current_performance: Dict,
        user_feedback: Optional[Dict] = None
    ) -> Dict:
        """
        Adapt content in real-time based on user performance and feedback.
        """
        # Get current session
        session = db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.content_id == session_id
        ).order_by(LearningSession.created_at.desc()).first()
        
        if not session:
            raise ValueError("Session not found")
        
        # Get user profile
        user_profile = self._build_user_profile(db, user_id)
        
        # Get RL agent's state representation
        session_data = {
            'performance_score': current_performance.get('score', 0.5),
            'engagement_score': current_performance.get('engagement', 0.5),
            'duration': current_performance.get('time_spent', 0),
            'difficulty_level': session.difficulty_level,
            'content_type': session.session_type,
            'estimated_duration': 1800  # 30 minutes default
        }
        
        current_state = self.rl_agent.get_state_representation(session_data, user_profile)
        
        # Get adaptation recommendations
        adaptations = self.rl_agent.get_adaptation_recommendations(
            current_state=current_state,
            user_session=session_data,
            user_profile=user_profile
        )
        
        # Apply the top adaptation
        if adaptations:
            top_adaptation = adaptations[0]
            adaptation_result = self._apply_adaptation(
                db, session, top_adaptation, current_performance
            )
            
            # Update session with adaptation
            session.adaptations_made = session.adaptations_made or {}
            session.adaptations_made.update({
                datetime.now().isoformat(): {
                    'action': top_adaptation['action'],
                    'reason': top_adaptation['explanation'],
                    'implementation': top_adaptation['implementation']
                }
            })
            db.commit()
            
            return {
                'adaptation_applied': top_adaptation,
                'result': adaptation_result,
                'all_recommendations': adaptations
            }
        
        return {'adaptation_applied': None, 'result': None, 'all_recommendations': []}
    
    def record_learning_session(
        self,
        db: Session,
        user_id: int,
        session_data: Dict
    ) -> int:
        """
        Record a completed learning session and update user progress.
        """
        # Create session record
        session = LearningSession(
            user_id=user_id,
            session_type=session_data.get('content_type', 'unknown'),
            content_id=session_data.get('content_id', ''),
            duration=session_data.get('duration', 0),
            performance_score=session_data.get('performance_score', 0.5),
            engagement_score=session_data.get('engagement_score', 0.5),
            difficulty_level=session_data.get('difficulty_level', 0.5),
            adaptations_made=session_data.get('adaptations_made', {}),
            feedback_given=session_data.get('ai_feedback', {}),
            user_feedback=session_data.get('user_feedback', {})
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Update user progress
        self._update_user_progress(db, user_id, session_data)
        
        # Update learning style analysis
        self.analyze_user_learning_style(db, user_id, session_data)
        
        # Train RL agent if we have previous session data
        self._train_rl_agent(db, user_id, session)
        
        return session.id
    
    def get_learning_analytics(
        self,
        db: Session,
        user_id: int,
        time_range: Optional[int] = 30  # days
    ) -> Dict:
        """
        Get comprehensive learning analytics for a user.
        """
        # Get session history
        cutoff_date = datetime.now() - timedelta(days=time_range)
        sessions = db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.created_at >= cutoff_date
        ).order_by(LearningSession.created_at).all()
        
        # Convert to dict format
        session_dicts = []
        for session in sessions:
            session_dict = {
                'id': session.id,
                'session_type': session.session_type,
                'content_id': session.content_id,
                'duration': session.duration,
                'performance_score': session.performance_score,
                'engagement_score': session.engagement_score,
                'difficulty_level': session.difficulty_level,
                'adaptations_made': session.adaptations_made or {},
                'created_at': session.created_at.isoformat()
            }
            session_dicts.append(session_dict)
        
        # Analyze learning patterns
        patterns = self.rl_agent.analyze_learning_patterns(user_id, session_dicts)
        
        # Get current progress
        progress_records = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()
        
        progress_summary = {}
        for progress in progress_records:
            progress_summary[progress.topic] = {
                'skill_level': progress.skill_level,
                'completion_rate': progress.completion_rate,
                'time_spent': progress.time_spent,
                'knowledge_gaps': progress.knowledge_gaps or [],
                'strengths': progress.strengths or []
            }
        
        # Calculate overall metrics
        if sessions:
            avg_performance = sum(s.performance_score for s in sessions) / len(sessions)
            avg_engagement = sum(s.engagement_score for s in sessions) / len(sessions)
            total_time = sum(s.duration for s in sessions) / 60  # Convert to minutes
        else:
            avg_performance = avg_engagement = total_time = 0
        
        return {
            'summary': {
                'total_sessions': len(sessions),
                'total_time_minutes': total_time,
                'average_performance': avg_performance,
                'average_engagement': avg_engagement,
                'time_range_days': time_range
            },
            'progress_by_topic': progress_summary,
            'learning_patterns': patterns,
            'recommendations': self._generate_analytics_recommendations(patterns, progress_summary)
        }
    
    def _build_user_profile(self, db: Session, user_id: int) -> Dict:
        """Build comprehensive user profile for AI components."""
        user = db.query(User).filter(User.id == user_id).first()
        
        # Get learning style
        learning_style = user.learning_style or {}
        primary_style = max(learning_style, key=learning_style.get) if learning_style else 'visual'
        
        # Get progress data
        progress_records = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()
        
        knowledge_gaps = []
        strengths = []
        current_skill_level = 0.5
        
        if progress_records:
            for progress in progress_records:
                if progress.knowledge_gaps:
                    knowledge_gaps.extend(progress.knowledge_gaps)
                if progress.strengths:
                    strengths.extend(progress.strengths)
            
            # Calculate average skill level
            skill_levels = [p.skill_level for p in progress_records]
            current_skill_level = sum(skill_levels) / len(skill_levels)
        
        # Get completed content
        sessions = db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).all()
        
        completed_content = list(set(s.content_id for s in sessions))
        
        return {
            'primary_learning_style': primary_style,
            'style_scores': learning_style,
            'neurodivergent_accommodations': user.neurodivergent_accommodations or {},
            'current_skill_level': current_skill_level,
            'knowledge_gaps': knowledge_gaps,
            'strengths': strengths,
            'completed_content': completed_content,
            'recent_performance': [
                {
                    'score': s.performance_score,
                    'topic': s.content_id,
                    'date': s.created_at.isoformat()
                }
                for s in sessions[-10:]  # Last 10 sessions
            ]
        }
    
    def _get_completed_topics(self, db: Session, user_id: int) -> List[str]:
        """Get list of topics the user has completed."""
        progress_records = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.completion_rate >= 0.8
        ).all()
        
        return [p.topic for p in progress_records]
    
    def _generate_learning_objectives(self, topic: str, difficulty: float) -> List[str]:
        """Generate learning objectives for a topic based on difficulty."""
        base_objectives = [
            f"Understand the fundamentals of {topic}",
            f"Apply {topic} concepts in practical scenarios"
        ]
        
        if difficulty > 0.6:
            base_objectives.extend([
                f"Analyze complex {topic} problems",
                f"Evaluate different approaches to {topic}",
                f"Create original solutions using {topic}"
            ])
        
        return base_objectives
    
    def _determine_optimal_content_type(self, learning_style: str, difficulty: float) -> str:
        """Determine optimal content type based on learning style and difficulty."""
        if learning_style == 'visual':
            return 'infographic' if difficulty < 0.5 else 'interactive'
        elif learning_style == 'auditory':
            return 'audio' if difficulty < 0.5 else 'discussion'
        elif learning_style == 'kinesthetic':
            return 'exercise' if difficulty < 0.5 else 'simulation'
        else:
            return 'mixed'
    
    def _apply_adaptation(
        self, 
        db: Session, 
        session: LearningSession, 
        adaptation: Dict, 
        current_performance: Dict
    ) -> Dict:
        """Apply a specific adaptation to the learning session."""
        action = adaptation['action']
        implementation = adaptation['implementation']
        
        result = {'action_taken': action, 'changes_made': []}
        
        if action == 'increase_difficulty':
            new_difficulty = min(1.0, session.difficulty_level + 0.1)
            session.difficulty_level = new_difficulty
            result['changes_made'].append(f"Increased difficulty to {new_difficulty:.1f}")
        
        elif action == 'decrease_difficulty':
            new_difficulty = max(0.1, session.difficulty_level - 0.1)
            session.difficulty_level = new_difficulty
            result['changes_made'].append(f"Decreased difficulty to {new_difficulty:.1f}")
        
        elif action == 'add_break':
            result['changes_made'].append("Break reminder added")
            # In a real implementation, this would trigger a break notification
        
        elif action == 'provide_hint':
            result['changes_made'].append("Hint provided")
            # In a real implementation, this would show a hint to the user
        
        elif action == 'gamify_content':
            result['changes_made'].append("Gamification elements added")
            # In a real implementation, this would add points, badges, etc.
        
        db.commit()
        return result
    
    def _update_user_progress(self, db: Session, user_id: int, session_data: Dict):
        """Update user's learning progress based on session data."""
        topic = session_data.get('topic', 'general')
        
        # Get or create progress record
        progress = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.topic == topic
        ).first()
        
        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                subject=topic.split('_')[0] if '_' in topic else 'General',
                topic=topic,
                skill_level=0.3,
                completion_rate=0.0,
                time_spent=0,
                knowledge_gaps=[],
                strengths=[]
            )
            db.add(progress)
        
        # Update progress metrics
        performance = session_data.get('performance_score', 0.5)
        session_time = session_data.get('duration', 0) // 60  # Convert to minutes
        
        # Update skill level using exponential moving average
        alpha = 0.2
        progress.skill_level = (1 - alpha) * progress.skill_level + alpha * performance
        
        # Update time spent
        progress.time_spent += session_time
        
        # Update completion rate (simplified)
        progress.completion_rate = min(1.0, progress.completion_rate + 0.1)
        
        # Update last accessed
        progress.last_accessed = datetime.now()
        
        db.commit()
    
    def _train_rl_agent(self, db: Session, user_id: int, current_session: LearningSession):
        """Train the RL agent with the latest session data."""
        # Get previous session for comparison
        previous_session = db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.id < current_session.id
        ).order_by(LearningSession.created_at.desc()).first()
        
        if not previous_session:
            return  # Need at least 2 sessions to train
        
        # Build user profile
        user_profile = self._build_user_profile(db, user_id)
        
        # Convert sessions to format expected by RL agent
        prev_session_data = {
            'performance_score': previous_session.performance_score,
            'engagement_score': previous_session.engagement_score,
            'duration': previous_session.duration,
            'difficulty_level': previous_session.difficulty_level,
            'content_type': previous_session.session_type
        }
        
        curr_session_data = {
            'performance_score': current_session.performance_score,
            'engagement_score': current_session.engagement_score,
            'duration': current_session.duration,
            'difficulty_level': current_session.difficulty_level,
            'content_type': current_session.session_type
        }
        
        # Get states
        prev_state = self.rl_agent.get_state_representation(prev_session_data, user_profile)
        curr_state = self.rl_agent.get_state_representation(curr_session_data, user_profile)
        
        # Determine action taken (simplified - would be more sophisticated in practice)
        action_taken = 'maintain_course'  # Default action
        if current_session.adaptations_made:
            # Get the most recent adaptation
            adaptations = current_session.adaptations_made
            if adaptations:
                latest_adaptation = max(adaptations.keys())
                action_taken = adaptations[latest_adaptation].get('action', 'maintain_course')
        
        # Calculate reward
        reward = self.rl_agent.calculate_reward(
            prev_session_data,
            curr_session_data,
            action_taken,
            current_session.user_feedback
        )
        
        # Update Q-value
        self.rl_agent.update_q_value(
            state=prev_state,
            action=action_taken,
            reward=reward,
            next_state=curr_state,
            done=False
        )
        
        # Perform experience replay periodically
        if current_session.id % 10 == 0:  # Every 10 sessions
            self.rl_agent.experience_replay()
        
        # Adapt learning parameters
        self.rl_agent.adapt_learning_parameters(reward)
    
    def _generate_analytics_recommendations(
        self, 
        patterns: Dict, 
        progress_summary: Dict
    ) -> List[str]:
        """Generate recommendations based on learning analytics."""
        recommendations = []
        
        # Analyze engagement patterns
        engagement_patterns = patterns.get('engagement_patterns', {})
        
        # Check content type preferences
        content_engagement = engagement_patterns.get('by_content_type', {})
        if content_engagement:
            best_content = max(content_engagement.items(), key=lambda x: x[1].get('average', 0))
            recommendations.append(
                f"You perform best with {best_content[0]} content. Consider focusing on this format."
            )
        
        # Check difficulty patterns
        difficulty_engagement = engagement_patterns.get('by_difficulty', {})
        if difficulty_engagement:
            best_difficulty = max(difficulty_engagement.items(), key=lambda x: x[1].get('average', 0))
            recommendations.append(
                f"You're most engaged with {best_difficulty[0]} difficulty content."
            )
        
        # Check for knowledge gaps
        all_gaps = []
        for topic_progress in progress_summary.values():
            all_gaps.extend(topic_progress.get('knowledge_gaps', []))
        
        if all_gaps:
            most_common_gap = max(set(all_gaps), key=all_gaps.count)
            recommendations.append(
                f"Focus on improving '{most_common_gap}' as it appears in multiple topics."
            )
        
        # Check learning efficiency
        efficiency_trends = patterns.get('learning_efficiency_trends', [])
        if efficiency_trends:
            recent_efficiency = [t['efficiency'] for t in efficiency_trends[-5:]]
            if recent_efficiency and sum(recent_efficiency) / len(recent_efficiency) < 0.5:
                recommendations.append(
                    "Your learning efficiency has decreased recently. Consider taking breaks or changing your study environment."
                )
        
        return recommendations[:5]  # Limit to top 5 recommendations