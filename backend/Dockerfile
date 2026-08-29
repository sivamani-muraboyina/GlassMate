# Backend Dockerfile
# Production-ready FastAPI/Uvicorn application

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project dependencies
COPY pyproject.toml pyproject.toml

# Install Python dependencies (without test extras for production)
RUN pip install --no-cache-dir -e .

# Copy application code
COPY alembic/ alembic/
COPY alembic.ini alembic.ini
COPY backend/ backend/

# Set Python to buffer=1 for proper logging in containers
ENV PYTHONUNBUFFERED=1

# Expose backend port
EXPOSE 8000

# Default to development environment; can be overridden
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Start Uvicorn server
CMD ["uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
