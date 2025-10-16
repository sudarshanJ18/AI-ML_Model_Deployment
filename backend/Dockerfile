# Dockerfile - robust backend image for face-recognition app
# - tolerant to missing ./models
# - installs runtime deps needed for headless OpenCV, numpy, TF, etc.
# - non-root user, healthcheck, minimal image size tweaks

FROM python:3.9-slim

# Set working dir
WORKDIR /app

# Install system dependencies (runtime libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgcc-s1 \
    libgfortran5 \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements first
COPY requirements.txt /tmp/requirements.txt

# Upgrade pip and install Python deps
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy entire project into a temporary build directory in the image
COPY . /tmp/build/

# Create runtime directories
RUN mkdir -p /app/models /app/dataset /app/uploads

# Copy models robustly (ignore missing or empty)
RUN mkdir -p /app/models && \
    cp -r /tmp/build/models/* /app/models/ 2>/dev/null || echo "no models found; continuing"

# Copy python app files (safe copy; tolerate missing patterns)
RUN cp /tmp/build/*.py /app/ 2>/dev/null || true

# If you have subfolders (e.g., app package), copy them too
RUN if [ -d /tmp/build/app ]; then cp -r /tmp/build/app /app/; fi

# Clean up build temp
RUN rm -rf /tmp/build /tmp/requirements.txt

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=2

# Expose the port FastAPI/uvicorn will use
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Security: create non-root user and set permissions
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Default command to run FastAPI app with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
