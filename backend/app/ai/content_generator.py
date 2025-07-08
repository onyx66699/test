import random
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

class ContentGenerator:
    """
    Generates personalized learning content, quizzes, and exercises
    based on user's learning style and progress.
    """
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        self.content_templates = self._load_content_templates()
        self.difficulty_adjusters = self._load_difficulty_adjusters()
    
    def generate_personalized_quiz(
        self, 
        topic: str, 
        difficulty: float, 
        learning_style: str,
        user_knowledge: Dict,
        num_questions: int = 10
    ) -> Dict:
        """
        Generate a personalized quiz based on user's learning style and knowledge gaps.
        """
        quiz = {
            'title': f"Personalized {topic} Quiz",
            'topic': topic,
            'difficulty_level': difficulty,
            'learning_style_adapted': learning_style,
            'questions': [],
            'estimated_time': num_questions * 2,  # 2 minutes per question
            'adaptive_parameters': {
                'difficulty_adjustment': True,
                'style_adaptation': True,
                'knowledge_gap_focus': True
            }
        }
        
        # Generate questions based on knowledge gaps
        knowledge_gaps = user_knowledge.get('gaps', [])
        strengths = user_knowledge.get('strengths', [])
        
        questions = []
        
        # 60% questions on knowledge gaps, 40% on review/reinforcement
        gap_questions = int(num_questions * 0.6)
        review_questions = num_questions - gap_questions
        
        # Generate gap-focused questions
        for i in range(gap_questions):
            if knowledge_gaps:
                gap_topic = random.choice(knowledge_gaps)
                question = self._generate_question(
                    gap_topic, difficulty, learning_style, 'gap'
                )
                questions.append(question)
        
        # Generate review questions
        for i in range(review_questions):
            review_topic = topic
            if strengths:
                review_topic = random.choice(strengths)
            question = self._generate_question(
                review_topic, difficulty * 0.8, learning_style, 'review'
            )
            questions.append(question)
        
        # Shuffle questions
        random.shuffle(questions)
        quiz['questions'] = questions
        
        return quiz
    
    def generate_adaptive_exercise(
        self,
        topic: str,
        learning_style: str,
        difficulty: float,
        time_available: int,  # minutes
        user_accommodations: Dict
    ) -> Dict:
        """
        Generate an adaptive exercise tailored to learning style and accommodations.
        """
        exercise = {
            'title': f"Adaptive {topic} Exercise",
            'topic': topic,
            'learning_style': learning_style,
            'difficulty_level': difficulty,
            'estimated_duration': time_available,
            'accommodations_applied': [],
            'content': {},
            'instructions': [],
            'success_criteria': {},
            'adaptive_features': {}
        }
        
        # Apply learning style adaptations
        if learning_style == 'visual':
            exercise['content'] = self._create_visual_exercise(topic, difficulty)
            exercise['accommodations_applied'].append('visual_elements')
        elif learning_style == 'auditory':
            exercise['content'] = self._create_auditory_exercise(topic, difficulty)
            exercise['accommodations_applied'].append('audio_elements')
        elif learning_style == 'kinesthetic':
            exercise['content'] = self._create_kinesthetic_exercise(topic, difficulty)
            exercise['accommodations_applied'].append('interactive_elements')
        
        # Apply neurodivergent accommodations
        if user_accommodations.get('needs_breaks'):
            exercise['adaptive_features']['break_reminders'] = True
            exercise['accommodations_applied'].append('break_reminders')
        
        if user_accommodations.get('needs_extra_time'):
            exercise['estimated_duration'] = int(exercise['estimated_duration'] * 1.5)
            exercise['accommodations_applied'].append('extended_time')
        
        if user_accommodations.get('prefers_clear_instructions'):
            exercise['instructions'] = self._create_clear_instructions(exercise['content'])
            exercise['accommodations_applied'].append('clear_instructions')
        
        if user_accommodations.get('benefits_from_repetition'):
            exercise['adaptive_features']['repetition_opportunities'] = True
            exercise['accommodations_applied'].append('repetition_support')
        
        return exercise
    
    def generate_personalized_content(
        self,
        topic: str,
        learning_objectives: List[str],
        learning_style: str,
        difficulty: float,
        user_background: Dict
    ) -> Dict:
        """
        Generate personalized learning content based on user profile.
        """
        content = {
            'title': f"Personalized {topic} Content",
            'topic': topic,
            'learning_objectives': learning_objectives,
            'difficulty_level': difficulty,
            'learning_style_adapted': learning_style,
            'sections': [],
            'interactive_elements': [],
            'assessment_checkpoints': [],
            'personalization_notes': []
        }
        
        # Create content sections based on learning objectives
        for i, objective in enumerate(learning_objectives):
            section = self._create_content_section(
                objective, learning_style, difficulty, user_background
            )
            content['sections'].append(section)
            
            # Add assessment checkpoint every 2-3 sections
            if (i + 1) % 2 == 0:
                checkpoint = self._create_assessment_checkpoint(
                    objective, difficulty, learning_style
                )
                content['assessment_checkpoints'].append(checkpoint)
        
        # Add interactive elements based on learning style
        content['interactive_elements'] = self._create_interactive_elements(
            topic, learning_style, difficulty
        )
        
        return content
    
    def adapt_content_difficulty(
        self,
        content: Dict,
        user_performance: float,
        target_performance: float = 0.7
    ) -> Dict:
        """
        Dynamically adjust content difficulty based on user performance.
        """
        adapted_content = content.copy()
        
        # Calculate difficulty adjustment
        performance_diff = user_performance - target_performance
        
        if performance_diff > 0.2:  # User performing well, increase difficulty
            difficulty_adjustment = 0.1
            adaptation_note = "Increased difficulty due to strong performance"
        elif performance_diff < -0.2:  # User struggling, decrease difficulty
            difficulty_adjustment = -0.1
            adaptation_note = "Decreased difficulty to support learning"
        else:
            difficulty_adjustment = 0
            adaptation_note = "Maintained current difficulty level"
        
        # Apply difficulty adjustment
        new_difficulty = max(0.1, min(1.0, content['difficulty_level'] + difficulty_adjustment))
        adapted_content['difficulty_level'] = new_difficulty
        
        # Adjust content based on new difficulty
        if difficulty_adjustment != 0:
            adapted_content = self._apply_difficulty_adjustment(
                adapted_content, difficulty_adjustment
            )
            adapted_content.setdefault('adaptation_history', []).append({
                'timestamp': datetime.now().isoformat(),
                'adjustment': difficulty_adjustment,
                'reason': adaptation_note,
                'user_performance': user_performance
            })
        
        return adapted_content
    
    def _generate_question(
        self, 
        topic: str, 
        difficulty: float, 
        learning_style: str, 
        question_type: str
    ) -> Dict:
        """Generate a single question based on parameters."""
        templates = self.question_templates.get(learning_style, {})
        template = random.choice(templates.get(question_type, [templates.get('default', [{}])[0]]))
        
        question = {
            'id': f"q_{random.randint(1000, 9999)}",
            'type': template.get('type', 'multiple_choice'),
            'topic': topic,
            'difficulty': difficulty,
            'question_text': template.get('text', '').format(topic=topic),
            'options': self._generate_options(topic, template.get('type', 'multiple_choice')),
            'correct_answer': None,
            'explanation': f"This question tests your understanding of {topic}.",
            'learning_style_features': self._get_style_features(learning_style),
            'estimated_time': 120  # 2 minutes
        }
        
        # Set correct answer
        if question['type'] == 'multiple_choice':
            question['correct_answer'] = 0  # First option is correct
        
        return question
    
    def _create_visual_exercise(self, topic: str, difficulty: float) -> Dict:
        """Create exercise optimized for visual learners."""
        return {
            'type': 'visual_exercise',
            'elements': [
                {
                    'type': 'diagram',
                    'title': f"{topic} Concept Map",
                    'interactive': True,
                    'description': f"Complete the concept map for {topic}"
                },
                {
                    'type': 'chart_analysis',
                    'title': f"{topic} Data Visualization",
                    'task': "Analyze the chart and answer questions"
                },
                {
                    'type': 'visual_matching',
                    'title': "Match Concepts",
                    'task': f"Match {topic} concepts with their visual representations"
                }
            ],
            'visual_aids': ['colors', 'icons', 'spatial_organization'],
            'completion_criteria': 'All visual elements correctly identified and connected'
        }
    
    def _create_auditory_exercise(self, topic: str, difficulty: float) -> Dict:
        """Create exercise optimized for auditory learners."""
        return {
            'type': 'auditory_exercise',
            'elements': [
                {
                    'type': 'audio_lecture',
                    'title': f"{topic} Audio Explanation",
                    'duration': 300,  # 5 minutes
                    'interactive': True
                },
                {
                    'type': 'discussion_prompt',
                    'title': "Explain Your Understanding",
                    'task': f"Record yourself explaining {topic} concepts"
                },
                {
                    'type': 'audio_quiz',
                    'title': "Listen and Respond",
                    'task': "Answer questions based on audio content"
                }
            ],
            'audio_features': ['narration', 'sound_effects', 'music'],
            'completion_criteria': 'All audio content reviewed and responses recorded'
        }
    
    def _create_kinesthetic_exercise(self, topic: str, difficulty: float) -> Dict:
        """Create exercise optimized for kinesthetic learners."""
        return {
            'type': 'kinesthetic_exercise',
            'elements': [
                {
                    'type': 'simulation',
                    'title': f"{topic} Interactive Simulation",
                    'hands_on': True,
                    'task': f"Manipulate variables to understand {topic}"
                },
                {
                    'type': 'building_activity',
                    'title': "Construct Your Understanding",
                    'task': f"Build a model or representation of {topic} concepts"
                },
                {
                    'type': 'movement_based',
                    'title': "Physical Learning Activity",
                    'task': "Use physical movements to demonstrate concepts"
                }
            ],
            'interactive_features': ['drag_drop', 'manipulation', 'construction'],
            'completion_criteria': 'All interactive elements successfully completed'
        }
    
    def _create_content_section(
        self, 
        objective: str, 
        learning_style: str, 
        difficulty: float, 
        user_background: Dict
    ) -> Dict:
        """Create a content section for a learning objective."""
        section = {
            'objective': objective,
            'content_type': self._get_optimal_content_type(learning_style),
            'difficulty': difficulty,
            'estimated_time': 10,  # 10 minutes
            'content': {
                'introduction': f"In this section, you will learn about {objective}.",
                'main_content': self._generate_main_content(objective, learning_style),
                'examples': self._generate_examples(objective, difficulty),
                'summary': f"Key takeaways about {objective}."
            },
            'learning_style_adaptations': self._get_style_adaptations(learning_style)
        }
        
        return section
    
    def _load_question_templates(self) -> Dict:
        """Load question templates for different learning styles."""
        return {
            'visual': {
                'gap': [
                    {
                        'type': 'multiple_choice',
                        'text': 'Looking at this diagram about {topic}, what is the missing component?'
                    },
                    {
                        'type': 'image_analysis',
                        'text': 'Analyze this visual representation of {topic} and identify the key elements.'
                    }
                ],
                'review': [
                    {
                        'type': 'multiple_choice',
                        'text': 'Which visual best represents the concept of {topic}?'
                    }
                ]
            },
            'auditory': {
                'gap': [
                    {
                        'type': 'multiple_choice',
                        'text': 'Listen to this explanation of {topic}. What is the main point?'
                    }
                ],
                'review': [
                    {
                        'type': 'audio_response',
                        'text': 'Explain {topic} in your own words.'
                    }
                ]
            },
            'kinesthetic': {
                'gap': [
                    {
                        'type': 'interactive',
                        'text': 'Use this simulation to demonstrate your understanding of {topic}.'
                    }
                ],
                'review': [
                    {
                        'type': 'hands_on',
                        'text': 'Complete this hands-on activity related to {topic}.'
                    }
                ]
            }
        }
    
    def _load_content_templates(self) -> Dict:
        """Load content templates for different learning styles."""
        return {
            'visual': {
                'structure': ['diagram', 'infographic', 'chart', 'timeline'],
                'features': ['colors', 'icons', 'spatial_layout', 'visual_hierarchy']
            },
            'auditory': {
                'structure': ['narration', 'discussion', 'explanation', 'story'],
                'features': ['audio_clips', 'rhythm', 'verbal_emphasis', 'sound_cues']
            },
            'kinesthetic': {
                'structure': ['simulation', 'experiment', 'building', 'manipulation'],
                'features': ['interactivity', 'movement', 'touch', 'physical_metaphors']
            }
        }
    
    def _load_difficulty_adjusters(self) -> Dict:
        """Load difficulty adjustment strategies."""
        return {
            'increase': {
                'vocabulary': 'use_advanced_terms',
                'concepts': 'add_complexity',
                'examples': 'use_abstract_examples',
                'questions': 'add_multi_step_reasoning'
            },
            'decrease': {
                'vocabulary': 'use_simple_terms',
                'concepts': 'break_into_steps',
                'examples': 'use_concrete_examples',
                'questions': 'provide_more_guidance'
            }
        }
    
    def _generate_options(self, topic: str, question_type: str) -> List[str]:
        """Generate answer options for questions."""
        if question_type == 'multiple_choice':
            return [
                f"Correct answer about {topic}",
                f"Plausible but incorrect option 1",
                f"Plausible but incorrect option 2",
                f"Obviously incorrect option"
            ]
        return []
    
    def _get_style_features(self, learning_style: str) -> List[str]:
        """Get features that enhance the question for specific learning style."""
        features = {
            'visual': ['diagram', 'color_coding', 'visual_cues'],
            'auditory': ['audio_narration', 'sound_effects', 'verbal_cues'],
            'kinesthetic': ['interactive_elements', 'drag_drop', 'manipulation']
        }
        return features.get(learning_style, [])
    
    def _get_optimal_content_type(self, learning_style: str) -> str:
        """Get the optimal content type for a learning style."""
        content_types = {
            'visual': 'interactive_infographic',
            'auditory': 'narrated_presentation',
            'kinesthetic': 'hands_on_simulation'
        }
        return content_types.get(learning_style, 'mixed_media')
    
    def _generate_main_content(self, objective: str, learning_style: str) -> str:
        """Generate main content based on objective and learning style."""
        return f"Detailed explanation of {objective} optimized for {learning_style} learners."
    
    def _generate_examples(self, objective: str, difficulty: float) -> List[str]:
        """Generate examples based on objective and difficulty."""
        num_examples = 2 if difficulty < 0.5 else 3
        return [f"Example {i+1} for {objective}" for i in range(num_examples)]
    
    def _get_style_adaptations(self, learning_style: str) -> List[str]:
        """Get adaptations for specific learning style."""
        adaptations = {
            'visual': ['visual_organizers', 'color_coding', 'diagrams'],
            'auditory': ['audio_narration', 'discussion_prompts', 'verbal_summaries'],
            'kinesthetic': ['interactive_elements', 'hands_on_activities', 'movement']
        }
        return adaptations.get(learning_style, [])
    
    def _create_assessment_checkpoint(
        self, 
        objective: str, 
        difficulty: float, 
        learning_style: str
    ) -> Dict:
        """Create an assessment checkpoint."""
        return {
            'type': 'quick_check',
            'objective': objective,
            'questions': [
                self._generate_question(objective, difficulty, learning_style, 'review')
            ],
            'passing_score': 0.7,
            'adaptive': True
        }
    
    def _create_interactive_elements(
        self, 
        topic: str, 
        learning_style: str, 
        difficulty: float
    ) -> List[Dict]:
        """Create interactive elements for content."""
        elements = []
        
        if learning_style == 'visual':
            elements.extend([
                {'type': 'interactive_diagram', 'topic': topic},
                {'type': 'visual_quiz', 'difficulty': difficulty}
            ])
        elif learning_style == 'auditory':
            elements.extend([
                {'type': 'audio_explanation', 'topic': topic},
                {'type': 'discussion_forum', 'topic': topic}
            ])
        elif learning_style == 'kinesthetic':
            elements.extend([
                {'type': 'simulation', 'topic': topic},
                {'type': 'hands_on_exercise', 'difficulty': difficulty}
            ])
        
        return elements
    
    def _apply_difficulty_adjustment(self, content: Dict, adjustment: float) -> Dict:
        """Apply difficulty adjustment to content."""
        adjusted_content = content.copy()
        
        if adjustment > 0:  # Increase difficulty
            adjusted_content['complexity_level'] = 'advanced'
            adjusted_content['guidance_level'] = 'minimal'
        else:  # Decrease difficulty
            adjusted_content['complexity_level'] = 'basic'
            adjusted_content['guidance_level'] = 'extensive'
        
        return adjusted_content
    
    def _create_clear_instructions(self, content: Dict) -> List[str]:
        """Create clear, step-by-step instructions."""
        return [
            "Step 1: Read through the content carefully",
            "Step 2: Complete each interactive element",
            "Step 3: Check your understanding with the quiz",
            "Step 4: Review any areas where you need more practice"
        ]