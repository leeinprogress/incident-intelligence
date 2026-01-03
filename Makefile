.PHONY: help install run test docker-build docker-up docker-down clean lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run application locally"
	@echo "  make test          - Run tests"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make clean         - Clean temporary files"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code with black"

# Install dependencies
install:
	pip install -r requirements.txt

# Run application locally
run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/ -v

# Build Docker image
docker-build:
	docker build -t incident-intelligence:latest .

# Start Docker containers
docker-up:
	docker compose up -d

# Stop Docker containers
docker-down:
	docker compose down

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Run linters
lint:
	ruff check src/ tests/ --fix
	mypy src/ --ignore-missing-imports

# Format code
format:
	black src/ tests/ scripts/

