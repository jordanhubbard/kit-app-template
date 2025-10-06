# Bug Fixes - Kit Playground

## Fixed Issues

### 1. ✅ Build Output Truncation
**Problem**: Build logs were only showing first 500 characters
**Cause**: Backend was truncating stdout/stderr with `[:500]` slice
**Fix**: Removed truncation in `web_server.py` line 306-308

**Before**:
```python
logger.info(f"Build stdout: {result.stdout[:500] if result.stdout else 'none'}")
logger.info(f"Build stderr: {result.stderr[:500] if result.stderr else 'none'}")
```

**After**:
```python
logger.info("Build stdout: %s", result.stdout if result.stdout else 'none')
if result.stderr:
    logger.info("Build stderr: %s", result.stderr)
```

**Result**: Full build output now visible in console logs

---

### 2. ✅ Project Configuration File Not Found Error
**Problem**: "Project created but configuration file not found: {"error":"File does not exist"}"
**Cause**: Path calculation was using absolute path with duplicated repo root
**Fix**: Separated relative path (for build/run) from absolute path (for file reading)

**Before** (`MainLayoutWorkflow.tsx` line 424):
```typescript
const outputDir = projectInfo.outputDir || '_build/apps';
const projectPath = `${repoRoot}/${outputDir}/${projectInfo.projectName}`;
setCurrentProjectPath(projectPath); // Wrong: absolute path
```

**After**:
```typescript
const outputDir = projectInfo.outputDir || '_build/apps';

// Use relative path for currentProjectPath (for build/run operations)
const relativeProjectPath = `${outputDir}/${projectInfo.projectName}`;
setCurrentProjectPath(relativeProjectPath);

// Use absolute path for file reading
const projectPath = `${repoRoot}/${outputDir}/${projectInfo.projectName}`;
const kitFilePath = `${projectPath}/${projectInfo.projectName}.kit`;
```

**Result**:
- Build/run operations use correct relative path
- File reading uses correct absolute path
- No more "file not found" errors

---

### 3. ✅ Preview Functionality Implemented
**Problem**: Preview tab showed "Preview functionality coming soon"
**Cause**: `renderPreviewPanel()` was just a placeholder
**Fix**: Implemented actual Xpra preview rendering

**Changes**:
- Added `PreviewPane` import
- Added `previewUrl` state variable
- Captured preview URL from backend on successful run
- Implemented preview rendering with proper fallback messages

**Result**: Xpra sessions now display in the preview tab

---

## Files Modified

### Backend
- `kit_playground/backend/web_server.py`
  - Fixed build log truncation (line 305-308)

### Frontend
- `kit_playground/ui/src/components/layout/MainLayoutWorkflow.tsx`
  - Fixed project path calculation (line 420-431)
  - Added preview functionality (line 22, 49, 356, 661-693)
  - Improved error messages with correct paths

---

## Testing

### Build Logs Test
1. Select a project
2. Click Build
3. ✅ Full build output should appear in console (not truncated)

### Project Creation Test
1. Click "Create from Template"
2. Select USD Viewer or any template
3. Fill in project details
4. Click Create
5. ✅ Project should load without "file not found" error
6. ✅ Configuration file should display in editor

### Preview Test
1. Create/select a project
2. Enable "Use Xpra for browser preview" checkbox
3. Click Run
4. Navigate to Preview tab
5. ✅ Xpra session should display in iframe
6. ✅ Should show application window in browser

---

## Related Documentation
- See `WRAPPER_INTEGRATION.md` for wrapper script details
- See `XPRA_SETUP.md` for Xpra installation instructions
