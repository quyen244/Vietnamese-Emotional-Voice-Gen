# Use an official Python runtime as a parent image
# We use a slim PyTorch capable image structure or standard Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (e.g. ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# We specify extra index url for PyTorch CPU/GPU depending on needs
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose ports for FastAPI (8000) and Gradio if isolated (7860) 
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the FastApi server (which mounts Gradio)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
