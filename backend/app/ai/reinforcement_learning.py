import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random

class AdaptiveLearningAgent:
    """
    Reinforcement Learning agent that optimizes the learning experience
    based on user engagement, performance, and long-term retention.
    """
    
    def __init__(self, learning_rate: float = 0.1, epsilon: float = 0.1, gamma: float = 0.95):
        self.learning_rate = learning_rate
        self.epsilon = epsilon  # Exploration rate
        self.gamma = gamma  # Discount factor
        
        # Q-table for state-action values
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=10000)
        
        # Action space
        self.actions = [
            'increase_difficulty',
            'decrease_difficulty',
            'change_content_type',
            'add_break',
            'provide_hint',
            'show_example',
            'repeat_content',
            'advance_topic',
            'review_previous',
            'gamify_content'
        ]
        
        # State features
        self.state_features = [
            'performance_score',
            'engagement_level',
            'time_spent',
            'difficulty_level',
            'content_type_preference',
            'fatigue_level',
            'knowledge_retention',
            'learning_velocity'
        ]
        
        # Reward components
        self.reward_weights = {
            'performance_improvement': 0.3,
            'engagement_increase': 0.25,
            'retention_improvement': 0.2,
            'efficiency_gain': 0.15,
            'user_satisfaction': 0.1
        }
        
        # Learning statistics
        self.episode_rewards = []
        self.action_counts = defaultdict(int)
        self.state_visits = defaultdict(int)
    
    def get_state_representation(self, user_session: Dict, user_profile: Dict) -> str:
        """
        Convert user session and profile data into a state representation.
        """
        # Extract and normalize features
        features = []
        
        # Performance score (0-1)
        performance = user_session.get('performance_score', 0.5)
        features.append(self._discretize(performance, 5))
        
        # Engagement level (0-1)
        engagement = user_session.get('engagement_score', 0.5)
        features.append(self._discretize(engagement, 5))
        
        # Time spent ratio (actual/expected)
        expected_time = user_session.get('estimated_duration', 600)
        actual_time = user_session.get('duration', 600)
        time_ratio = min(2.0, actual_time / expected_time) if expected_time > 0 else 1.0
        features.append(self._discretize(time_ratio, 4))
        
        # Difficulty level (0-1)
        difficulty = user_session.get('difficulty_level', 0.5)
        features.append(self._discretize(difficulty, 5))
        
        # Content type preference match
        user_style = user_profile.get('primary_learning_style', 'visual')
        content_type = user_session.get('content_type', 'text')
        style_match = self._calculate_style_match(user_style, content_type)
        features.append(self._discretize(style_match, 3))
        
        # Fatigue level (based on session length and time of day)
        fatigue = self._estimate_fatigue_level(user_session, user_profile)
        features.append(self._discretize(fatigue, 3))
        
        # Knowledge retention (based on recent performance)
        retention = self._estimate_retention_level(user_profile)
        features.append(self._discretize(retention, 4))
        
        # Learning velocity (progress rate)
        velocity = self._calculate_learning_velocity(user_profile)
        features.append(self._discretize(velocity, 4))
        
        # Create state string
        state = '_'.join(map(str, features))
        self.state_visits[state] += 1
        
        return state
    
    def select_action(self, state: str, available_actions: Optional[List[str]] = None) -> str:
        """
        Select an action using epsilon-greedy policy with exploration.
        """
        if available_actions is None:
            available_actions = self.actions
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            # Exploration: random action
            action = random.choice(available_actions)
        else:
            # Exploitation: best known action
            q_values = {action: self.q_table[state][action] for action in available_actions}
            action = max(q_values, key=q_values.get)
        
        self.action_counts[action] += 1
        return action
    
    def calculate_reward(
        self,
        previous_session: Dict,
        current_session: Dict,
        action_taken: str,
        user_feedback: Optional[Dict] = None
    ) -> float:
        """
        Calculate reward based on the improvement in learning metrics.
        """
        rewards = {}
        
        # Performance improvement reward
        prev_performance = previous_session.get('performance_score', 0.5)
        curr_performance = current_session.get('performance_score', 0.5)
        performance_delta = curr_performance - prev_performance
        rewards['performance_improvement'] = self._sigmoid_reward(performance_delta, scale=2.0)
        
        # Engagement improvement reward
        prev_engagement = previous_session.get('engagement_score', 0.5)
        curr_engagement = current_session.get('engagement_score', 0.5)
        engagement_delta = curr_engagement - prev_engagement
        rewards['engagement_increase'] = self._sigmoid_reward(engagement_delta, scale=2.0)
        
        # Efficiency reward (learning per unit time)
        prev_efficiency = self._calculate_efficiency(previous_session)
        curr_efficiency = self._calculate_efficiency(current_session)
        efficiency_delta = curr_efficiency - prev_efficiency
        rewards['efficiency_gain'] = self._sigmoid_reward(efficiency_delta, scale=1.0)
        
        # Retention reward (based on spaced repetition performance)
        retention_reward = self._calculate_retention_reward(current_session)
        rewards['retention_improvement'] = retention_reward
        
        # User satisfaction reward
        if user_feedback:
            satisfaction = user_feedback.get('rating', 3) / 5.0  # Normalize to 0-1
            rewards['user_satisfaction'] = satisfaction
        else:
            # Estimate satisfaction from engagement and performance
            estimated_satisfaction = (curr_engagement + curr_performance) / 2.0
            rewards['user_satisfaction'] = estimated_satisfaction
        
        # Calculate weighted total reward
        total_reward = sum(
            rewards[component] * self.reward_weights[component]
            for component in rewards
        )
        
        # Add action-specific bonuses/penalties
        total_reward += self._get_action_specific_reward(action_taken, current_session)
        
        return total_reward
    
    def update_q_value(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        done: bool = False
    ):
        """
        Update Q-value using Q-learning algorithm.
        """
        current_q = self.q_table[state][action]
        
        if done:
            # Terminal state
            max_next_q = 0
        else:
            # Find maximum Q-value for next state
            next_q_values = [self.q_table[next_state][a] for a in self.actions]
            max_next_q = max(next_q_values) if next_q_values else 0
        
        # Q-learning update rule
        new_q = current_q + self.learning_rate * (
            reward + self.gamma * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
        
        # Store experience for replay
        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'timestamp': datetime.now().isoformat()
        }
        self.experience_buffer.append(experience)
    
    def experience_replay(self, batch_size: int = 32):
        """
        Perform experience replay to improve learning stability.
        """
        if len(self.experience_buffer) < batch_size:
            return
        
        # Sample random batch from experience buffer
        batch = random.sample(list(self.experience_buffer), batch_size)
        
        for experience in batch:
            state = experience['state']
            action = experience['action']
            reward = experience['reward']
            next_state = experience['next_state']
            done = experience['done']
            
            # Update Q-value with reduced learning rate for replay
            current_q = self.q_table[state][action]
            
            if done:
                max_next_q = 0
            else:
                next_q_values = [self.q_table[next_state][a] for a in self.actions]
                max_next_q = max(next_q_values) if next_q_values else 0
            
            # Use reduced learning rate for experience replay
            replay_lr = self.learning_rate * 0.5
            new_q = current_q + replay_lr * (
                reward + self.gamma * max_next_q - current_q
            )
            
            self.q_table[state][action] = new_q
    
    def adapt_learning_parameters(self, episode_reward: float):
        """
        Adapt learning parameters based on performance.
        """
        self.episode_rewards.append(episode_reward)
        
        # Decay epsilon (exploration rate) over time
        min_epsilon = 0.01
        decay_rate = 0.995
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)
        
        # Adjust learning rate based on recent performance
        if len(self.episode_rewards) >= 10:
            recent_rewards = self.episode_rewards[-10:]
            avg_recent_reward = np.mean(recent_rewards)
            
            if avg_recent_reward > 0.7:  # Good performance
                self.learning_rate *= 0.99  # Slightly reduce learning rate
            elif avg_recent_reward < 0.3:  # Poor performance
                self.learning_rate *= 1.01  # Slightly increase learning rate
            
            # Keep learning rate in reasonable bounds
            self.learning_rate = max(0.01, min(0.3, self.learning_rate))
    
    def get_adaptation_recommendations(
        self,
        current_state: str,
        user_session: Dict,
        user_profile: Dict
    ) -> List[Dict]:
        """
        Get ranked adaptation recommendations based on Q-values.
        """
        recommendations = []
        
        # Get Q-values for all actions in current state
        action_values = [(action, self.q_table[current_state][action]) 
                        for action in self.actions]
        
        # Sort by Q-value (descending)
        action_values.sort(key=lambda x: x[1], reverse=True)
        
        # Create recommendations with explanations
        for action, q_value in action_values[:5]:  # Top 5 recommendations
            recommendation = {
                'action': action,
                'confidence': self._normalize_confidence(q_value),
                'expected_benefit': q_value,
                'explanation': self._get_action_explanation(action, user_session, user_profile),
                'implementation': self._get_action_implementation(action, user_session)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_learning_patterns(self, user_id: int, session_history: List[Dict]) -> Dict:
        """
        Analyze learning patterns to identify optimization opportunities.
        """
        analysis = {
            'optimal_difficulty_progression': [],
            'best_content_sequence': [],
            'effective_adaptations': [],
            'learning_efficiency_trends': [],
            'engagement_patterns': {},
            'performance_predictors': {}
        }
        
        if not session_history:
            return analysis
        
        # Analyze difficulty progression
        analysis['optimal_difficulty_progression'] = self._analyze_difficulty_progression(
            session_history
        )
        
        # Analyze content sequencing
        analysis['best_content_sequence'] = self._analyze_content_sequencing(
            session_history
        )
        
        # Identify effective adaptations
        analysis['effective_adaptations'] = self._identify_effective_adaptations(
            session_history
        )
        
        # Analyze learning efficiency trends
        analysis['learning_efficiency_trends'] = self._analyze_efficiency_trends(
            session_history
        )
        
        # Analyze engagement patterns
        analysis['engagement_patterns'] = self._analyze_engagement_patterns(
            session_history
        )
        
        # Identify performance predictors
        analysis['performance_predictors'] = self._identify_performance_predictors(
            session_history
        )
        
        return analysis
    
    def _discretize(self, value: float, bins: int) -> int:
        """Discretize continuous value into bins."""
        return min(bins - 1, int(value * bins))
    
    def _calculate_style_match(self, user_style: str, content_type: str) -> float:
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
    
    def _estimate_fatigue_level(self, session: Dict, profile: Dict) -> float:
        """Estimate user fatigue level."""
        session_duration = session.get('duration', 0) / 60  # Convert to minutes
        
        # Base fatigue increases with session length
        base_fatigue = min(1.0, session_duration / 60)  # 1 hour = full fatigue
        
        # Adjust based on user accommodations
        accommodations = profile.get('neurodivergent_accommodations', {})
        if accommodations.get('needs_breaks'):
            base_fatigue *= 1.5  # Higher fatigue sensitivity
        
        return base_fatigue
    
    def _estimate_retention_level(self, profile: Dict) -> float:
        """Estimate knowledge retention level."""
        # Simplified retention estimation
        # In practice, this would use spaced repetition algorithms
        recent_performance = profile.get('recent_performance', [])
        if recent_performance:
            return np.mean([p.get('score', 0.5) for p in recent_performance[-5:]])
        return 0.7  # Default retention
    
    def _calculate_learning_velocity(self, profile: Dict) -> float:
        """Calculate learning velocity (progress rate)."""
        progress_history = profile.get('progress_history', [])
        if len(progress_history) < 2:
            return 0.5  # Default velocity
        
        # Calculate rate of skill level improvement
        recent_progress = progress_history[-5:]  # Last 5 sessions
        if len(recent_progress) >= 2:
            start_level = recent_progress[0].get('skill_level', 0.5)
            end_level = recent_progress[-1].get('skill_level', 0.5)
            velocity = (end_level - start_level) / len(recent_progress)
            return max(0, min(1, velocity + 0.5))  # Normalize to 0-1
        
        return 0.5
    
    def _sigmoid_reward(self, delta: float, scale: float = 1.0) -> float:
        """Apply sigmoid function to normalize reward."""
        return 1 / (1 + np.exp(-delta * scale))
    
    def _calculate_efficiency(self, session: Dict) -> float:
        """Calculate learning efficiency (performance per unit time)."""
        performance = session.get('performance_score', 0.5)
        duration = session.get('duration', 600) / 60  # Convert to minutes
        
        if duration == 0:
            return 0
        
        # Efficiency = performance / time, normalized
        efficiency = performance / max(1, duration / 30)  # 30 minutes as baseline
        return min(1.0, efficiency)
    
    def _calculate_retention_reward(self, session: Dict) -> float:
        """Calculate reward based on retention performance."""
        # Check if this is a review session
        if session.get('session_type') == 'review':
            performance = session.get('performance_score', 0.5)
            # Higher reward for good performance on review material
            return performance * 1.2
        
        return 0.5  # Neutral reward for non-review sessions
    
    def _get_action_specific_reward(self, action: str, session: Dict) -> float:
        """Get action-specific reward bonuses/penalties."""
        action_rewards = {
            'increase_difficulty': 0.1 if session.get('performance_score', 0.5) > 0.8 else -0.1,
            'decrease_difficulty': 0.1 if session.get('performance_score', 0.5) < 0.4 else -0.1,
            'add_break': 0.05 if session.get('duration', 0) > 1800 else 0,  # 30+ minutes
            'provide_hint': 0.05 if session.get('performance_score', 0.5) < 0.6 else 0,
            'gamify_content': 0.1 if session.get('engagement_score', 0.5) < 0.5 else 0
        }
        
        return action_rewards.get(action, 0)
    
    def _normalize_confidence(self, q_value: float) -> float:
        """Normalize Q-value to confidence score."""
        # Simple normalization - in practice, this would be more sophisticated
        return max(0, min(1, (q_value + 1) / 2))
    
    def _get_action_explanation(self, action: str, session: Dict, profile: Dict) -> str:
        """Get human-readable explanation for an action."""
        explanations = {
            'increase_difficulty': "User is performing well and ready for more challenge",
            'decrease_difficulty': "User is struggling and needs easier content",
            'change_content_type': f"Switch to {profile.get('primary_learning_style', 'visual')} content",
            'add_break': "User may be experiencing fatigue",
            'provide_hint': "User needs additional guidance",
            'show_example': "Concrete examples will help understanding",
            'repeat_content': "Repetition will improve retention",
            'advance_topic': "User has mastered current topic",
            'review_previous': "Previous concepts need reinforcement",
            'gamify_content': "Gamification will increase engagement"
        }
        
        return explanations.get(action, "Recommended based on learning patterns")
    
    def _get_action_implementation(self, action: str, session: Dict) -> Dict:
        """Get implementation details for an action."""
        implementations = {
            'increase_difficulty': {
                'type': 'difficulty_adjustment',
                'parameters': {'difficulty_delta': 0.1}
            },
            'decrease_difficulty': {
                'type': 'difficulty_adjustment',
                'parameters': {'difficulty_delta': -0.1}
            },
            'change_content_type': {
                'type': 'content_adaptation',
                'parameters': {'new_type': 'visual'}
            },
            'add_break': {
                'type': 'session_management',
                'parameters': {'break_duration': 300}  # 5 minutes
            },
            'provide_hint': {
                'type': 'assistance',
                'parameters': {'hint_level': 'moderate'}
            },
            'gamify_content': {
                'type': 'engagement_boost',
                'parameters': {'gamification_elements': ['points', 'progress_bar']}
            }
        }
        
        return implementations.get(action, {'type': 'general', 'parameters': {}})
    
    def _analyze_difficulty_progression(self, sessions: List[Dict]) -> List[Dict]:
        """Analyze optimal difficulty progression patterns."""
        progression_analysis = []
        
        for i in range(1, len(sessions)):
            prev_session = sessions[i-1]
            curr_session = sessions[i]
            
            difficulty_change = (
                curr_session.get('difficulty_level', 0.5) - 
                prev_session.get('difficulty_level', 0.5)
            )
            
            performance_change = (
                curr_session.get('performance_score', 0.5) - 
                prev_session.get('performance_score', 0.5)
            )
            
            progression_analysis.append({
                'difficulty_change': difficulty_change,
                'performance_change': performance_change,
                'effectiveness': performance_change / max(0.1, abs(difficulty_change))
            })
        
        return progression_analysis
    
    def _analyze_content_sequencing(self, sessions: List[Dict]) -> List[Dict]:
        """Analyze effective content sequencing patterns."""
        sequences = []
        
        for i in range(len(sessions) - 2):
            sequence = {
                'content_types': [
                    sessions[i].get('content_type'),
                    sessions[i+1].get('content_type'),
                    sessions[i+2].get('content_type')
                ],
                'performance_trend': [
                    sessions[i].get('performance_score', 0.5),
                    sessions[i+1].get('performance_score', 0.5),
                    sessions[i+2].get('performance_score', 0.5)
                ],
                'effectiveness': np.mean([
                    sessions[i+1].get('performance_score', 0.5),
                    sessions[i+2].get('performance_score', 0.5)
                ])
            }
            sequences.append(sequence)
        
        return sequences
    
    def _identify_effective_adaptations(self, sessions: List[Dict]) -> List[Dict]:
        """Identify which adaptations were most effective."""
        effective_adaptations = []
        
        for session in sessions:
            adaptations = session.get('adaptations_made', [])
            performance = session.get('performance_score', 0.5)
            engagement = session.get('engagement_score', 0.5)
            
            if adaptations:
                effectiveness = (performance + engagement) / 2
                effective_adaptations.append({
                    'adaptations': adaptations,
                    'effectiveness': effectiveness,
                    'session_id': session.get('id')
                })
        
        # Sort by effectiveness
        effective_adaptations.sort(key=lambda x: x['effectiveness'], reverse=True)
        
        return effective_adaptations[:10]  # Top 10 most effective
    
    def _analyze_efficiency_trends(self, sessions: List[Dict]) -> List[Dict]:
        """Analyze learning efficiency trends over time."""
        efficiency_trends = []
        
        for session in sessions:
            efficiency = self._calculate_efficiency(session)
            efficiency_trends.append({
                'timestamp': session.get('created_at'),
                'efficiency': efficiency,
                'session_type': session.get('session_type'),
                'content_type': session.get('content_type')
            })
        
        return efficiency_trends
    
    def _analyze_engagement_patterns(self, sessions: List[Dict]) -> Dict:
        """Analyze engagement patterns across different conditions."""
        patterns = {
            'by_content_type': defaultdict(list),
            'by_difficulty': defaultdict(list),
            'by_time_of_day': defaultdict(list),
            'by_session_length': defaultdict(list)
        }
        
        for session in sessions:
            engagement = session.get('engagement_score', 0.5)
            
            # By content type
            content_type = session.get('content_type', 'unknown')
            patterns['by_content_type'][content_type].append(engagement)
            
            # By difficulty
            difficulty = session.get('difficulty_level', 0.5)
            difficulty_bin = 'easy' if difficulty < 0.4 else 'medium' if difficulty < 0.7 else 'hard'
            patterns['by_difficulty'][difficulty_bin].append(engagement)
            
            # By session length
            duration = session.get('duration', 0) / 60  # minutes
            length_bin = 'short' if duration < 15 else 'medium' if duration < 45 else 'long'
            patterns['by_session_length'][length_bin].append(engagement)
        
        # Calculate averages
        for category in patterns:
            for subcategory in patterns[category]:
                values = patterns[category][subcategory]
                patterns[category][subcategory] = {
                    'average': np.mean(values),
                    'count': len(values),
                    'std': np.std(values)
                }
        
        return dict(patterns)
    
    def _identify_performance_predictors(self, sessions: List[Dict]) -> Dict:
        """Identify factors that predict good performance."""
        predictors = {
            'strong_predictors': [],
            'weak_predictors': [],
            'correlations': {}
        }
        
        if len(sessions) < 5:
            return predictors
        
        # Extract features and performance scores
        features = []
        performances = []
        
        for session in sessions:
            session_features = [
                session.get('difficulty_level', 0.5),
                session.get('duration', 600) / 600,  # Normalize to 10 minutes
                1 if session.get('content_type') == 'interactive' else 0,
                session.get('engagement_score', 0.5)
            ]
            features.append(session_features)
            performances.append(session.get('performance_score', 0.5))
        
        # Calculate correlations (simplified)
        features_array = np.array(features)
        performances_array = np.array(performances)
        
        feature_names = ['difficulty', 'duration', 'interactive_content', 'engagement']
        
        for i, feature_name in enumerate(feature_names):
            correlation = np.corrcoef(features_array[:, i], performances_array)[0, 1]
            predictors['correlations'][feature_name] = correlation
            
            if abs(correlation) > 0.5:
                predictors['strong_predictors'].append({
                    'feature': feature_name,
                    'correlation': correlation
                })
            elif abs(correlation) > 0.3:
                predictors['weak_predictors'].append({
                    'feature': feature_name,
                    'correlation': correlation
                })
        
        return predictors