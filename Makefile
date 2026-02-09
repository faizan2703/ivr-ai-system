# IVR AI Agent System - Development Commands

## Installation & Setup
install: 
	pip install -r requirements.txt

setup-env:
	cp .env.example .env
	@echo "✓ Created .env file - please edit and add your OpenAI API key"

## Running Services
run-backend:
	cd backend && python main.py

run-frontend:
	cd frontend && python -m http.server 8080

run-all:
	@echo "Starting backend..." && cd backend && python main.py &
	@echo "Starting frontend..." && cd frontend && python -m http.server 8080

## Testing
test-health:
	curl http://localhost:8000/api/v1/health

test-api:
	curl -X POST http://localhost:8000/api/v1/calls/initiate \
		-H "Content-Type: application/json" \
		-d '{"user_name":"Test","user_phone":"+1234567890","call_topic":"test"}'

## Docker
docker-build:
	docker build -t ivr-ai-system .

docker-run:
	docker run -p 8000:8000 -p 8080:8080 -e OPENAI_API_KEY=${OPENAI_API_KEY} ivr-ai-system

docker-compose:
	docker-compose up --build

## Cleanup & Maintenance
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache build dist *.egg-info
	rm -rf data/chroma

lint:
	pylint backend/app --disable=all --enable=E,F

format:
	black backend/ frontend/

## Documentation
docs-open:
	@echo "API docs available at: http://localhost:8000/docs"
	@echo "ReDoc available at: http://localhost:8000/redoc"

help:
	@echo "IVR AI Agent System - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install         - Install Python dependencies"
	@echo "  make setup-env       - Create .env from template"
	@echo ""
	@echo "Development:"
	@echo "  make run-backend     - Start backend server"
	@echo "  make run-frontend    - Start frontend server"
	@echo "  make run-all         - Start both services"
	@echo ""
	@echo "Testing:"
	@echo "  make test-health     - Check API health"
	@echo "  make test-api        - Test API with sample call"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-run      - Run Docker container"
	@echo "  make docker-compose  - Run with Docker Compose"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Clean temporary files"
	@echo "  make lint            - Run linter"
	@echo "  make format          - Format code"
	@echo ""

.PHONY: install setup-env run-backend run-frontend run-all test-health test-api docker-build docker-run docker-compose clean lint format docs-open help
