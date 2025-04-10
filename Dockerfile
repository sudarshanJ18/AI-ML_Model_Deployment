FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    # Add X11 dependencies for GUI applications
    libx11-6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY collect_faces.py .
COPY train_model.py .
COPY utils.py .
# Copy the GUI application (looks like it might be named differently than gui.py)
COPY *.py .

# Create necessary directories
RUN mkdir -p models dataset

# Set environment variable for display
ENV DISPLAY=:0

# Set the entry point to the GUI application
# Based on your paste, it seems the main GUI file might not be named recognize.py
CMD ["python", "recognize_faces.py"]

# Expose port if you have an API component 
EXPOSE 10000