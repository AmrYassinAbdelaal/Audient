.PHONY: help install dev-install test test-cov run docker-build docker-run clean lint format

help:
	@echo "AI Audience Agent - Makefile Commands"
	@echo "======================================"
	@echo "install        - Install production dependencies"
	@echo "dev-install    - Install development dependencies"
	@echo "test           - Run tests"
	@echo "test-cov       - Run tests with coverage"
	@echo "run            - Run the application locally"
	@echo "docker-build   - Build Docker image"
	@echo "docker-run     - Run Docker container"
	@echo "docker-compose - Run with docker-compose"
	@echo "clean          - Clean up generated files"
	@echo "lint           - Run linters"
	@echo "format         - Format code with black"
	@echo "evaluate       - Evaluate model accuracy"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black ruff mypy

test:
	pytest app/tests/ -v

test-cov:
	pytest app/tests/ --cov=app --cov-report=html --cov-report=term

run:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -f docker/Dockerfile -t ai-audience-agent:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env ai-audience-agent:latest

docker-compose:
	docker-compose -f docker/docker-compose.yml up --build

docker-compose-down:
	docker-compose -f docker/docker-compose.yml down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build

lint:
	ruff check app/
	mypy app/

format:
	black app/
	ruff check --fix app/

evaluate:
	python scripts/evaluate_accuracy.py --language both --output evaluation_report.json

setup-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env and add your API keys"; \
	else \
		echo ".env file already exists"; \
	fi

init: setup-env install
	@echo "✅ Setup complete! Run 'make run' to start the server."

