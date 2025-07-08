import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime, timedelta
import random

class RecommendationEngine:
    """
    AI-powered recommendation engine that suggests personalized learning content
    based on user progress, learning style, and performance patterns.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.user_profiles = {}
        self.content_features = {}
        self.interaction_history = {}
        
        # Recommendation weights
        self.weights = {
            'learning_style_match': 0.3,
            'difficulty_appropriateness': 0.25,
            'knowledge_gap_relevance': 0.2,
            'engagement_prediction': 0.15,
            'novelty_factor': 0.1
        }
    
    def get_personalized_recommendations(
        self,
        user_id: int,
        user_profile: Dict,
        available_content: List[Dict],
        current_session_context: Optional[Dict] = None,
        num_recommendations: int = 5
    ) -> List[Dict]:
        """
        Generate personalized content recommendations for a user.
        """
        if not available_content:
            return []
        
        # Calculate recommendation scores for each content item
        scored_content = []
        
        for content in available_content:
            score = self._calculate_recommendation_score(
                user_profile, content, current_session_context
            )
            
            recommendation = {
                'content_id': content.get('id'),
                'content': content,
                'score': score,
                'reasoning': self._generate_reasoning(user_profile, content, score),
                'estimated_benefit': self._estimate_learning_benefit(user_profile, content),
                'confidence': self._calculate_confidence(user_profile, content)
            }
            
            scored_content.append(recommendation)
        
        # Sort by score and return top recommendations
        scored_content.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply diversity to avoid recommending too similar content
        diverse_recommendations = self._apply_diversity_filter(
            scored_content[:num_recommendations * 2], num_recommendations
        )
        
        return diverse_recommendations[:num_recommendations]
    
    def get_next_learning_path(
        self,
        user_id: int,
        user_profile: Dict,
        current_progress: Dict,
        learning_goals: List[str],
        time_available: int  # minutes
    ) -> Dict:
        """
        Recommend the next steps in the user's learning path.
        """
        learning_path = {
            'recommended_sequence': [],
            'estimated_total_time': 0,
            'learning_objectives': [],
            'difficulty_progression': [],
            'style_adaptations': [],
            'checkpoint_assessments': []
        }
        
        # Analyze current knowledge state
        knowledge_state = self._analyze_knowledge_state(current_progress)
        
        # Identify priority learning areas
        priority_areas = self._identify_priority_areas(
            knowledge_state, learning_goals, user_profile
        )
        
        # Generate learning sequence
        remaining_time = time_available
        current_difficulty = knowledge_state.get('current_level', 0.5)
        
        for area in priority_areas:
            if remaining_time <= 0:
                break
            
            # Find appropriate content for this area
            area_content = self._find_content_for_area(
                area, current_difficulty, user_profile['primary_learning_style']
            )
            
            if area_content and area_content['estimated_duration'] <= remaining_time:
                learning_path['recommended_sequence'].append(area_content)
                learning_path['estimated_total_time'] += area_content['estimated_duration']
                learning_path['learning_objectives'].extend(area_content.get('objectives', []))
                learning_path['difficulty_progression'].append(current_difficulty)
                
                remaining_time -= area_content['estimated_duration']
                current_difficulty = min(1.0, current_difficulty + 0.1)  # Gradual increase
        
        # Add style adaptations
        learning_path['style_adaptations'] = self._get_path_adaptations(
            user_profile, learning_path['recommended_sequence']
        )
        
        # Add assessment checkpoints
        learning_path['checkpoint_assessments'] = self._plan_assessments(
            learning_path['recommended_sequence']
        )
        
        return learning_path
    
    def recommend_review_content(
        self,
        user_id: int,
        user_profile: Dict,
        performance_history: List[Dict],
        time_since_last_review: Dict  # topic -> days
    ) -> List[Dict]:
        """
        Recommend content for review based on forgetting curve and performance.
        """
        review_recommendations = []
        
        # Analyze what needs review based on forgetting curve
        for topic, days_since in time_since_last_review.items():
            # Calculate forgetting probability
            forgetting_prob = self._calculate_forgetting_probability(
                days_since, performance_history, topic
            )
            
            if forgetting_prob > 0.3:  # Threshold for review recommendation
                review_item = {
                    'topic': topic,
                    'urgency': forgetting_prob,
                    'recommended_method': self._get_optimal_review_method(
                        user_profile, topic, forgetting_prob
                    ),
                    'estimated_time': self._estimate_review_time(topic, forgetting_prob),
                    'reasoning': f"Review recommended due to {forgetting_prob:.1%} forgetting probability"
                }
                review_recommendations.append(review_item)
        
        # Sort by urgency
        review_recommendations.sort(key=lambda x: x['urgency'], reverse=True)
        
        return review_recommendations
    
    def adapt_recommendations_from_feedback(
        self,
        user_id: int,
        recommendation_id: str,
        user_feedback: Dict,
        actual_performance: Optional[Dict] = None
    ):
        """
        Update recommendation algorithm based on user feedback and performance.
        """
        # Store feedback for learning
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'recommendation_id': recommendation_id,
            'user_feedback': user_feedback,
            'actual_performance': actual_performance
        }
        
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
        
        self.interaction_history[user_id].append(feedback_entry)
        
        # Adjust recommendation weights based on feedback
        self._update_recommendation_weights(user_feedback, actual_performance)
        
        # Update user profile if needed
        if actual_performance:
            self._update_user_profile_from_performance(user_id, actual_performance)
    
    def _calculate_recommendation_score(
        self,
        user_profile: Dict,
        content: Dict,
        session_context: Optional[Dict] = None
    ) -> float:
        """
        Calculate a recommendation score for a piece of content.
        """
        scores = {}
        
        # Learning style match score
        scores['learning_style_match'] = self._calculate_style_match_score(
            user_profile.get('primary_learning_style', 'visual'),
            content.get('content_type', 'text')
        )
        
        # Difficulty appropriateness score
        user_level = user_profile.get('current_skill_level', 0.5)
        content_difficulty = content.get('difficulty_level', 0.5)
        scores['difficulty_appropriateness'] = self._calculate_difficulty_score(
            user_level, content_difficulty
        )
        
        # Knowledge gap relevance score
        user_gaps = user_profile.get('knowledge_gaps', [])
        content_topics = content.get('topics', [])
        scores['knowledge_gap_relevance'] = self._calculate_gap_relevance_score(
            user_gaps, content_topics
        )
        
        # Engagement prediction score
        scores['engagement_prediction'] = self._predict_engagement_score(
            user_profile, content
        )
        
        # Novelty factor score
        scores['novelty_factor'] = self._calculate_novelty_score(
            user_profile.get('completed_content', []),
            content
        )
        
        # Calculate weighted total score
        total_score = sum(
            scores[factor] * self.weights[factor]
            for factor in scores
        )
        
        # Apply session context adjustments
        if session_context:
            total_score = self._apply_session_context(total_score, session_context, content)
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_style_match_score(self, user_style: str, content_type: str) -> float:
        """Calculate how well content type matches user's learning style."""
        style_content_mapping = {
            'visual': {
                'video': 0.9, 'diagram': 1.0, 'infographic': 0.95,
                'image': 0.8, 'chart': 0.85, 'text': 0.3, 'audio': 0.1
            },
            'auditory': {
                'audio': 1.0, 'podcast': 0.95, 'lecture': 0.9,
                'discussion': 0.85, 'video': 0.6, 'text': 0.4, 'diagram': 0.2
            },
            'kinesthetic': {
                'interactive': 1.0, 'simulation': 0.95, 'hands_on': 0.9,
                'exercise': 0.85, 'video': 0.5, 'text': 0.2, 'audio': 0.3
            }
        }
        
        mapping = style_content_mapping.get(user_style, {})
        return mapping.get(content_type, 0.5)
    
    def _calculate_difficulty_score(self, user_level: float, content_difficulty: float) -> float:
        """Calculate appropriateness of content difficulty for user level."""
        # Optimal difficulty is slightly above user's current level (zone of proximal development)
        optimal_difficulty = user_level + 0.1
        difficulty_diff = abs(content_difficulty - optimal_difficulty)
        
        # Score decreases as difficulty difference increases
        if difficulty_diff <= 0.1:
            return 1.0
        elif difficulty_diff <= 0.2:
            return 0.8
        elif difficulty_diff <= 0.3:
            return 0.6
        else:
            return 0.3
    
    def _calculate_gap_relevance_score(self, user_gaps: List[str], content_topics: List[str]) -> float:
        """Calculate how well content addresses user's knowledge gaps."""
        if not user_gaps or not content_topics:
            return 0.5
        
        # Calculate overlap between gaps and content topics
        gap_set = set(user_gaps)
        topic_set = set(content_topics)
        overlap = len(gap_set.intersection(topic_set))
        
        if overlap == 0:
            return 0.2
        
        # Score based on proportion of gaps addressed
        relevance_score = overlap / len(gap_set)
        return min(1.0, relevance_score)
    
    def _predict_engagement_score(self, user_profile: Dict, content: Dict) -> float:
        """Predict how engaging the content will be for the user."""
        engagement_factors = {
            'interactive_elements': content.get('interactive_elements', 0) * 0.3,
            'multimedia_richness': len(content.get('media_types', [])) * 0.1,
            'personalization': content.get('personalization_level', 0.5) * 0.2,
            'social_elements': content.get('social_features', 0) * 0.1,
            'gamification': content.get('gamification_elements', 0) * 0.2
        }
        
        # Adjust based on user preferences
        accommodations = user_profile.get('neurodivergent_accommodations', {})
        if accommodations.get('sensitive_to_distractions'):
            engagement_factors['multimedia_richness'] *= 0.5
        
        base_score = sum(engagement_factors.values())
        
        # Add user history factor
        similar_content_performance = self._get_similar_content_performance(
            user_profile, content
        )
        
        return min(1.0, base_score + similar_content_performance * 0.1)
    
    def _calculate_novelty_score(self, completed_content: List[str], content: Dict) -> float:
        """Calculate novelty score to promote content diversity."""
        content_id = content.get('id', '')
        content_topics = set(content.get('topics', []))
        
        if content_id in completed_content:
            return 0.0  # Already completed
        
        # Check topic overlap with completed content
        completed_topics = set()
        for completed_id in completed_content:
            # In a real implementation, you'd fetch the topics for completed content
            # For now, we'll simulate this
            completed_topics.update([f"topic_{completed_id}"])
        
        if not completed_topics:
            return 1.0  # Everything is novel for new users
        
        overlap = len(content_topics.intersection(completed_topics))
        total_topics = len(content_topics)
        
        if total_topics == 0:
            return 0.5
        
        novelty = 1.0 - (overlap / total_topics)
        return novelty
    
    def _apply_session_context(
        self, 
        base_score: float, 
        session_context: Dict, 
        content: Dict
    ) -> float:
        """Apply session-specific adjustments to recommendation score."""
        adjusted_score = base_score
        
        # Time constraint adjustments
        available_time = session_context.get('time_available', 60)  # minutes
        content_duration = content.get('estimated_duration', 30)
        
        if content_duration > available_time:
            adjusted_score *= 0.3  # Heavily penalize content that won't fit
        elif content_duration <= available_time * 0.5:
            adjusted_score *= 1.1  # Slight bonus for content that fits well
        
        # Current performance adjustments
        current_performance = session_context.get('current_performance', 0.7)
        if current_performance < 0.5:  # User struggling
            content_difficulty = content.get('difficulty_level', 0.5)
            if content_difficulty > 0.6:
                adjusted_score *= 0.7  # Prefer easier content
        elif current_performance > 0.8:  # User excelling
            content_difficulty = content.get('difficulty_level', 0.5)
            if content_difficulty < 0.4:
                adjusted_score *= 0.8  # Prefer more challenging content
        
        # Energy level adjustments
        energy_level = session_context.get('energy_level', 'medium')
        if energy_level == 'low':
            if content.get('content_type') in ['interactive', 'hands_on']:
                adjusted_score *= 0.8  # Prefer less demanding content
        elif energy_level == 'high':
            if content.get('content_type') in ['interactive', 'hands_on']:
                adjusted_score *= 1.2  # Prefer engaging content
        
        return adjusted_score
    
    def _apply_diversity_filter(
        self, 
        scored_content: List[Dict], 
        target_count: int
    ) -> List[Dict]:
        """Apply diversity filter to avoid too similar recommendations."""
        if len(scored_content) <= target_count:
            return scored_content
        
        diverse_recommendations = []
        used_topics = set()
        used_types = set()
        
        for recommendation in scored_content:
            content = recommendation['content']
            content_topics = set(content.get('topics', []))
            content_type = content.get('content_type', '')
            
            # Check diversity criteria
            topic_overlap = len(content_topics.intersection(used_topics))
            type_used = content_type in used_types
            
            # Add if diverse enough or if we haven't reached minimum count
            if (len(diverse_recommendations) < target_count // 2 or
                (topic_overlap <= 1 and not type_used)):
                
                diverse_recommendations.append(recommendation)
                used_topics.update(content_topics)
                used_types.add(content_type)
                
                if len(diverse_recommendations) >= target_count:
                    break
        
        return diverse_recommendations
    
    def _generate_reasoning(self, user_profile: Dict, content: Dict, score: float) -> Dict:
        """Generate explanation for why content was recommended."""
        reasoning = {
            'primary_reason': '',
            'supporting_factors': [],
            'confidence_level': 'medium'
        }
        
        # Determine primary reason
        learning_style = user_profile.get('primary_learning_style', 'visual')
        content_type = content.get('content_type', 'text')
        
        if self._calculate_style_match_score(learning_style, content_type) > 0.8:
            reasoning['primary_reason'] = f"Matches your {learning_style} learning style"
        
        user_gaps = user_profile.get('knowledge_gaps', [])
        content_topics = content.get('topics', [])
        if any(gap in content_topics for gap in user_gaps):
            reasoning['primary_reason'] = "Addresses your knowledge gaps"
        
        # Add supporting factors
        if content.get('difficulty_level', 0.5) > 0.7:
            reasoning['supporting_factors'].append("Provides appropriate challenge")
        
        if content.get('interactive_elements', 0) > 0:
            reasoning['supporting_factors'].append("Includes interactive elements")
        
        accommodations = user_profile.get('neurodivergent_accommodations', {})
        if accommodations.get('prefers_structure') and content.get('structured', False):
            reasoning['supporting_factors'].append("Well-structured content")
        
        # Set confidence level
        if score > 0.8:
            reasoning['confidence_level'] = 'high'
        elif score > 0.6:
            reasoning['confidence_level'] = 'medium'
        else:
            reasoning['confidence_level'] = 'low'
        
        return reasoning
    
    def _estimate_learning_benefit(self, user_profile: Dict, content: Dict) -> float:
        """Estimate the learning benefit of content for the user."""
        benefit_factors = {
            'gap_coverage': 0.0,
            'skill_advancement': 0.0,
            'retention_improvement': 0.0,
            'engagement_boost': 0.0
        }
        
        # Gap coverage benefit
        user_gaps = user_profile.get('knowledge_gaps', [])
        content_topics = content.get('topics', [])
        if user_gaps and content_topics:
            gap_coverage = len(set(user_gaps).intersection(set(content_topics))) / len(user_gaps)
            benefit_factors['gap_coverage'] = gap_coverage * 0.4
        
        # Skill advancement benefit
        user_level = user_profile.get('current_skill_level', 0.5)
        content_difficulty = content.get('difficulty_level', 0.5)
        if content_difficulty > user_level:
            advancement_potential = min(0.3, content_difficulty - user_level)
            benefit_factors['skill_advancement'] = advancement_potential
        
        # Retention improvement (based on learning style match)
        style_match = self._calculate_style_match_score(
            user_profile.get('primary_learning_style', 'visual'),
            content.get('content_type', 'text')
        )
        benefit_factors['retention_improvement'] = style_match * 0.2
        
        # Engagement boost
        engagement_score = self._predict_engagement_score(user_profile, content)
        benefit_factors['engagement_boost'] = engagement_score * 0.1
        
        total_benefit = sum(benefit_factors.values())
        return min(1.0, total_benefit)
    
    def _calculate_confidence(self, user_profile: Dict, content: Dict) -> float:
        """Calculate confidence in the recommendation."""
        confidence_factors = []
        
        # Data quality factor
        profile_completeness = len([v for v in user_profile.values() if v]) / len(user_profile)
        confidence_factors.append(profile_completeness)
        
        # Content metadata quality
        content_completeness = len([v for v in content.values() if v]) / len(content)
        confidence_factors.append(content_completeness)
        
        # Historical data factor
        user_history_length = len(user_profile.get('completed_content', []))
        history_factor = min(1.0, user_history_length / 10.0)  # Full confidence after 10 items
        confidence_factors.append(history_factor)
        
        return np.mean(confidence_factors)
    
    def _analyze_knowledge_state(self, current_progress: Dict) -> Dict:
        """Analyze user's current knowledge state."""
        knowledge_state = {
            'current_level': 0.5,
            'strong_areas': [],
            'weak_areas': [],
            'learning_velocity': 0.5,
            'retention_rate': 0.7
        }
        
        if not current_progress:
            return knowledge_state
        
        # Calculate overall level
        skill_levels = [p.get('skill_level', 0.5) for p in current_progress.values()]
        knowledge_state['current_level'] = np.mean(skill_levels) if skill_levels else 0.5
        
        # Identify strong and weak areas
        for topic, progress in current_progress.items():
            skill_level = progress.get('skill_level', 0.5)
            if skill_level > 0.7:
                knowledge_state['strong_areas'].append(topic)
            elif skill_level < 0.4:
                knowledge_state['weak_areas'].append(topic)
        
        return knowledge_state
    
    def _identify_priority_areas(
        self, 
        knowledge_state: Dict, 
        learning_goals: List[str], 
        user_profile: Dict
    ) -> List[str]:
        """Identify priority learning areas based on goals and current state."""
        priority_areas = []
        
        # Prioritize weak areas that align with goals
        weak_areas = knowledge_state.get('weak_areas', [])
        goal_aligned_weak = [area for area in weak_areas if area in learning_goals]
        priority_areas.extend(goal_aligned_weak)
        
        # Add other goal areas not yet mastered
        current_strong = knowledge_state.get('strong_areas', [])
        remaining_goals = [goal for goal in learning_goals 
                          if goal not in current_strong and goal not in priority_areas]
        priority_areas.extend(remaining_goals)
        
        # Add foundational areas if user is struggling
        if knowledge_state.get('current_level', 0.5) < 0.4:
            foundational_areas = ['basics', 'fundamentals', 'introduction']
            priority_areas = foundational_areas + priority_areas
        
        return priority_areas[:5]  # Limit to top 5 priorities
    
    def _find_content_for_area(
        self, 
        area: str, 
        difficulty: float, 
        learning_style: str
    ) -> Optional[Dict]:
        """Find appropriate content for a learning area."""
        # In a real implementation, this would query the content database
        # For now, we'll return a mock content item
        return {
            'id': f"content_{area}_{int(difficulty*10)}",
            'title': f"{area.title()} Learning Module",
            'topic': area,
            'difficulty_level': difficulty,
            'content_type': self._get_optimal_content_type_for_style(learning_style),
            'estimated_duration': random.randint(10, 30),
            'objectives': [f"Understand {area}", f"Apply {area} concepts"],
            'interactive_elements': 2 if learning_style == 'kinesthetic' else 1
        }
    
    def _get_optimal_content_type_for_style(self, learning_style: str) -> str:
        """Get optimal content type for learning style."""
        optimal_types = {
            'visual': 'infographic',
            'auditory': 'audio',
            'kinesthetic': 'interactive'
        }
        return optimal_types.get(learning_style, 'text')
    
    def _get_path_adaptations(self, user_profile: Dict, sequence: List[Dict]) -> List[str]:
        """Get adaptations to apply to the learning path."""
        adaptations = []
        
        accommodations = user_profile.get('neurodivergent_accommodations', {})
        
        if accommodations.get('needs_breaks'):
            adaptations.append('break_reminders')
        
        if accommodations.get('needs_extra_time'):
            adaptations.append('extended_timeouts')
        
        if accommodations.get('prefers_structure'):
            adaptations.append('clear_progress_indicators')
        
        learning_style = user_profile.get('primary_learning_style', 'visual')
        adaptations.append(f'{learning_style}_optimized')
        
        return adaptations
    
    def _plan_assessments(self, sequence: List[Dict]) -> List[Dict]:
        """Plan assessment checkpoints for the learning sequence."""
        assessments = []
        
        # Add assessment every 2-3 content items
        for i in range(0, len(sequence), 3):
            assessment = {
                'position': i + 2,  # After 2 content items
                'type': 'formative_assessment',
                'topics': [item.get('topic') for item in sequence[i:i+3]],
                'estimated_time': 5
            }
            assessments.append(assessment)
        
        return assessments
    
    def _calculate_forgetting_probability(
        self, 
        days_since: int, 
        performance_history: List[Dict], 
        topic: str
    ) -> float:
        """Calculate probability of forgetting based on time and performance."""
        # Simplified forgetting curve implementation
        # In reality, this would be more sophisticated
        
        # Base forgetting rate (Ebbinghaus curve approximation)
        base_forgetting = 1 - np.exp(-days_since / 7.0)  # 7-day half-life
        
        # Adjust based on initial learning strength
        topic_performance = [p for p in performance_history if p.get('topic') == topic]
        if topic_performance:
            avg_performance = np.mean([p.get('score', 0.5) for p in topic_performance])
            # Better initial learning reduces forgetting rate
            forgetting_adjustment = 1 - (avg_performance * 0.5)
            adjusted_forgetting = base_forgetting * forgetting_adjustment
        else:
            adjusted_forgetting = base_forgetting
        
        return min(1.0, max(0.0, adjusted_forgetting))
    
    def _get_optimal_review_method(
        self, 
        user_profile: Dict, 
        topic: str, 
        forgetting_prob: float
    ) -> str:
        """Get optimal review method based on user profile and forgetting probability."""
        learning_style = user_profile.get('primary_learning_style', 'visual')
        
        if forgetting_prob > 0.7:  # High forgetting - need intensive review
            methods = {
                'visual': 'interactive_recap',
                'auditory': 'audio_summary',
                'kinesthetic': 'hands_on_practice'
            }
        else:  # Moderate forgetting - lighter review
            methods = {
                'visual': 'visual_summary',
                'auditory': 'brief_audio',
                'kinesthetic': 'quick_exercise'
            }
        
        return methods.get(learning_style, 'mixed_review')
    
    def _estimate_review_time(self, topic: str, forgetting_prob: float) -> int:
        """Estimate time needed for review based on forgetting probability."""
        base_time = 10  # 10 minutes base
        
        if forgetting_prob > 0.7:
            return base_time * 2  # 20 minutes for high forgetting
        elif forgetting_prob > 0.5:
            return int(base_time * 1.5)  # 15 minutes for moderate forgetting
        else:
            return base_time  # 10 minutes for low forgetting
    
    def _update_recommendation_weights(
        self, 
        user_feedback: Dict, 
        actual_performance: Optional[Dict]
    ):
        """Update recommendation weights based on feedback."""
        # Simplified weight adjustment
        # In a real system, this would use more sophisticated ML techniques
        
        feedback_rating = user_feedback.get('rating', 3)  # 1-5 scale
        
        if feedback_rating >= 4:  # Positive feedback
            # Slightly increase weights for factors that led to good recommendation
            adjustment = 0.01
        elif feedback_rating <= 2:  # Negative feedback
            # Slightly decrease weights for factors that led to poor recommendation
            adjustment = -0.01
        else:
            adjustment = 0
        
        # Apply adjustment (simplified - would be more sophisticated in practice)
        for factor in self.weights:
            self.weights[factor] = max(0.05, min(0.5, self.weights[factor] + adjustment))
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        for factor in self.weights:
            self.weights[factor] /= total_weight
    
    def _update_user_profile_from_performance(self, user_id: int, performance: Dict):
        """Update user profile based on actual performance."""
        # This would update the user's profile in the database
        # For now, we'll just store it in memory
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        
        # Update skill level based on performance
        topic = performance.get('topic')
        score = performance.get('score', 0.5)
        
        if topic:
            current_level = self.user_profiles[user_id].get('skill_levels', {}).get(topic, 0.5)
            # Exponential moving average update
            alpha = 0.2
            new_level = (1 - alpha) * current_level + alpha * score
            
            if 'skill_levels' not in self.user_profiles[user_id]:
                self.user_profiles[user_id]['skill_levels'] = {}
            
            self.user_profiles[user_id]['skill_levels'][topic] = new_level
    
    def _get_similar_content_performance(self, user_profile: Dict, content: Dict) -> float:
        """Get user's performance on similar content."""
        # Simplified implementation
        # Would analyze content similarity and user performance in a real system
        return user_profile.get('average_performance', 0.7)