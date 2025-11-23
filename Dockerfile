# Use NVIDIA CUDA base image with Ubuntu 22.04
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    git-lfs \
    libsndfile1 \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy Python requirements first for better caching
COPY py/requirements.txt /app/py/
COPY py/pyproject.toml /app/py/

# Install Python dependencies with GPU support
# Note: Using onnxruntime-gpu 1.23.2 (1.23.1 doesn't exist)
RUN pip3 install --no-cache-dir \
    onnxruntime-gpu==1.23.2 \
    numpy>=1.26.0 \
    soundfile>=0.12.1 \
    librosa>=0.10.0 \
    PyYAML>=6.0 \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.0.0

# Copy project files
COPY . /app/

# Create results directory
RUN mkdir -p /app/results

# Initialize git-lfs
RUN git lfs install

# Set default command
WORKDIR /app/py
CMD ["python3", "example_onnx.py", "--use-gpu"]
