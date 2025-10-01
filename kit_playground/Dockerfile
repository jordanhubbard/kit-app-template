# Kit Playground - Docker Build Environment
# Based on electronuserland/builder for cross-platform Electron builds
FROM electronuserland/builder:wine

# Set working directory
WORKDIR /app

# Install Python for cross-platform build script
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Copy package files first for better layer caching
COPY ui/package*.json ui/

# Install Node.js dependencies (use legacy-peer-deps for compatibility)
RUN cd ui && npm install --legacy-peer-deps

# Copy the rest of the application
COPY electron/ electron/
COPY backend/ backend/
COPY ui/ ui/
COPY core/ core/
COPY cross_platform_builder.py .

# Install Python dependencies
RUN pip3 install -r backend/requirements.txt

# Build the React application (disable TypeScript checking for faster builds)
RUN cd ui && DISABLE_ESLINT_PLUGIN=true TSC_COMPILE_ON_ERROR=true npm run build

# Set environment for Electron
ENV ELECTRON_BUILDER_CACHE=/app/cache
ENV ELECTRON_CACHE=/app/cache/electron

# Create cache directories
RUN mkdir -p /app/cache/electron /app/cache/electron-builder

# Default command: show available build targets
CMD ["sh", "-c", "echo 'Kit Playground Docker Build Environment\\n\\nAvailable commands:\\n  docker run <image> npm run dist           - Build for current platform\\n  docker run <image> npm run dist:windows   - Build for Windows\\n  docker run <image> npm run dist:linux     - Build for Linux\\n  docker run <image> npm run dist:all       - Build for all platforms\\n  docker run <image> python3 cross_platform_builder.py --help - Cross-platform builder help\\n\\nOr use make targets from the host:\\n  make playground-docker-build\\n  make playground-docker-dist'"]
