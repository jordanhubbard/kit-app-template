# Kit Playground Development Guide

## Development Modes

### Production Mode (Full Build)
For testing the production build or when Node.js is not available:
```bash
make playground
# or
./kit_playground/playground.sh
```

This builds the React app once and serves it from the Flask backend.

### Development Mode (Hot Reload) ⚡ RECOMMENDED
For active development with instant hot-reloading:
```bash
make playground-dev
# or shortcut
make dev
# or directly
./kit_playground/dev.sh  # Linux/Mac
./kit_playground/dev.bat # Windows
```

**What happens:**
- Backend runs on `http://localhost:8081` (API server)
- Frontend runs on `http://localhost:3000` (React dev server with hot-reload)
- API calls are automatically proxied from frontend to backend
- Changes to `.tsx`, `.ts`, `.css` files reload instantly (< 1 second)
- No need to manually rebuild!

**Benefits:**
- ⚡ **Hot Module Replacement (HMR)** - Changes appear instantly without full page reload
- 🔍 **Better error messages** - See TypeScript/React errors in browser console
- 🚀 **Faster iteration** - No build step between changes
- 🎯 **Component-level updates** - Only changed components refresh

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
1. Run `make dev` once
2. Edit files in `kit_playground/ui/src/`
3. Save - changes appear instantly in browser!

### Backend Changes (Python/Flask)
1. Run `make dev` once
2. Edit files in `kit_playground/backend/`
3. Press Ctrl+C and restart `make dev` (or use a Python auto-reload tool)

### When to Use Production Build
- Testing the final bundled app
- Before creating a pull request
- When deploying to production
- When you don't have Node.js installed

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
1. Make sure you're running `make dev` (not `make playground`)
2. Check browser console for errors
3. Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)

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

### Development Flow
```
Browser (localhost:3000)
    ↓ React DevServer (Hot Reload)
    ↓ /api/* requests proxied to →
Flask Backend (localhost:8081)
    ↓
Template API / File System
```

### Production Flow
```
Browser (localhost:8888)
    ↓
Flask Backend (serves static React build)
    ↓
Template API / File System
```

## Performance Tips

1. **Use Dev Mode** - It's 10-100x faster for iteration
2. **Keep React DevTools Open** - See component updates in real-time
3. **Use Browser DevTools Network Tab** - Monitor API calls
4. **Component-Level Debugging** - Add `console.log` statements (they hot-reload!)

## Contributing

When submitting changes:
1. Test in **dev mode** (`make dev`)
2. Test **production build** (`make playground`)
3. Verify TypeScript compilation (`npm run build`)
4. Run tests if available (`npm test`)
