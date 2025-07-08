import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  User,
  LoginCredentials,
  RegisterData,
  AuthToken,
  LearningContent,
  Recommendation,
  RecommendationRequest,
  LearningSession,
  LearningAnalytics,
  LearningProgress,
  AdaptationResult,
  LearningPath
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:12000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response: AxiosResponse<AuthToken> = await this.api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  }

  async register(userData: RegisterData): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }

  // Learning style analysis
  async analyzeLearningStyle(userId: number): Promise<any> {
    const response = await this.api.get(`/learning/style-analysis/${userId}`);
    return response.data;
  }

  // Content generation
  async generatePersonalizedContent(
    topic: string,
    contentType: string = 'auto',
    difficulty?: number
  ): Promise<any> {
    const params: any = { topic, content_type: contentType };
    if (difficulty !== undefined) {
      params.difficulty = difficulty;
    }

    const response = await this.api.post('/learning/generate-content', null, { params });
    return response.data;
  }

  // Recommendations
  async getRecommendations(request: RecommendationRequest): Promise<Recommendation[]> {
    const response: AxiosResponse<Recommendation[]> = await this.api.post(
      '/learning/recommendations',
      request
    );
    return response.data;
  }

  // Session recording
  async recordLearningSession(sessionData: LearningSession): Promise<any> {
    const response = await this.api.post('/learning/session/record', sessionData);
    return response.data;
  }

  // Analytics
  async getLearningAnalytics(timeRange: number = 30): Promise<LearningAnalytics> {
    const response: AxiosResponse<LearningAnalytics> = await this.api.get(
      `/learning/analytics?time_range=${timeRange}`
    );
    return response.data;
  }

  // Real-time adaptation
  async adaptContentRealtime(
    sessionId: string,
    performanceData: any,
    userFeedback?: any
  ): Promise<AdaptationResult> {
    const response: AxiosResponse<AdaptationResult> = await this.api.post(
      '/learning/adapt-realtime',
      {
        session_id: sessionId,
        performance_data: performanceData,
        user_feedback: userFeedback,
      }
    );
    return response.data;
  }

  // Progress tracking
  async getTopicProgress(topic: string): Promise<LearningProgress> {
    const response: AxiosResponse<LearningProgress> = await this.api.get(
      `/learning/progress/${topic}`
    );
    return response.data;
  }

  // Learning path
  async getLearningPath(
    learningGoals: string[],
    timeAvailable: number = 60
  ): Promise<LearningPath> {
    const goalsString = learningGoals.join(',');
    const response: AxiosResponse<LearningPath> = await this.api.get(
      `/learning/learning-path?learning_goals=${goalsString}&time_available=${timeAvailable}`
    );
    return response.data;
  }

  // Review recommendations
  async getReviewRecommendations(): Promise<any> {
    const response = await this.api.get('/learning/review-recommendations');
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // WebSocket connection
  createWebSocketConnection(userId: number): WebSocket {
    const wsUrl = this.baseURL.replace('http', 'ws') + `/learning/ws/${userId}`;
    return new WebSocket(wsUrl);
  }
}

export const apiService = new ApiService();
export default apiService;