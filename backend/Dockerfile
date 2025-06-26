FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for better Python behavior
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with better error handling
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies with better error handling
COPY requirements-minimal.txt .

# Install dependencies with verbose output for debugging
RUN pip install --no-cache-dir --verbose -r requirements-minimal.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Health check with better error handling
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main_production:app", "--host", "0.0.0.0", "--port", "8000"] 