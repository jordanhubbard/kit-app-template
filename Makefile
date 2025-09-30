# Kit App Template - Master Makefile
# Handles all build operations and dependency management

# Detect OS
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

ifeq ($(UNAME_S),Linux)
	OS := linux
	PYTHON := python3
	PACKAGE_MANAGER := $(shell which apt-get 2>/dev/null || which yum 2>/dev/null || which dnf 2>/dev/null || which pacman 2>/dev/null)
	NPM_INSTALL_CMD := sudo apt-get install -y nodejs npm || sudo yum install -y nodejs npm || sudo dnf install -y nodejs npm || sudo pacman -S --noconfirm nodejs npm
endif

ifeq ($(UNAME_S),Darwin)
	OS := macos
	PYTHON := python3
	PACKAGE_MANAGER := $(shell which brew 2>/dev/null)
	NPM_INSTALL_CMD := brew install node
endif

ifeq ($(OS),Windows_NT)
	OS := windows
	PYTHON := python
	PACKAGE_MANAGER := $(shell where choco 2>NUL || where winget 2>NUL)
	NPM_INSTALL_CMD := winget install OpenJS.NodeJS || choco install nodejs
endif

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Check for required tools
HAS_PYTHON := $(shell which $(PYTHON) 2>/dev/null)
HAS_NPM := $(shell which npm 2>/dev/null)
HAS_NODE := $(shell which node 2>/dev/null)
HAS_GIT := $(shell which git 2>/dev/null)
HAS_MAKE := true

# Node/NPM version requirements
MIN_NODE_VERSION := 16.0.0
MIN_NPM_VERSION := 7.0.0

# Directories
ROOT_DIR := $(shell pwd)
KIT_PLAYGROUND_DIR := $(ROOT_DIR)/kit_playground
TOOLS_DIR := $(ROOT_DIR)/tools
BUILD_DIR := $(ROOT_DIR)/_build

# Default target
.PHONY: all
all: check-deps
	@echo "$(GREEN)Kit App Template - Available Commands:$(NC)"
	@echo ""
	@echo "$(BLUE)Core Commands:$(NC)"
	@echo "  make build              - Build Kit applications"
	@echo "  make playground         - Launch Kit Playground (visual IDE)"
	@echo "  make template-new       - Create new template (CLI)"
	@echo "  make test              - Run test suite"
	@echo ""
	@echo "$(BLUE)Kit Playground (Local):$(NC)"
	@echo "  make playground-install - Install Kit Playground dependencies"
	@echo "  make playground-dev     - Run Kit Playground in development mode"
	@echo "  make playground-build   - Build Kit Playground for distribution"
	@echo "  make playground-dist    - Create platform installers"
	@echo ""
	@echo "$(BLUE)Kit Playground (Docker - No Node.js required):$(NC)"
	@echo "  make playground-docker-build     - Build in Docker container"
	@echo "  make playground-docker-dist      - Create distribution in Docker"
	@echo "  make playground-docker-dist-linux - Create Linux AppImage"
	@echo "  make playground-docker-dist-all   - Build for all platforms"
	@echo "  make playground-docker-shell     - Open shell in container"
	@echo "  make playground-docker-clean     - Remove Docker image"
	@echo ""
	@echo "$(BLUE)Dependencies:$(NC)"
	@echo "  make deps              - Check all dependencies"
	@echo "  make install-deps      - Install missing dependencies"
	@echo "  make install-npm       - Install Node.js and npm"
	@echo "  make install-python    - Install Python"
	@echo ""
	@echo "$(BLUE)Utilities:$(NC)"
	@echo "  make clean             - Clean build artifacts"
	@echo "  make help              - Show this help message"

.PHONY: help
help: all

# Check dependencies
.PHONY: check-deps deps
check-deps deps:
	@echo "$(BLUE)Checking system dependencies...$(NC)"
	@echo ""
	@echo "Operating System: $(OS) ($(UNAME_M))"
	@echo ""

	@# Check Git
	@if [ -z "$(HAS_GIT)" ]; then \
		echo "$(RED)✗ Git is not installed$(NC)"; \
		echo "  Install: https://git-scm.com/downloads"; \
		EXIT_CODE=1; \
	else \
		echo "$(GREEN)✓ Git is installed$(NC) ($(shell git --version))"; \
	fi

	@# Check Python
	@if [ -z "$(HAS_PYTHON)" ]; then \
		echo "$(RED)✗ Python is not installed$(NC)"; \
		echo "  Run: make install-python"; \
		EXIT_CODE=1; \
	else \
		PYTHON_VERSION=$$($(PYTHON) --version 2>&1 | cut -d' ' -f2); \
		echo "$(GREEN)✓ Python is installed$(NC) ($$PYTHON_VERSION)"; \
	fi

	@# Check Node.js
	@if [ -z "$(HAS_NODE)" ]; then \
		echo "$(RED)✗ Node.js is not installed$(NC)"; \
		echo "  Run: make install-npm"; \
		EXIT_CODE=1; \
	else \
		NODE_VERSION=$$(node --version | cut -d'v' -f2); \
		NODE_MAJOR=$$(echo $$NODE_VERSION | cut -d'.' -f1); \
		if [ $$NODE_MAJOR -lt 16 ]; then \
			echo "$(YELLOW)⚠ Node.js version $$NODE_VERSION is too old (need >= 16.0.0)$(NC)"; \
			echo "  Run: make install-npm"; \
		else \
			echo "$(GREEN)✓ Node.js is installed$(NC) (v$$NODE_VERSION)"; \
		fi; \
	fi

	@# Check npm
	@if [ -z "$(HAS_NPM)" ]; then \
		echo "$(RED)✗ npm is not installed$(NC)"; \
		echo "  Run: make install-npm"; \
		EXIT_CODE=1; \
	else \
		NPM_VERSION=$$(npm --version); \
		echo "$(GREEN)✓ npm is installed$(NC) (v$$NPM_VERSION)"; \
	fi

	@# Check for NVIDIA GPU (optional but recommended)
	@if command -v nvidia-smi >/dev/null 2>&1; then \
		echo "$(GREEN)✓ NVIDIA GPU detected$(NC)"; \
		nvidia-smi --query-gpu=name --format=csv,noheader | head -1; \
	else \
		echo "$(YELLOW)⚠ No NVIDIA GPU detected$(NC) (optional but recommended)"; \
	fi

	@echo ""
	@if [ -n "$$EXIT_CODE" ]; then \
		echo "$(RED)Some dependencies are missing. Run 'make install-deps' to install them.$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)All required dependencies are installed!$(NC)"; \
	fi

# Install all missing dependencies
.PHONY: install-deps
install-deps:
	@echo "$(BLUE)Installing missing dependencies...$(NC)"
	@if [ -z "$(HAS_PYTHON)" ]; then \
		$(MAKE) install-python; \
	fi
	@if [ -z "$(HAS_NPM)" ] || [ -z "$(HAS_NODE)" ]; then \
		$(MAKE) install-npm; \
	fi
	@echo "$(GREEN)Dependencies installation complete!$(NC)"

# Install Node.js and npm
.PHONY: install-npm
install-npm:
	@echo "$(BLUE)Installing Node.js and npm...$(NC)"
ifeq ($(OS),linux)
	@if [ -z "$(PACKAGE_MANAGER)" ]; then \
		echo "$(RED)No package manager found. Please install Node.js manually:$(NC)"; \
		echo "  https://nodejs.org/en/download/"; \
		exit 1; \
	fi
	@echo "Using package manager: $(PACKAGE_MANAGER)"
	@$(NPM_INSTALL_CMD) || { \
		echo "$(RED)Failed to install Node.js. Trying alternative method...$(NC)"; \
		curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -; \
		sudo apt-get install -y nodejs; \
	}
endif
ifeq ($(OS),macos)
	@if [ -z "$(PACKAGE_MANAGER)" ]; then \
		echo "$(YELLOW)Homebrew not found. Installing Homebrew first...$(NC)"; \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
	fi
	@brew install node || { \
		echo "$(RED)Failed to install Node.js via Homebrew$(NC)"; \
		echo "Please install manually from: https://nodejs.org/en/download/"; \
		exit 1; \
	}
endif
ifeq ($(OS),windows)
	@echo "$(YELLOW)Please install Node.js using one of these methods:$(NC)"
	@echo "1. Download installer from: https://nodejs.org/en/download/"
	@echo "2. Using winget: winget install OpenJS.NodeJS"
	@echo "3. Using chocolatey: choco install nodejs"
	@exit 1
endif
	@echo "$(GREEN)Node.js and npm installed successfully!$(NC)"

# Install Python
.PHONY: install-python
install-python:
	@echo "$(BLUE)Installing Python...$(NC)"
ifeq ($(OS),linux)
	@sudo apt-get update && sudo apt-get install -y python3 python3-pip || \
	 sudo yum install -y python3 python3-pip || \
	 sudo dnf install -y python3 python3-pip || \
	 sudo pacman -S --noconfirm python python-pip
endif
ifeq ($(OS),macos)
	@brew install python3 || { \
		echo "$(RED)Failed to install Python via Homebrew$(NC)"; \
		echo "Please install manually from: https://www.python.org/downloads/"; \
		exit 1; \
	}
endif
ifeq ($(OS),windows)
	@echo "$(YELLOW)Please install Python from:$(NC)"
	@echo "https://www.python.org/downloads/"
	@echo "Make sure to check 'Add Python to PATH' during installation"
	@exit 1
endif
	@echo "$(GREEN)Python installed successfully!$(NC)"

# Build Kit applications
.PHONY: build
build: check-deps
	@echo "$(BLUE)Building Kit applications...$(NC)"
	@./repo.sh build

# Launch Kit Playground
.PHONY: playground
playground: playground-check
	@echo "$(BLUE)Launching Kit Playground...$(NC)"
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm start

# Check if Kit Playground is installed
.PHONY: playground-check
playground-check:
	@if [ ! -f "$(KIT_PLAYGROUND_DIR)/ui/node_modules/.package-lock.json" ]; then \
		echo "$(YELLOW)Kit Playground dependencies not installed. Installing...$(NC)"; \
		$(MAKE) playground-install; \
	fi

# Install Kit Playground dependencies
.PHONY: playground-install
playground-install: check-deps
	@echo "$(BLUE)Installing Kit Playground dependencies...$(NC)"
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm install
	@echo "$(GREEN)Kit Playground is ready!$(NC)"
	@echo "Run 'make playground' to launch"

# Run Kit Playground in development mode
.PHONY: playground-dev
playground-dev: playground-check
	@echo "$(BLUE)Starting Kit Playground in development mode...$(NC)"
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm run dev

# Build Kit Playground for production
.PHONY: playground-build
playground-build: playground-check
	@echo "$(BLUE)Building Kit Playground for production...$(NC)"
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm run build

# Create platform-specific installers
.PHONY: playground-dist
playground-dist: playground-check
	@echo "$(BLUE)Creating Kit Playground installers...$(NC)"
ifeq ($(OS),linux)
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm run dist -- --linux
endif
ifeq ($(OS),macos)
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm run dist -- --mac
endif
ifeq ($(OS),windows)
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm run dist -- --win
endif
	@echo "$(GREEN)Installer created in $(KIT_PLAYGROUND_DIR)/ui/dist/$(NC)"

# Docker-based playground targets (no host dependencies except make and docker)
.PHONY: playground-docker-check
playground-docker-check:
	@which docker >/dev/null 2>&1 || { \
		echo "$(RED)Docker is not installed or not in PATH$(NC)"; \
		echo "Please install Docker: https://docs.docker.com/get-docker/"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ Docker is installed$(NC)"

.PHONY: playground-docker-image
playground-docker-image: playground-docker-check
	@echo "$(BLUE)Building Kit Playground Docker image...$(NC)"
	@cd $(KIT_PLAYGROUND_DIR) && docker build -t kit-playground:latest .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

.PHONY: playground-docker-build
playground-docker-build: playground-docker-image
	@echo "$(BLUE)Building Kit Playground in Docker container...$(NC)"
	@docker run --rm \
		-v $(KIT_PLAYGROUND_DIR)/ui/build:/app/ui/build \
		kit-playground:latest \
		sh -c "cd ui && npm run build"
	@echo "$(GREEN)Build complete! Output in $(KIT_PLAYGROUND_DIR)/ui/build/$(NC)"

.PHONY: playground-docker-dist
playground-docker-dist: playground-docker-image
	@echo "$(BLUE)Creating Kit Playground distribution in Docker...$(NC)"
	@mkdir -p $(KIT_PLAYGROUND_DIR)/ui/dist
	@docker run --rm \
		-v $(KIT_PLAYGROUND_DIR)/ui/dist:/app/ui/dist \
		kit-playground:latest \
		sh -c "cd ui && npm run dist"
	@echo "$(GREEN)Distribution created in $(KIT_PLAYGROUND_DIR)/ui/dist/$(NC)"

.PHONY: playground-docker-dist-linux
playground-docker-dist-linux: playground-docker-image
	@echo "$(BLUE)Creating Linux distribution in Docker...$(NC)"
	@mkdir -p $(KIT_PLAYGROUND_DIR)/ui/dist
	@docker run --rm \
		-v $(KIT_PLAYGROUND_DIR)/ui/dist:/app/ui/dist \
		kit-playground:latest \
		sh -c "cd ui && npm run dist -- --linux"
	@echo "$(GREEN)Linux distribution created in $(KIT_PLAYGROUND_DIR)/ui/dist/$(NC)"

.PHONY: playground-docker-dist-all
playground-docker-dist-all: playground-docker-image
	@echo "$(BLUE)Creating distributions for all platforms in Docker...$(NC)"
	@mkdir -p $(KIT_PLAYGROUND_DIR)/ui/dist
	@docker run --rm \
		-v $(KIT_PLAYGROUND_DIR)/ui/dist:/app/ui/dist \
		kit-playground:latest \
		sh -c "cd ui && npm run dist:all"
	@echo "$(GREEN)All distributions created in $(KIT_PLAYGROUND_DIR)/ui/dist/$(NC)"

.PHONY: playground-docker-shell
playground-docker-shell: playground-docker-image
	@echo "$(BLUE)Starting interactive shell in Kit Playground container...$(NC)"
	@docker run --rm -it \
		-v $(KIT_PLAYGROUND_DIR):/app \
		kit-playground:latest \
		/bin/bash

.PHONY: playground-docker-clean
playground-docker-clean:
	@echo "$(BLUE)Removing Kit Playground Docker image...$(NC)"
	@docker rmi kit-playground:latest 2>/dev/null || true
	@echo "$(GREEN)Docker image removed$(NC)"

# Create new template (CLI)
.PHONY: template-new
template-new: check-deps
	@echo "$(BLUE)Creating new template...$(NC)"
	@./repo.sh template new

# Run tests
.PHONY: test
test: check-deps
	@echo "$(BLUE)Running test suite...$(NC)"
	@./repo.sh test

# Clean build artifacts
.PHONY: clean
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR)
	@rm -rf $(KIT_PLAYGROUND_DIR)/ui/build
	@rm -rf $(KIT_PLAYGROUND_DIR)/ui/dist
	@rm -rf $(ROOT_DIR)/_compiler
	@rm -rf $(ROOT_DIR)/_repo
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

# Deep clean including dependencies
.PHONY: clean-all
clean-all: clean playground-docker-clean
	@echo "$(YELLOW)Removing all installed dependencies...$(NC)"
	@rm -rf $(KIT_PLAYGROUND_DIR)/ui/node_modules
	@rm -f $(KIT_PLAYGROUND_DIR)/ui/package-lock.json
	@echo "$(GREEN)Deep clean complete!$(NC)"

# Platform-specific repo commands
.PHONY: repo-build
repo-build: check-deps
	@./repo.sh build

.PHONY: repo-launch
repo-launch: check-deps
	@./repo.sh launch

.PHONY: repo-package
repo-package: check-deps
	@./repo.sh package

# Windows-specific targets (when running on Windows via Git Bash or WSL)
ifeq ($(OS),windows)
.PHONY: win-build
win-build:
	@cmd.exe /c "repo.bat build"

.PHONY: win-launch
win-launch:
	@cmd.exe /c "repo.bat launch"
endif

# Help for Windows users
.PHONY: windows-help
windows-help:
	@echo "$(BLUE)Windows Users:$(NC)"
	@echo ""
	@echo "Option 1: Use Git Bash (Recommended)"
	@echo "  - Install Git for Windows: https://git-scm.com/download/win"
	@echo "  - Open Git Bash and run: make playground"
	@echo ""
	@echo "Option 2: Use WSL2"
	@echo "  - Install WSL2: wsl --install"
	@echo "  - Open WSL terminal and run: make playground"
	@echo ""
	@echo "Option 3: Use native Windows commands"
	@echo "  - Run repo.bat instead of make"
	@echo "  - Use 'npm' commands directly in kit_playground/"

# Version check
.PHONY: version
version:
	@echo "Kit App Template Build System"
	@echo "OS: $(OS) ($(UNAME_M))"
	@if [ -n "$(HAS_PYTHON)" ]; then $(PYTHON) --version; fi
	@if [ -n "$(HAS_NODE)" ]; then echo "Node.js: $$(node --version)"; fi
	@if [ -n "$(HAS_NPM)" ]; then echo "npm: v$$(npm --version)"; fi
	@if [ -n "$(HAS_GIT)" ]; then git --version; fi

.DEFAULT_GOAL := all