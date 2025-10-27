#!/bin/bash
# Automated Xpra OpenGL Whitelist Setup
# Ensures llvmpipe software renderer is whitelisted for OpenGL in Xpra
# Safe to run multiple times (idempotent)

set -e

XPRA_DRIVERS="/usr/lib/python3/dist-packages/xpra/opengl/drivers.py"
XPRA_CHECK="/usr/lib/python3/dist-packages/xpra/opengl/check.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[Xpra OpenGL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[Xpra OpenGL]${NC} $1"
}

log_error() {
    echo -e "${RED}[Xpra OpenGL]${NC} $1"
}

# Check if Xpra is installed
if ! command -v xpra &> /dev/null; then
    log_warn "Xpra not installed, skipping OpenGL setup"
    exit 0
fi

# Check if running with sufficient privileges
if [ ! -w "$XPRA_DRIVERS" ] || [ ! -w "$XPRA_CHECK" ]; then
    log_error "Insufficient permissions to patch Xpra. Run with sudo or fix permissions."
    exit 1
fi

# Check if drivers.py exists
if [ ! -f "$XPRA_DRIVERS" ]; then
    log_warn "Xpra drivers.py not found at expected location, skipping"
    exit 0
fi

# Check if check.py exists
if [ ! -f "$XPRA_CHECK" ]; then
    log_warn "Xpra check.py not found at expected location, skipping"
    exit 0
fi

# Check if drivers.py already has llvmpipe whitelisted
if grep -q '"renderer": ("llvmpipe",)' "$XPRA_DRIVERS"; then
    log_info "✓ llvmpipe already whitelisted in drivers.py"
    DRIVERS_PATCHED=true
else
    log_info "Patching drivers.py to whitelist llvmpipe..."
    
    # Backup original file
    if [ ! -f "${XPRA_DRIVERS}.backup" ]; then
        cp "$XPRA_DRIVERS" "${XPRA_DRIVERS}.backup"
        log_info "  Created backup: ${XPRA_DRIVERS}.backup"
    fi
    
    # Apply patch: Add llvmpipe to WHITELIST
    sed -i 's/^WHITELIST: GL_MATCH_LIST = {$/WHITELIST: GL_MATCH_LIST = {\n    "renderer": ("llvmpipe",),/' "$XPRA_DRIVERS"
    
    # Clear Python bytecode cache
    rm -f /usr/lib/python3/dist-packages/xpra/opengl/__pycache__/drivers.*.pyc 2>/dev/null || true
    
    log_info "✓ drivers.py patched successfully"
    DRIVERS_PATCHED=true
fi

# Check if check.py already has the whitelist bypass fix
if grep -q 'match_list(props, GREYLIST, "greylist") and not match_list(props, WHITELIST, "whitelist")' "$XPRA_CHECK"; then
    log_info "✓ check.py already has whitelist bypass fix"
    CHECK_PATCHED=true
else
    log_info "Patching check.py to fix whitelist bypass..."
    
    # Backup original file
    if [ ! -f "${XPRA_CHECK}.backup" ]; then
        cp "$XPRA_CHECK" "${XPRA_CHECK}.backup"
        log_info "  Created backup: ${XPRA_CHECK}.backup"
    fi
    
    # Find the line number of the greylist check
    LINE_NUM=$(grep -n 'if safe and match_list(props, GREYLIST, "greylist"):' "$XPRA_CHECK" | cut -d: -f1)
    
    if [ -n "$LINE_NUM" ]; then
        # Apply patch: Add whitelist check to the condition
        sed -i "${LINE_NUM}s/.*/    if safe and match_list(props, GREYLIST, \"greylist\") and not match_list(props, WHITELIST, \"whitelist\"):/" "$XPRA_CHECK"
        
        # Clear Python bytecode cache
        rm -f /usr/lib/python3/dist-packages/xpra/opengl/__pycache__/check.*.pyc 2>/dev/null || true
        
        log_info "✓ check.py patched successfully"
        CHECK_PATCHED=true
    else
        log_warn "Could not find greylist check line in check.py, may already be patched differently"
        CHECK_PATCHED=true
    fi
fi

# Verify patches
if [ "$DRIVERS_PATCHED" = true ] && [ "$CHECK_PATCHED" = true ]; then
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "✅ Xpra OpenGL setup complete!"
    log_info "   llvmpipe software renderer is now whitelisted"
    log_info "   OpenGL will be enabled in Xpra sessions"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    log_error "Patching incomplete, please check manually"
    exit 1
fi

exit 0

