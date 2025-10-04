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
	@echo "  make playground         - Build and launch Kit Playground (Docker)"
	@echo "  make template-new       - Create new template (CLI)"
	@echo "  make test              - Run test suite"
	@echo ""
	@echo "$(BLUE)Kit Playground (Web-based):$(NC)"
	@echo "  make playground                    - Build UI and launch web server (localhost)"
	@echo "  make playground REMOTE=1           - Launch with remote access (0.0.0.0)"
	@echo "  make playground-dev (or make dev)  - Development mode with hot-reload ⚡"
	@echo "  make playground-build              - Build UI only (requires Node.js)"
	@echo "  make playground-clean              - Remove build artifacts"
	@echo ""
	@echo "$(BLUE)Dependencies:$(NC)"
	@echo "  make deps                  - Check all dependencies"
	@echo "  make install-deps          - Install missing dependencies"
	@echo "  make install-python-deps   - Install required Python packages (toml, etc)"
	@echo "  make install-npm           - Install Node.js and npm"
	@echo "  make install-python        - Install Python"
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
		if ./tools/packman/python.sh -c "import toml" 2>/dev/null || ./tools/packman/python.sh -c "import tomllib" 2>/dev/null; then \
			echo "$(GREEN)✓ Python toml library is available$(NC)"; \
		else \
			echo "$(RED)✗ Python toml library is not installed$(NC)"; \
			echo "  Required for: Template system and configuration files"; \
			echo "  Run: make install-python-deps"; \
			EXIT_CODE=1; \
		fi; \
	fi

	@# Check Node.js (optional - only needed for native builds or dev mode)
	@if [ -z "$(HAS_NODE)" ]; then \
		echo "$(YELLOW)⚠ Node.js is not installed (optional - only needed for native builds/dev mode)$(NC)"; \
		echo "  Container builds work without Node.js on host"; \
		echo "  To install: make install-npm"; \
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

	@# Check npm (optional - only needed for native builds or dev mode)
	@if [ -z "$(HAS_NPM)" ]; then \
		echo "$(YELLOW)⚠ npm is not installed (optional - only needed for native builds/dev mode)$(NC)"; \
		echo "  Container builds work without npm on host"; \
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
		echo "$(RED)Some required dependencies are missing. Run 'make install-deps' to install them.$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)All core dependencies are available!$(NC)"; \
		echo "$(BLUE)Note: Node.js is optional - only needed for Kit Playground$(NC)"; \
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
	@$(MAKE) install-python-deps
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

# Install Python dependencies
.PHONY: install-python-deps
install-python-deps:
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	@if [ -f requirements.txt ]; then \
		echo "Installing core dependencies from requirements.txt..."; \
		./tools/packman/python.sh -m pip install -q -r requirements.txt || { \
			echo "$(YELLOW)Warning: Failed to install with packman Python, trying system Python...$(NC)"; \
			$(PYTHON) -m pip install --user -q -r requirements.txt || { \
				echo "$(RED)Failed to install Python dependencies$(NC)"; \
				echo "Please install manually: pip install -r requirements.txt"; \
				exit 1; \
			}; \
		}; \
		echo "$(GREEN)✓ Python dependencies installed$(NC)"; \
	else \
		echo "$(YELLOW)Warning: requirements.txt not found$(NC)"; \
	fi


# Build Kit applications
.PHONY: build
build: check-deps
	@echo "$(BLUE)Building Kit applications...$(NC)"
	@./repo.sh build

# Kit Playground - Simple Web-based Build
.PHONY: playground-build
playground-build:
	@echo "$(BLUE)Building Kit Playground UI...$(NC)"
	@if [ -z "$(HAS_NODE)" ] || [ -z "$(HAS_NPM)" ]; then \
		echo "$(RED)✗ Node.js and npm are required$(NC)"; \
		echo "  Run: make install-npm"; \
		exit 1; \
	fi
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm install
	@cd $(KIT_PLAYGROUND_DIR)/ui && npm run build
	@echo "$(GREEN)✓ Kit Playground UI built successfully!$(NC)"

# Main playground target: build and launch
# Usage: make playground          - Local access only (localhost)
#        make playground REMOTE=1 - Remote access (0.0.0.0)
.PHONY: playground
playground: playground-build
	@echo "$(BLUE)Starting Kit Playground...$(NC)"
	@if [ "$(REMOTE)" = "1" ]; then \
		echo "$(YELLOW)Starting in remote mode (listening on 0.0.0.0)$(NC)"; \
		$(PYTHON) $(KIT_PLAYGROUND_DIR)/backend/web_server.py --port 8888 --host 0.0.0.0 --open-browser; \
	else \
		$(PYTHON) $(KIT_PLAYGROUND_DIR)/backend/web_server.py --port 8888 --open-browser; \
	fi

# Development mode with hot-reload (requires Node.js on host)
.PHONY: playground-dev
playground-dev:
	@echo "$(BLUE)Starting Kit Playground in development mode...$(NC)"
	@if [ -z "$(HAS_NODE)" ] || [ -z "$(HAS_NPM)" ]; then \
		echo "$(RED)✗ Node.js and npm are required for development mode$(NC)"; \
		echo "  Run: make install-npm"; \
		exit 1; \
	fi
	@echo "$(GREEN)Launching development servers with hot-reload...$(NC)"
	@$(KIT_PLAYGROUND_DIR)/dev.sh

# Alias for dev mode
.PHONY: dev
dev: playground-dev

# Clean build artifacts
.PHONY: playground-clean
playground-clean:
	@echo "$(BLUE)Cleaning Kit Playground artifacts...$(NC)"
	@rm -rf $(KIT_PLAYGROUND_DIR)/ui/build
	@rm -rf $(KIT_PLAYGROUND_DIR)/ui/node_modules
	@echo "$(GREEN)Cleanup complete$(NC)"

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
clean-all: clean playground-clean
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
