# LeaderboardX - Technical Documentation

A high-performance, multi-tenant SaaS leaderboard platform for indie game studios.

## 🏗️ Architecture Overview

### Core Technologies
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache**: (planned) Redis for high-performance leaderboard operations
- **Frontend**: React with TypeScript
- **Deployment**: Docker + Docker Compose

### Multi-Tenant Architecture
```
Studios (Tenants)
├── Games (Multiple per studio)
│   ├── Leaderboards (Multiple per game)
│   └── Players/Users
├── Team Members (Dashboard users)
└── Subscription/Billing
```

## 📁 Project Structure

```
leaderboardx/
├── codebase/
│   ├── api/                 # API route handlers
│   │   └── v1/             # Version 1 API endpoints
│   │       ├── health.py   # Health endpoints
│   │       ├── studio.py   # Company/game/leaderboard management (no dashboard auth yet)
│   │       ├── client.py   # Client API (device auth, score submit, leaderboard fetch)
│   │       └── admin.py    # Developer overview endpoints
│   ├── auth/               # Authentication utilities
│   ├── crud/               # Database operations
│   ├── models/             # SQLAlchemy database models
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic
│   ├── middleware/         # Custom middleware
│   ├── config.py           # Configuration management
│   └── main.py             # FastAPI fast_app initialization
├── frontend/               # React dashboard (planned)
├── migrations/             # Database migrations (Alembic)
├── docker-compose.yml      # Development environment
├── Dockerfile              # Production container
└── requirements.txt        # Python dependencies
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT tokens** for dashboard users (studio team members)
- **API keys** for game client integration
- **Role-based access control** (Admin, Manager, Developer)
- **Multi-tenant data isolation** (studio-level)

### API Security
- Rate limiting per API key and IP
- Request validation with Pydantic
- SQL injection prevention
- CORS configuration
- Secure password hashing (bcrypt)

### Production Security
- Environment-based configuration
- Secrets management via environment variables
- Docker non-root user execution
- Health checks and monitoring endpoints

## 🚀 Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Quick Start
```bash
# Clone and start services
git clone <repo>
cd leaderboardx
docker-compose up --build

# Access the API
curl http://localhost:8000/health
```

### Environment Variables
```bash
# Core settings
APP_NAME=LeaderboardX
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/leaderboard

# Redis
REDIS_URL=redis://redis:6379

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 📊 Performance Features

### Redis Integration
- **Real-time leaderboards** with sorted sets
- **Session caching** for dashboard users
- **Rate limiting** with sliding windows
- **API response caching**

### Database Optimization
- **Async SQLAlchemy** for non-blocking I/O
- **Connection pooling** for high concurrency
- **Optimized queries** with proper indexing
- **Database migrations** with Alembic

## 🔧 API Design

### RESTful Endpoints
- **Studios**: Registration, management, settings
- **Games**: CRUD operations, API key management
- **Leaderboards**: Configuration, analytics
- **Client API**: Score submission, leaderboard fetching

### WebSocket Integration
- Real-time leaderboard updates
- Studio dashboard notifications
- System status updates

## 📈 Monitoring & Observability

### Health Checks
- `/health` - Basic service health
- `/health/database` - Database connectivity
- `/health/redis` - Redis connectivity

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking and monitoring
- Performance metrics

---

*This documentation is updated as features are implemented.*