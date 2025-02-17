# Use Python as base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install system dependencies needed for compiling C code
RUN apt-get update && apt-get install -y \
    build-essential \
    clang \
    swig \
    python3-dev \
    libdbus-1-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    pkg-config 

# Compile your C library (phylib)
RUN make

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python can find your custom modules
ENV PYTHONPATH="/app"
ENV LD_LIBRARY_PATH="/usr/local/lib:/usr/lib:/app"

# Expose port (if your server runs on a port)
EXPOSE 8000

# Command to start your Python server
CMD ["python", "poolserver.py"]
