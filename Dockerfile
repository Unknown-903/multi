FROM ubuntu:latest

# Create app directory
RUN mkdir ./app
WORKDIR /app

# Set timezone to avoid tzdata prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

# Install system dependencies, including SoX
RUN apt -qq update --fix-missing && \
    apt -qq install -y \
    git \
    mediainfo \
    zip \
    rar \
    sox \
    libsox-fmt-all \
    python3 \
    ffmpeg \
    python3-pip \
    p7zip-full \
    p7zip-rar && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Install numpy first to avoid sox setup.py errors
RUN pip3 install numpy

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Start script
CMD ["bash", "start.sh"]
