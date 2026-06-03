FROM ollama/ollama:latest

# Pull llama3.2 model on build (so it's cached)
RUN ollama pull llama3.2

# Expose Ollama default port
EXPOSE 11434

# Keep container running
CMD ["serve"]
