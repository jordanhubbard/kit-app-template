# Kit Playground - Docker Build Environment
# Based on electronuserland/builder for cross-platform Electron builds
FROM electronuserland/builder:wine

# Set working directory
WORKDIR /app

# Copy package files first for better layer caching
COPY ui/package*.json ui/

# Install Node.js dependencies (use legacy-peer-deps for compatibility)
RUN cd ui && npm install --legacy-peer-deps

# Copy the rest of the application
COPY electron/ electron/
COPY backend/ backend/
COPY ui/ ui/
COPY core/ core/

# Build the React application (disable TypeScript checking for faster builds)
RUN cd ui && DISABLE_ESLINT_PLUGIN=true TSC_COMPILE_ON_ERROR=true npm run build

# Set environment for Electron
ENV ELECTRON_BUILDER_CACHE=/app/cache

# Default command: show available build targets
CMD ["sh", "-c", "echo 'Kit Playground Docker Build Environment\n\nAvailable commands:\n  docker run <image> npm run build          - Build React app\n  docker run <image> npm run build:electron - Build Electron app\n  docker run <image> npm run dist           - Create distribution\n  docker run <image> npm run dist:all       - Build for all platforms\n\nOr use make targets from the host:\n  make playground-docker-build\n  make playground-docker-dist'"]
