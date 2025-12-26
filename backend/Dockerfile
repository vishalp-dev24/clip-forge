# ===============================
# Base image with CUDA runtime
# ===============================
# Use the official NVIDIA CUDA runtime image as a base.
# This provides the necessary drivers and libraries for GPU acceleration.
FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04


# Avoid interactive prompts during package installation.
ENV DEBIAN_FRONTEND=noninteractive

# ===============================
# System dependencies
# ===============================
# Update the package lists and install essential system-level dependencies.
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# Python setup
# ===============================
# Upgrade pip to the latest version.
RUN python3 -m pip install --upgrade pip

# ===============================
# Set working directory
# ===============================
# Set the working directory inside the container to /app.
WORKDIR /app
# ===============================
# Copy and install Python deps
# ===============================
# Copy the requirements file into the container.
COPY requirements.txt .

# Install PyTorch with CUDA 12.1 support first.
# This ensures that the GPU-enabled version of torch is installed.
# It uses PyTorch's specific pip wheel index for CUDA 12.1.
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir \
      torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Then install the rest of the Python dependencies from the requirements.txt file.
# The --no-cache-dir option is used to reduce the image size.
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# ===============================
# Copy backend source code
# ===============================
# Copy the application source code into the container.
COPY app/ .

# ===============================
# Runtime directories (mounted as volumes in practice)
# ===============================
# Create directories that will be used at runtime.
# These are typically mounted as volumes to persist data outside the container.
RUN mkdir -p \
    /runtime/data/input_audio \
    /runtime/data/normalized_audio \
    /runtime/data/clips \
    /runtime/data/output_podcast \
    /runtime/cache/models \
    /runtime/cache/torch \
    /runtime/state \
    /runtime/logs

# ===============================
# Environment variables
# ===============================
# Set environment variables for the application.
# PYTHONUNBUFFERED=1 ensures that Python output is sent straight to stdout.
ENV PYTHONUNBUFFERED=1
# Set the home directories for torch and huggingface models to the cache directories.
ENV TORCH_HOME=/runtime/cache/torch
ENV HF_HOME=/runtime/cache/models
ENV TRANSFORMERS_CACHE=/runtime/cache/models

# ===============================
# Expose API port
# ===============================
# Expose port 8000 to allow communication with the application from outside the container.
EXPOSE 8000

# ===============================
# Start backend
# ===============================
# The command to run when the container starts.
# It starts the uvicorn server to run the FastAPI application.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]