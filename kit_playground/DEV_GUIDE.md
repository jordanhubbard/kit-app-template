# Kit Playground Development Guide

## Running the Playground

Kit Playground **always runs in development mode** with hot-reload enabled:

```bash
make playground          # Local access (localhost only)
make playground REMOTE=1 # Remote access (all interfaces)

# Or directly:
./kit_playground/dev.sh  # Linux/Mac
./kit_playground/dev.bat # Windows
```

**What runs:**
- Backend API server on `http://localhost:8081` (Flask)
- Frontend dev server on `http://localhost:3000` (React with hot-reload)
- API calls automatically proxied from frontend → backend
- Changes to `.tsx`, `.ts`, `.css` files reload instantly (< 1 second)

**Why always development mode?**
- ⚡ **Instant feedback** - Changes appear in < 1 second
- 🔍 **Better debugging** - See TypeScript/React errors in console
- 🚀 **Faster workflow** - No build step between changes
- 🎯 **Component-level HMR** - Only changed components refresh
- 💾 **Saves time** - No need to wait for production builds

**Production builds are optional** and only needed for:
- Creating deployment artifacts
- Testing the build process itself
- CI/CD pipelines

## Project Structure

```
kit_playground/
├── backend/          # Flask API server (Python)
│   ├── web_server.py # Main server
│   └── requirements.txt
├── ui/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── store/       # Redux state management
│   │   └── services/    # API clients
│   ├── public/
│   ├── package.json     # Now includes proxy config
│   └── build/           # Production build output
├── dev.sh            # Development mode launcher (Linux/Mac)
├── dev.bat           # Development mode launcher (Windows)
└── playground.sh     # Production mode launcher
```

## Making Changes

### Frontend Changes (React/TypeScript)
1. Run `make playground` once
2. Edit files in `kit_playground/ui/src/`
3. Save - changes appear instantly in browser! ⚡

### Backend Changes (Python/Flask)
1. Run `make playground` once
2. Edit files in `kit_playground/backend/`
3. Press Ctrl+C and restart `make playground` (or use a Python auto-reload tool)

### Optional: Production Build

Only needed if you're testing the build process or creating deployment artifacts:

```bash
make playground-build  # Creates optimized bundle in ui/build/
```

**You don't need this for normal development!** Always use `make playground` instead.

## Common Tasks

### Install Dependencies
```bash
# Backend (Python)
pip3 install -r kit_playground/backend/requirements.txt

# Frontend (Node.js)
cd kit_playground/ui
npm install
```

### Clean Build Artifacts
```bash
make playground-clean
```

### Build for Production
```bash
make playground-build
```

### View Backend Logs (Dev Mode)
```bash
tail -f /tmp/playground-backend.log
```

## Troubleshooting

### Port Already in Use
If port 3000 or 8081 is in use:
```bash
# Find and kill processes
lsof -ti:3000 | xargs kill
lsof -ti:8081 | xargs kill
```

### Changes Not Appearing
1. Check browser console for errors
2. Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)
3. Restart: Press Ctrl+C and run `make playground` again

### API Calls Failing
- Dev mode proxies `/api/*` to `http://localhost:8081`
- Make sure backend is running (check `/tmp/playground-backend.log`)
- Verify backend URL in `ui/package.json` proxy setting

### TypeScript Errors
```bash
cd kit_playground/ui
npm run build  # Check for compilation errors
```

## Architecture

### Standard Flow (Always Used)
```
Browser (localhost:3000)
    ↓ React DevServer (Hot Reload ⚡)
    ↓ /api/* requests proxied to →
Flask Backend (localhost:8081)
    ↓
Template API / File System / Xpra
```

**No production mode needed!** Development mode is fast enough for all use cases.

## Performance Tips

1. **Use Dev Mode** - It's 10-100x faster for iteration
2. **Keep React DevTools Open** - See component updates in real-time
3. **Use Browser DevTools Network Tab** - Monitor API calls
4. **Component-Level Debugging** - Add `console.log` statements (they hot-reload!)

## Contributing

When submitting changes:
1. Test changes (`make playground`)
2. Verify TypeScript compilation (`cd kit_playground/ui && npm run build`)
3. Run tests if available (`npm test`)
4. Commit and push
