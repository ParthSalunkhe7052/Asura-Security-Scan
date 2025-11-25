# Base image with Python 3.11
FROM python:3.11-slim

# Install Node.js and npm (for Frontend SCA)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY backend/app /app/app
COPY backend/__init__.py /app/backend/__init__.py

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Create a volume mount point for the project to scan
VOLUME /scan

# Set the entrypoint to the CLI
ENTRYPOINT ["python", "-m", "app.cli"]

# Default command (can be overridden)
CMD ["--help"]
