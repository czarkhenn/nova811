# Nova811 - Django + Next.js Full Stack Application

A modern full-stack application built with Django REST Framework backend and Next.js frontend, following the HackSoftware Django-Styleguide.

## 🚀 Features

### Backend (Django)
- **Django 5.1** with Django REST Framework
- **JWT Authentication** using SimpleJWT
- **PostgreSQL** database
- **Redis** for caching and Celery broker
- **Celery** for background tasks
- **CORS** enabled for frontend integration
- **Pytest** for testing
- **Docker** containerized development
- **Comprehensive logging** configuration

### Frontend (Next.js)
- **Next.js 14** with React
- **Tailwind CSS** for styling
- **TypeScript** support
- **Docker** containerized development

## 🛠 Development Setup

### Prerequisites
- Docker and Docker Compose
- Make (for using Makefile commands)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nova811
   ```

2. **Set up environment files**
   ```bash
   # Backend environment
   cp compose/local/backend/.env.sample compose/local/backend/.env
   
   # Frontend environment
   cp compose/local/frontend/.env.sample compose/local/frontend/.env
   ```

3. **Start all services**
   ```bash
   make start
   ```

4. **Run initial migrations**
   ```bash
   make migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   make createsuperuser
   ```

### 📋 Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make build` | Build all Docker images |
| `make logs` | Show logs for all services |
| `make logs-backend` | Show logs for Django backend |
| `make logs-frontend` | Show logs for Next.js frontend |
| `make logs-db` | Show logs for PostgreSQL |
| `make logs-redis` | Show logs for Redis |
| `make logs-celery` | Show logs for Celery worker |
| `make shell-backend` | Access Django shell |
| `make migrate` | Run Django migrations |
| `make test` | Run pytest tests |
| `make clean` | Clean up containers and volumes |

## 🏗 Architecture

### Backend Structure
```
backend/
├── core/                   # Django project
│   ├── settings/          # Settings module
│   │   ├── base.py       # Base settings
│   │   └── local.py      # Local development settings
│   ├── celery.py         # Celery configuration
│   ├── urls.py           # URL configuration
│   └── wsgi.py           # WSGI configuration
├── requirements/          # Python dependencies
│   ├── base.txt          # Base requirements
│   └── local.txt         # Local development requirements
├── manage.py             # Django management script
└── pytest.ini           # Pytest configuration
```

### Services
- **Backend**: Django application (port 8000)
- **Frontend**: Next.js application (port 3000)
- **Database**: PostgreSQL (port 5432)
- **Redis**: Cache and Celery broker (port 6379)
- **Celery Worker**: Background task processing
- **Celery Beat**: Periodic task scheduler

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database configuration
- `REDIS_URL`: Redis connection URL
- `CELERY_BROKER_URL`: Celery broker URL

#### Frontend (.env)
- `NEXT_PUBLIC_API_URL`: Backend API URL for client-side
- `API_BASE_URL`: Backend API URL for server-side

## 🧪 Testing

Run the test suite:
```bash
make test
```

## 📝 Development Guidelines

This project follows the [HackSoftware Django-Styleguide](https://github.com/HackSoftware/Django-Styleguide):

- Use **APIView** for views
- Implement **Input/Output serializers** pattern
- Use **services** for business logic
- Write **unit tests** for models and services
- Use **optimized Django ORM queries**
- Handle exceptions at **service level**

## 🚀 Deployment

This template is configured for local development. For production deployment:

1. Create production settings file
2. Configure production environment variables
3. Set up production Docker configuration
4. Configure reverse proxy (nginx)
5. Set up SSL certificates

## 📚 API Documentation

Once the backend is running, you can access:
- **Admin Panel**: http://localhost:8000/admin/
- **API Authentication**:
  - Token obtain: `POST /api/auth/token/`
  - Token refresh: `POST /api/auth/token/refresh/`
  - Token verify: `POST /api/auth/token/verify/`

## 🤝 Contributing

1. Follow the HackSoftware Django-Styleguide
2. Write tests for new features
3. Update documentation as needed
4. Use the provided Make commands for development

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
