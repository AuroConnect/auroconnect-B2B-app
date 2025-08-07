FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install Python dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🔧 Initializing database..."\n\
python init_db_docker.py\n\
echo "🚀 Starting server..."\n\
python run.py' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 