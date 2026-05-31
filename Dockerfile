FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (minimal - no fastmcp)
RUN pip install --no-cache-dir requests pillow python-dotenv

# Copy only the server file needed
COPY simple_http_server.py .
COPY ollama_client.py .

# Create logs directory
RUN mkdir -p /app/logs

# Railway injects PORT automatically
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python3", "simple_http_server.py"]
