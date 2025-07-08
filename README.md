# 🧠 Powered Adaptive Learning & Skill Development APP

A comprehensive web application that uses AI to analyze learning styles, generate personalized content, and provide real-time adaptive learning experiences with support for neurodivergent learners.

## 🚀 Features

### AI Components
- **Learning Style Analysis**: NLP-powered analysis of user responses to determine visual, auditory, or kinesthetic learning preferences
- **Content Generation**: Dynamic creation of personalized learning materials based on learning style and difficulty level
- **Recommendation Engine**: ML-driven suggestions for learning paths and resources
- **Real-time Adaptation**: WebSocket-based live adjustments to learning experience
- **Neurodivergent Support**: Specialized adaptations for different learning needs

### Core Functionality
- User authentication and profile management
- Progress tracking and analytics
- Interactive dashboard with real-time updates
- Responsive Material-UI design
- RESTful API with comprehensive endpoints

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Database ORM
- **scikit-learn**: Machine learning algorithms
- **WebSockets**: Real-time communication
- **Pydantic**: Data validation

### Frontend
- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Component library
- **Vite**: Fast build tool
- **Axios**: HTTP client
- **Recharts**: Data visualization

### AI/ML
- **Natural Language Processing**: User input analysis
- **Machine Learning**: Progress tracking and adaptation
- **Reinforcement Learning**: Experience optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 12001
```

### Demo
```bash
python demo_server.py
```

## 🌐 Access Points

- **Backend API**: http://localhost:12000
- **Interactive Demo**: http://localhost:12002
- **API Documentation**: http://localhost:12000/docs

## 🧪 Testing

Run the comprehensive integration test:
```bash
python integration_test.py
```

## 📊 API Endpoints

### AI Endpoints
- `POST /ai/analyze-learning-style` - Analyze user learning style
- `POST /ai/generate-content` - Generate personalized content
- `POST /ai/recommendations` - Get learning recommendations

### Core Endpoints
- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /users/profile` - User profile
- `WebSocket /ws` - Real-time updates

## 🏗️ Architecture

```
adaptive-learning-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── ai/             # AI components
│   │   │   ├── learning_style_analyzer.py
│   │   │   ├── content_generator.py
│   │   │   ├── recommendation_engine.py
│   │   │   └── reinforcement_learning.py
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── database/       # Database configuration
│   └── main.py             # Application entry point
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   └── services/       # API services
│   └── package.json
├── shared/                 # Shared utilities
└── demo.html              # Interactive demo
```

## 🎯 Key Features Demonstrated

### Learning Style Analysis
```json
{
  "user_responses": ["I prefer visual diagrams", "I like hands-on practice"],
  "result": {
    "primary_style": "visual",
    "confidence": 0.85,
    "adaptations": ["Use visual materials", "Interactive examples"]
  }
}
```

### Content Generation
```json
{
  "topic": "Python Functions",
  "learning_style": "visual",
  "difficulty_level": "beginner",
  "result": {
    "content_type": "lesson",
    "content": "Personalized content for visual learners",
    "exercises": [...],
    "adaptations": [...]
  }
}
```

### Recommendations
```json
{
  "user_id": "user123",
  "current_topic": "Python OOP",
  "performance_data": {"accuracy": 0.75},
  "result": {
    "recommendations": [...],
    "user_profile": {...}
  }
}
```

## 🎉 Status

✅ **FULLY FUNCTIONAL** - All AI components working, API endpoints tested, frontend built successfully!

The Adaptive Learning App is ready for use with comprehensive AI-powered features for personalized learning experiences.
