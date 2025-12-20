# Multi-stage build for production optimization
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY autonomous-orchestrator/ ./autonomous-orchestrator/
COPY payment-integration/ ./payment-integration/

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PAYPAL_ACCOUNT=gwc2780@gmail.com
ENV AUTONOMOUS_MODE=true
ENV SELF_HEALING_ENABLED=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose ports
EXPOSE 8000 8001

# Run application
CMD ["python3", "autonomous-orchestrator/quantum-revenue-engine.py"]
