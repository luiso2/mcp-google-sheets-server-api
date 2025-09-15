# Multi-stage build for MCP Google Sheets Server
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install uv for faster dependency installation
RUN pip install uv

# Install dependencies
RUN uv pip install --system .

# Production stage
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser pyproject.toml ./

# Create directories for credentials and config
RUN mkdir -p /app/credentials /app/config && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV API_KEYS_FILE=/app/config/api_keys.json
ENV SERVICE_ACCOUNT_PATH=/app/credentials/service-account.json
ENV CREDENTIALS_PATH=/app/credentials/credentials.json

# Expose port
EXPOSE 8080

# Default command - HTTP API server
CMD ["python", "-m", "mcp_google_sheets.api.http_server"]