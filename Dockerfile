FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .

# Create necessary directories
RUN mkdir -p models dataset uploads

# Copy models if they exist
COPY models/ models/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for the API
EXPOSE 8000

# Create a non-root user for security
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set the entry point to the FastAPI application
CMD ["python", "-m", "uvicorn", "recognize:app", "--host", "0.0.0.0", "--port", "8000"]