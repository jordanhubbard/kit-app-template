# Debugging Prompt

Use this prompt when debugging an issue.

## Quick Diagnostics

### 1. Orphaned Kit Processes
```bash
# Check for orphaned processes
ps aux | grep kit

# Kill all kit processes
pkill -9 -f kit

# Check for file locks
lsof | grep kit-app-template
```

### 2. Path Issues
```bash
# Print resolved path
python3 -c "from pathlib import Path; print(Path('path').resolve())"

# Check permissions
ls -la source/apps/

# Validate path is within base
python3 -c "
from pathlib import Path
p = Path('user/provided/path').resolve()
base = Path('base/dir').resolve()
print(str(p).startswith(str(base)))
"
```

### 3. WebSocket Not Connecting
```bash
# Check if server is running
curl http://localhost:5000/api/templates/list

# Check WebSocket in browser console
socket.on('connect', () => console.log('Connected'))
socket.on('connect_error', (err) => console.error('Error:', err))

# Backend logs
tail -f kit_playground/backend/logs/app.log
```

### 4. JSON Output Corrupted
```bash
# Test JSON mode
./repo.sh template new kit_base_editor --name test --json 2>&1 | jq .

# Check for non-JSON output
./repo.sh template new kit_base_editor --name test --json 2>&1 | grep -v "^{"
```

### 5. Tests Hanging
```bash
# Run with timeout
pytest tests/test_file.py --timeout=30

# Check for orphaned processes during test
ps aux | grep kit & pytest tests/test_file.py

# Verbose output
pytest tests/test_file.py -vv -s
```

## Debug Tools

### Python Debugger
```bash
# Interactive debugger
python3 -m pdb tools/repoman/script.py

# Pytest with pdb
pytest tests/test_file.py --pdb

# Break on failure
pytest tests/ --pdb --maxfail=1
```

### Network Debugging
```bash
# Curl with verbose
curl -v http://localhost:5000/api/endpoint

# Check port availability
lsof -i :47995

# Test WebSocket
websocat ws://localhost:5000/socket.io/
```

### Logging
```bash
# Enable debug logging
LOGLEVEL=DEBUG ./repo.sh launch app.kit

# Python logging
export PYTHONVERBOSE=1

# Flask debug mode
FLASK_ENV=development python3 web_server.py
```

## Common Issues

### Issue: Tests timeout
**Cause**: Orphaned Kit processes
**Fix**: Use process groups (os.setsid + os.killpg)

### Issue: JSON output invalid
**Cause**: Mixed stdout/stderr
**Fix**: All JSON to stdout, all other output to stderr (or suppressed in JSON mode)

### Issue: WebSocket events not received
**Cause**: Not connected or not subscribed
**Fix**: Check connection, ensure event handlers registered

### Issue: Path traversal attack
**Cause**: Not validating user paths
**Fix**: Use Path.resolve() and check prefix

### Issue: Port already in use
**Cause**: Previous process still running
**Fix**: Kill process or use different port
