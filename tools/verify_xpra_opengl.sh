#!/bin/bash
# Verify Xpra OpenGL Configuration
# This script tests if Xpra OpenGL is properly enabled

set -e

DISPLAY_NUM=${1:-100}
EXPECTED_STATE="True"

echo "=========================================="
echo "Xpra OpenGL Verification"
echo "=========================================="
echo ""
echo "Display: :$DISPLAY_NUM"
echo ""

# Check if Xpra is running
echo "1. Checking if Xpra is running on :$DISPLAY_NUM..."
if ! xpra info :$DISPLAY_NUM >/dev/null 2>&1; then
    echo "   ❌ Xpra is NOT running on :$DISPLAY_NUM"
    echo ""
    echo "   Start Xpra with:"
    echo "   xpra start :$DISPLAY_NUM --bind-tcp=0.0.0.0:10000 --html=on --opengl=yes --opengl-driver=all"
    exit 1
fi
echo "   ✅ Xpra is running"
echo ""

# Check OpenGL status
echo "2. Checking OpenGL configuration..."
OPENGL_ENABLED=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "^display.opengl.enable=" | cut -d= -f2)
OPENGL_MESSAGE=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "^display.opengl.message=" | cut -d= -f2)
OPENGL_RENDERER=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "^display.opengl.renderer=" | cut -d= -f2)
OPENGL_SUCCESS=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "^display.opengl.success=" | cut -d= -f2)
OPENGL_BACKEND=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "^display.opengl.backend=" | cut -d= -f2)

echo "   OpenGL Enabled:  $OPENGL_ENABLED"
echo "   OpenGL Message:  $OPENGL_MESSAGE"
echo "   OpenGL Renderer: $OPENGL_RENDERER"
echo "   OpenGL Success:  $OPENGL_SUCCESS"
echo "   OpenGL Backend:  $OPENGL_BACKEND"
echo ""

# Validate OpenGL is enabled
echo "3. Validating OpenGL status..."
if [ "$OPENGL_ENABLED" = "$EXPECTED_STATE" ]; then
    echo "   ✅ OpenGL is ENABLED"
    
    # Check if using hardware or software rendering
    if echo "$OPENGL_RENDERER" | grep -qi "llvmpipe\|software"; then
        echo "   ⚠️  WARNING: Using SOFTWARE rendering (slow)"
        echo "   Renderer: $OPENGL_RENDERER"
        echo ""
        echo "   This will work but performance may be poor."
        echo "   Consider using a hardware GPU for better performance."
    else
        echo "   ✅ Using HARDWARE rendering"
        echo "   Renderer: $OPENGL_RENDERER"
    fi
else
    echo "   ❌ OpenGL is DISABLED"
    echo ""
    echo "   Expected: $EXPECTED_STATE"
    echo "   Got:      $OPENGL_ENABLED"
    echo ""
    echo "   Reason: $OPENGL_MESSAGE"
    echo ""
    echo "   This will cause Kit applications to hang!"
    echo ""
    echo "   Fix:"
    echo "   1. Stop Xpra: xpra stop :$DISPLAY_NUM"
    echo "   2. Set environment variables:"
    echo "      export XPRA_OPENGL=1"
    echo "      export XPRA_OPENGL_ALLOW_GREYLISTED=1"
    echo "   3. Restart Xpra with --opengl-driver=all"
    exit 1
fi
echo ""

# Check window management
echo "4. Checking window management..."
WINDOW_COUNT=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "^state.windows=" | cut -d= -f2)
echo "   Current windows: $WINDOW_COUNT"
echo ""

# Summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""
if [ "$OPENGL_ENABLED" = "$EXPECTED_STATE" ]; then
    echo "✅ Xpra OpenGL is properly configured"
    echo "✅ Kit applications should launch successfully"
    echo ""
    echo "Test by launching a Kit application:"
    echo "  cd /home/jkh/Src/kit-app-template"
    echo "  ./repo.sh launch --name your_app.kit --xpra"
    echo ""
    echo "Check window count:"
    echo "  xpra info :$DISPLAY_NUM | grep state.windows"
    echo "  # Should increase to 1+ when app starts"
    exit 0
else
    echo "❌ Xpra OpenGL is NOT properly configured"
    echo "❌ Kit applications will HANG during startup"
    echo ""
    echo "Please fix the configuration and try again."
    exit 1
fi

