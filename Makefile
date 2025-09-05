.PHONY: help start stop restart build logs logs-backend logs-frontend logs-db logs-redis logs-celery shell-backend migrate makemigrations test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  start          - Start all services"
	@echo "  stop           - Stop all services"
	@echo "  restart        - Restart all services"
	@echo "  build          - Build all Docker images"
	@echo "  logs           - Show logs for all services"
	@echo "  logs-backend   - Show logs for Django backend service"
	@echo "  logs-frontend  - Show logs for Next.js frontend service"
	@echo "  logs-db        - Show logs for PostgreSQL database"
	@echo "  logs-redis     - Show logs for Redis service"
	@echo "  logs-celery    - Show logs for Celery worker"
	@echo "  shell-backend  - Access Django shell via docker exec"
	@echo "  migrate        - Run Django migrations"
	@echo "  makemigrations - Create Django migrations"
	@echo "  test           - Run pytest tests"
	@echo "  clean          - Clean up Docker containers and volumes"

# Start all services
start:
	@echo "Starting all services..."
	docker-compose -f docker-compose-local.yml up -d

# Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose -f docker-compose-local.yml down

# Restart all services
restart: stop start
	@echo "Services restarted successfully"

# Build all Docker images
build:
	@echo "Building Docker images..."
	docker-compose -f docker-compose-local.yml build

# Show logs for all services
logs:
	@echo "Showing logs for all services..."
	docker-compose -f docker-compose-local.yml logs -f

# Show logs for backend service
logs-backend:
	@echo "Showing logs for Django backend..."
	docker-compose -f docker-compose-local.yml logs -f backend

# Show logs for frontend service
logs-frontend:
	@echo "Showing logs for Next.js frontend..."
	docker-compose -f docker-compose-local.yml logs -f frontend

# Show logs for database service
logs-db:
	@echo "Showing logs for PostgreSQL database..."
	docker-compose -f docker-compose-local.yml logs -f db

# Show logs for Redis service
logs-redis:
	@echo "Showing logs for Redis..."
	docker-compose -f docker-compose-local.yml logs -f redis

# Show logs for Celery worker
logs-celery:
	@echo "Showing logs for Celery worker..."
	docker-compose -f docker-compose-local.yml logs -f celeryworker

# Access Django shell
shell-backend:
	@echo "Accessing Django shell..."
	docker exec -it nova811_backend python manage.py shell

# Run Django migrations
migrate:
	@echo "Running Django migrations..."
	docker exec -it nova811_backend python manage.py migrate

# Create Django migrations
makemigrations:
	@echo "Creating Django migrations..."
	docker exec -it nova811_backend python manage.py makemigrations

# Run bash in backend container
bash-backend:
	@echo "Starting backend bash..."
	docker exec -it nova811_backend bash

# Run tests
test:
	@echo "Running pytest tests..."
	docker exec -it nova811_backend pytest

# Clean up Docker containers and volumes
clean:
	@echo "Cleaning up Docker containers and volumes..."
	docker-compose -f docker-compose-local.yml down -v
	docker system prune -f

# Create superuser
createsuperuser:
	@echo "Creating Django superuser..."
	docker exec -it nova811_backend python manage.py createsuperuser

# Collect static files
collectstatic:
	@echo "Collecting static files..."
	docker exec -it nova811_backend python manage.py collectstatic --noinput

# Show Django management commands
django-help:
	@echo "Available Django management commands:"
	docker exec -it nova811_backend python manage.py help
