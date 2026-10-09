# Multi-stage Docker build for IMS Bearing Predictive Maintenance Platform
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY . /app

# Expose ports for FastAPI (8000), Streamlit (8501), and MLflow (5000)
EXPOSE 8000 8501 5000

# Default command launches FastAPI API server
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
