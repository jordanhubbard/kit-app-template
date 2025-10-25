# Kit Playground UI Build Workflow

## Two Modes: Development vs. Production

### 🔧 Development Mode (Default)

**Command**: `make playground` or `make playground REMOTE=1`

**What Happens**:
1. ❌ **NO BUILD STEP** - Vite dev server serves files dynamically
2. ✅ **Hot Module Replacement (HMR)** - Changes auto-refresh in browser
3. ✅ **Fast iteration** - Edit code, see changes instantly
4. ✅ **Cache-Control headers** - Browser won't cache aggressively
5. ⚠️ **Not optimized** - Larger bundle, slower initial load

**File Output**: None - files served from `src/` on the fly

**When to Use**: During active development, debugging, and testing

---

### 🚀 Production Mode

**Command**: `make playground PRODUCTION=1`

**What Happens**:
1. ✅ **BUILD STEP RUNS** - `npm run build` compiles to `dist/`
2. ✅ **Optimized bundle** - Minified, tree-shaken, code-split
3. ✅ **Hash-based filenames** - `index-[hash].js` for cache busting
4. ✅ **Static files** - Served from `dist/` by preview server
5. ⚠️ **Slower iteration** - Must rebuild to see changes

**File Output**: `kit_playground/ui/dist/` directory with:
- `index.html`
- `assets/index-[hash].js`
- `assets/index-[hash].css`

**When to Use**: Production deployment, performance testing

---

## Build Commands Reference

| Command | Mode | Builds? | Output | Use Case |
|---------|------|---------|--------|----------|
| `make playground` | Dev | ❌ No | None | Development |
| `make playground REMOTE=1` | Dev | ❌ No | None | Remote dev |
| `make playground PRODUCTION=1` | Prod | ✅ Yes | `dist/` | Production |
| `make playground-build` | N/A | ✅ Yes | `dist/` | Manual build |
| `npm run build` | N/A | ✅ Yes | `dist/` | Direct build |

---

## Clean Commands

| Command | What It Cleans |
|---------|---------------|
| `make clean` | Build artifacts + playground (`dist/`, `.vite/`, `_build/`) |
| `make playground-clean` | Just playground (`dist/`, `.vite/`) |
| `make clean-all` | Everything (build + playground + user apps) |

**Important**: `make clean` now automatically includes playground cleanup!

---

## Debugging Cache Issues

### Problem: UI Not Updating After Code Changes

**In Development Mode**:
1. Check Vite is running in dev mode (look for HMR messages in logs)
2. Check browser console for HMR connection errors
3. **Browser cache should NOT be an issue** (we set `Cache-Control: no-store`)
4. If still stuck: Clear browser cache once (F12 → Application → Clear site data)
5. Enable "Disable cache" in DevTools Network tab for future

**In Production Mode**:
1. Verify you rebuilt: `make playground-build` or `make playground PRODUCTION=1`
2. Check `dist/` has new files with new hash (e.g., `index-abc123.js` changed)
3. Clear browser cache (files are hashed, so this should force reload)

---

## How Cache Busting Works

### Development Mode
```typescript
// vite.config.ts
server: {
  headers: {
    'Cache-Control': 'no-store, no-cache, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
}
```
- Tells browser: "Don't cache anything from this dev server"
- Files loaded with ?t=timestamp for extra bust
- HMR websocket triggers reload on file change

### Production Mode
```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      entryFileNames: 'assets/[name]-[hash].js',  // ← Content hash
      chunkFileNames: 'assets/[name]-[hash].js',
      assetFileNames: 'assets/[name]-[hash].[ext]',
    },
  },
}
```
- Files named by content hash (e.g., `index-Up4U-0sS.js`)
- When code changes, hash changes, new filename
- Browser loads new file automatically (old cache becomes irrelevant)

---

## Workflow Recommendations

### For Active Development
```bash
# 1. Start dev server
make playground REMOTE=1

# 2. Open browser with DevTools
#    F12 → Network tab → Check "Disable cache"

# 3. Edit code in src/
#    Changes appear automatically via HMR
```

### For Testing Production Build
```bash
# 1. Clean everything
make clean

# 2. Build and run production mode
make playground PRODUCTION=1

# 3. Test in browser (may need to clear cache once)
#    New build = new hashes = new files = no cache issues
```

### After Pulling Code Changes
```bash
# 1. Clean to remove old caches
make clean

# 2. Restart playground
make playground REMOTE=1

# 3. If browser still shows old UI:
#    Hard refresh: Ctrl+Shift+R
#    Or: F12 → Application → Clear site data
```

---

## Why This Was Confusing (Before This Fix)

### Old Behavior
1. Dev mode didn't set cache-control headers
2. Browser aggressively cached JavaScript
3. Vite HMR worked, but browser served cached files
4. Manual `npm run build` created production files, but dev server ignored them
5. Users didn't know when builds happened or what mode they were in

### New Behavior
1. Dev mode sets `Cache-Control: no-store` (no aggressive caching)
2. Production mode uses content hashes (cache-safe by design)
3. `make clean` clears ALL caches (Vite + dist + build)
4. Makefile help clearly states when builds happen
5. This document explains the full workflow

---

## Quick Troubleshooting

**UI not updating?**
1. Is Vite running? Check logs: `tail -f /tmp/kit-playground-frontend.log`
2. Dev or prod mode? Look for "Development mode" or "Production build" in startup
3. Browser DevTools open? Enable "Disable cache" in Network tab
4. Still stuck? `make clean && make playground REMOTE=1`

**Build failing?**
1. Check node/npm versions: `node --version` (need 16+)
2. Reinstall deps: `cd kit_playground/ui && rm -rf node_modules && npm install`
3. Check TypeScript errors: `cd kit_playground/ui && npm run build`

**HMR not working?**
1. Check websocket connection in browser console
2. Verify Vite is in dev mode (not preview mode)
3. Try restarting: `make playground-stop && make playground REMOTE=1`

---

## Summary

✅ **Development** = No build, HMR, no cache  
✅ **Production** = Build to dist/, hashed files, cache-safe  
✅ **`make clean`** = Cleans everything  
✅ **Cache busting** = Automatic in both modes  

**You should never need to manually clear browser cache in dev mode!**

