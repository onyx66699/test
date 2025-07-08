// User types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  learning_style?: LearningStyle;
  neurodivergent_accommodations?: NeurodivergentAccommodations;
  created_at: string;
  is_active: boolean;
}

export interface LearningStyle {
  visual: number;
  auditory: number;
  kinesthetic: number;
}

export interface NeurodivergentAccommodations {
  needs_breaks: boolean;
  prefers_structure: boolean;
  sensitive_to_distractions: boolean;
  needs_extra_time: boolean;
  benefits_from_repetition: boolean;
  prefers_clear_instructions: boolean;
}

// Learning content types
export interface LearningContent {
  id: number;
  title: string;
  subject: string;
  topic: string;
  content_type: string;
  difficulty_level: number;
  estimated_duration: number;
  content_data: any;
  learning_objectives: string[];
  prerequisites?: string[];
  tags?: string[];
  accessibility_features?: NeurodivergentAccommodations;
  created_at: string;
  is_active: boolean;
}

export interface Quiz {
  id: number;
  title: string;
  subject: string;
  topic: string;
  difficulty_level: number;
  questions: QuizQuestion[];
  time_limit?: number;
  created_at: string;
}

export interface QuizQuestion {
  id: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay';
  question_text: string;
  options?: string[];
  correct_answer: any;
  explanation: string;
  learning_style_features: string[];
  estimated_time: number;
}

// Progress and session types
export interface LearningProgress {
  topic: string;
  skill_level: number;
  completion_rate: number;
  time_spent: number;
  knowledge_gaps: string[];
  strengths: string[];
  last_accessed?: string;
}

export interface LearningSession {
  id?: number;
  session_type: string;
  content_id: string;
  duration: number;
  performance_score: number;
  engagement_score: number;
  difficulty_level: number;
  adaptations_made?: any;
  feedback_given?: any;
  user_feedback?: any;
}

// Recommendation types
export interface Recommendation {
  content_id: number;
  recommendation_type: string;
  confidence_score: number;
  reasoning: any;
  estimated_benefit: number;
  content_preview: {
    title: string;
    type: string;
    difficulty: number;
    duration: number;
  };
}

export interface RecommendationRequest {
  user_id?: number;
  current_topic?: string;
  session_performance?: number;
  time_available?: number;
  learning_goal?: string;
}

// Analytics types
export interface LearningAnalytics {
  summary: {
    total_sessions: number;
    total_time_minutes: number;
    average_performance: number;
    average_engagement: number;
    time_range_days: number;
  };
  progress_by_topic: Record<string, LearningProgress>;
  learning_patterns: {
    optimal_difficulty_progression: any[];
    best_content_sequence: any[];
    effective_adaptations: any[];
    learning_efficiency_trends: any[];
    engagement_patterns: any;
    performance_predictors: any;
  };
  recommendations: string[];
}

// Adaptation types
export interface AdaptationResult {
  adaptation_applied?: {
    action: string;
    confidence: number;
    expected_benefit: number;
    explanation: string;
    implementation: any;
  };
  result?: {
    action_taken: string;
    changes_made: string[];
  };
  all_recommendations: any[];
}

// Learning path types
export interface LearningPath {
  recommended_sequence: LearningContent[];
  estimated_total_time: number;
  learning_objectives: string[];
  difficulty_progression: number[];
  style_adaptations: string[];
  checkpoint_assessments: any[];
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'performance_update' | 'adaptation_response' | 'heartbeat' | 'heartbeat_response' | 'error';
  data?: any;
  session_id?: string;
  message?: string;
  timestamp: string;
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status_code?: number;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  learning_style?: LearningStyle;
  neurodivergent_accommodations?: NeurodivergentAccommodations;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

// Component prop types
export interface LearningStyleAssessmentProps {
  onComplete: (style: LearningStyle) => void;
}

export interface ContentViewerProps {
  content: LearningContent;
  onProgress: (progress: number) => void;
  onComplete: (session: LearningSession) => void;
}

export interface ProgressDashboardProps {
  analytics: LearningAnalytics;
  onTopicSelect: (topic: string) => void;
}

export interface RecommendationCardProps {
  recommendation: Recommendation;
  onSelect: (contentId: number) => void;
}

// Theme and styling types
export interface ThemeColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
  };
}

export interface LearningStyleTheme {
  visual: ThemeColors;
  auditory: ThemeColors;
  kinesthetic: ThemeColors;
}