FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port (Railway will use this)
EXPOSE 8765

# Set environment variables
ENV PORT=8765
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the server
CMD ["python3", "simple_http_server.py"]
