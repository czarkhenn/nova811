# Nova811 Ticketing Platform

A comprehensive full-stack ticketing platform for managing work orders and contractor assignments with role-based access control, audit trails, and automated notifications.

## 🚀 Tech Stack

### Backend
- **Django 5.1+** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL 15** - Primary database
- **Redis 7** - Caching and message broker
- **Celery** - Asynchronous task processing
- **JWT Authentication** - Token-based authentication
- **Docker** - Containerization

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Build tool and development server
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Bootstrap 5** - CSS framework
- **Axios** - HTTP client
- **Vitest** - Testing framework

### Infrastructure
- **Docker Compose** - Multi-container orchestration

## 📋 Prerequisites

- **Docker** and **Docker Compose**
- **Make** (for using Makefile commands)
- **Git**

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/czarkhenn/nova811.git
cd nova811
```

### 2. Environment Configuration
Copy the sample environment files and configure them:

```bash
# Backend environment
cp compose/local/backend/.env.sample compose/local/backend/.env

# Frontend environment  
cp compose/local/frontend/.env.sample compose/local/frontend/.env
```

Edit the environment files with your specific configuration.

### 3. Build and Start Services
```bash
# Build all Docker images
make build

# Start all services
make start
```

### 4. Initialize Database
```bash
# Run database migrations
make migrate

# Create a superuser account
make createsuperuser

# Load sample data (optional)
make import-tickets
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 📖 Makefile Commands

The project includes a comprehensive Makefile for easy development workflow:

### Service Management
```bash
make start          # Start all services
make stop           # Stop all services  
make restart        # Restart all services
make build          # Build all Docker images
make clean          # Clean up containers and volumes
```

### Development
```bash
make shell-backend  # Access Django shell
make bash-backend   # Access backend container bash
make migrate        # Run Django migrations
make makemigrations # Create Django migrations
make test           # Run pytest tests
```

### Logging
```bash
make logs           # Show logs for all services
make logs-backend   # Show Django backend logs
make logs-frontend  # Show Vue.js frontend logs
make logs-db        # Show PostgreSQL logs
make logs-redis     # Show Redis logs
make logs-celery    # Show Celery worker logs
```

### Data Management
```bash
make import-tickets # Import test users and tickets
make clear-tickets  # Clear all data from database
make createsuperuser # Create Django superuser
make collectstatic  # Collect static files
```

### Utilities
```bash
make django-help    # Show available Django commands
make help          # Show all available make commands
```

## ✨ Features

### 🔐 Authentication & Authorization
- **Email-based Authentication** - Login using email instead of username
- **JWT Token Authentication** - Secure API access with refresh tokens
- **Two-Factor Authentication (2FA)** - Optional TOTP-based 2FA
- **Role-based Access Control** - Admin and Contractor roles with different permissions

### 🎫 Ticket Management
- **Complete CRUD Operations** - Create, read, update, and delete tickets
- **Status Tracking** - Open, In Progress, and Closed statuses
- **Auto-generated Ticket Numbers** - Format: TKT-YYYYMMDD-XXXX
- **Expiration Management** - Automatic tracking of ticket expiration dates
- **Assignment System** - Assign tickets to specific contractors
- **Renewal Functionality** - Extend ticket expiration dates

### 📊 Dashboard & Monitoring
- **Real-time Dashboard** - Overview of ticket statistics and status
- **Expiring Tickets View** - Monitor tickets nearing expiration
- **Notification System** - Automated alerts for expiring tickets
- **Audit Trail** - Comprehensive logging of all user and ticket actions

### 🔍 Audit & Logging
- **User Activity Logs** - Track login, logout, profile changes, and 2FA actions
- **Ticket Change Logs** - Detailed history of all ticket modifications
- **IP Address Tracking** - Record IP addresses for security auditing
- **Before/After Values** - Track field changes with previous and new values

### 🔄 Background Processing
- **Celery Workers** - Asynchronous task processing
- **Scheduled Tasks** - Automated notifications and cleanup jobs
- **Email Notifications** - Automated alerts for ticket events
- **Data Cleanup** - Periodic maintenance tasks

### 🧪 Testing & Quality
- **Comprehensive Test Suite** - Backend tests with pytest
- **Frontend Testing** - Vue component tests with Vitest
- **API Testing** - Automated API endpoint testing
- **Code Quality** - ESLint and Prettier for frontend code formatting



## 🧪 Development Workflow

### Running Tests
```bash
# Run all backend tests
make test

# Run specific test file
docker exec -it nova811_backend pytest backend/users/tests/test_models.py

# Run frontend tests
cd frontend && npm run test

# Run tests with coverage
docker exec -it nova811_backend pytest --cov=.
```

### Code Quality
```bash
# Frontend linting and formatting
cd frontend
npm run lint
npm run format

# Backend code formatting (if using black/isort)
docker exec -it nova811_backend black .
docker exec -it nova811_backend isort .
```

### Database Operations
```bash
# Create new migration
make makemigrations

# Apply migrations
make migrate

# Reset database (WARNING: Destroys all data)
make clean
make build
make start
make migrate
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DB_NAME=nova811
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
```

#### Frontend (.env)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Nova811 Ticketing Platform

# Development
NODE_ENV=development
```


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
