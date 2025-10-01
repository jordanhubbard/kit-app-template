#!/bin/bash
# Test script to verify backend starts correctly
cd "$(dirname "$0")"
echo "Testing Kit Playground backend..."
echo "Starting backend server on port 8083..."
python3 backend/web_server.py --port 8083 </dev/null >backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 3

# Test if server is responding
echo "Testing /api/health endpoint..."
HEALTH=$(curl -s http://localhost:8083/api/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    echo "✓ Backend is running!"
    echo "$HEALTH"
else
    echo "✗ Backend failed to start"
    echo "Backend log:"
    cat backend.log
fi

# Test templates endpoint
echo ""
echo "Testing /api/templates endpoint..."
TEMPLATES=$(curl -s http://localhost:8083/api/templates 2>/dev/null)
if [ -n "$TEMPLATES" ]; then
    echo "$TEMPLATES" | python3 -m json.tool 2>/dev/null | head -50
else
    echo "Failed to get templates"
fi

# Cleanup
kill $BACKEND_PID 2>/dev/null
wait $BACKEND_PID 2>/dev/null
rm -f backend.log
echo ""
echo "Backend test complete."
