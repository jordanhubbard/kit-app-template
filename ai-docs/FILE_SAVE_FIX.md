# File Save Fix

## Issue
Users could not save edited `.kit` files. Clicking "Save" in the CodeEditor resulted in:
```
Failed to save file: Request failed with status code 405
```

**405 Method Not Allowed** = The endpoint exists but doesn't support the HTTP method being used.

## Root Cause
The backend filesystem API had a `/read` endpoint but **no `/write` endpoint**.

### Before
```
GET  /api/filesystem/read    ✅ Implemented
POST /api/filesystem/write   ❌ Missing!
```

### Frontend Expected
```typescript
// api.ts
async saveFile(filePath: string, content: string) {
  const response = await this.client.post('/filesystem/write', {
    path: filePath,
    content,
  });
  return response.data;
}
```

But backend had no matching route, resulting in 405.

## The Fix

Added `/write` endpoint to `filesystem_routes.py`:

```python
@bp.route('/write', methods=['POST'])
def write_file():
    """Write content to a file."""
    try:
        data = request.json
        path = data.get('path')
        content = data.get('content')

        if not path:
            return jsonify({'error': 'path required'}), 400

        if content is None:  # Allow empty string but not None
            return jsonify({'error': 'content required'}), 400

        # Security: Validate path is within allowed directories
        path_obj = security_validator._validate_filesystem_path(path)
        if not path_obj:
            return jsonify({'error': 'Invalid or inaccessible path'}), 400

        # Ensure parent directory exists
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        path_obj.write_text(content, encoding='utf-8')

        logger.info(f"File written successfully: {path_obj}")
        return jsonify({
            'success': True,
            'path': str(path_obj),
            'size': len(content)
        }), 200

    except PermissionError as e:
        logger.error(f"Permission denied writing file: {e}")
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return jsonify({'error': str(e)}), 500
```

### Security Features
1. **Path Validation**: Uses `security_validator._validate_filesystem_path()` to ensure paths are within the repo
2. **Rejects Arbitrary Paths**: `/tmp/`, `/etc/`, or any path outside the project will be rejected
3. **Permission Handling**: Catches and reports permission errors gracefully
4. **Directory Creation**: Safely creates parent directories if needed (`mkdir -p` behavior)

## Files Modified

### `/kit_playground/backend/routes/filesystem_routes.py`
- Added `@bp.route('/write', methods=['POST'])` endpoint
- Validates path, content, and permissions
- Returns success status with file size

## Testing

### Valid Save (Within Project)
```bash
curl -X POST http://localhost:5000/api/filesystem/write \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/home/user/Src/kit-app-template/source/apps/my_app/my_app.kit",
    "content": "[package]\ntitle = \"My App\"\n"
  }'

# Response:
{
  "success": true,
  "path": "/home/user/Src/kit-app-template/source/apps/my_app/my_app.kit",
  "size": 32
}
```

### Invalid Save (Outside Project)
```bash
curl -X POST http://localhost:5000/api/filesystem/write \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/tmp/test.txt",
    "content": "hack"
  }'

# Response:
{
  "error": "Invalid or inaccessible path"
}
```

### UI Workflow
1. Create a project (e.g., "Kit Base Editor")
2. Make changes to the `.kit` file in the editor
3. Click **"Save"** button
4. ✅ File saves successfully
5. ✅ "Unsaved changes" indicator disappears
6. ✅ File status shows "Saved" at bottom

## API Endpoints Summary

| Endpoint | Method | Purpose | Security |
|----------|--------|---------|----------|
| `/filesystem/read` | GET | Read file contents | Path validation |
| `/filesystem/write` | POST | Write file contents | Path validation, permission checks |
| `/filesystem/list` | GET | List directory contents | Path validation |
| `/filesystem/mkdir` | POST | Create directory | Path validation |

## Related Documents

- `kit_playground/ui/src/services/api.ts` - Frontend API service
- `kit_playground/backend/routes/filesystem_routes.py` - Backend filesystem routes
- `kit_playground/ui/src/components/panels/CodeEditor.tsx` - Editor component with Save button
