# Kit Playground - Native Linux Build Container
# Builds for the container's architecture (x86_64 or ARM64)
# Build context should be the repository root: docker build -f kit_playground/Dockerfile .
FROM node:18-bullseye

# Install Python and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libgtk-3-0 \
    libnotify4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    libatspi2.0-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files for caching
COPY kit_playground/ui/package*.json ui/

# Install Node.js dependencies
RUN cd ui && npm install --legacy-peer-deps

# Copy application source
COPY kit_playground/electron/ electron/
COPY kit_playground/backend/ backend/
COPY kit_playground/ui/ ui/
COPY kit_playground/core/ core/

# Copy tools and templates from repository root
COPY tools/ tools/
COPY templates/ templates/

# Install Python dependencies
RUN pip3 install -r backend/requirements.txt

# Build the React application
RUN cd ui && npm run build

# Default command
CMD ["sh", "-c", "echo 'Kit Playground Build Container\\n\\nUsage:\\n  docker run <image> sh -c \"cd ui && npm run dist\"\\n  docker run -v $(pwd)/ui/dist:/app/ui/dist <image> sh -c \"cd ui && npm run dist\"'"]
