# Carousel and Build Fixes

## Issues Addressed

### 1. Build Endpoint 404 Error ✅ FIXED
**Problem**: Frontend was getting 404 when clicking "Build" button.

**Root Cause**: Backend was running but the `useJob` hook wasn't properly configured to call the build API.

**Fix**:
- Verified backend is running on `http://localhost:5000` (not 8000)
- Confirmed `/api/projects/build` endpoint exists and responds
- Updated `useJob.ts` to properly call the backend build endpoint with correct parameters:
  - `projectPath`: `source/apps/{projectName}`
  - `projectName`: The actual project name

**Files Modified**:
- `kit_playground/ui/src/hooks/useJob.ts`

### 2. Carousel Panel Ordering Issues ✅ FIXED
**Problem**: When navigating left through retired panels, they appeared in the wrong order, and navigation ran out before reaching the sidebar/home view.

**Root Cause**:
- Panels were being restored with simple array prepending `[restoredPanel, ...visiblePanels]`
- This didn't respect the sidebar's position or maintain proper left-to-right order

**Fix**:
- Updated `scrollLeft()` to:
  - Find the sidebar index (always first)
  - Insert restored panels **right after the sidebar** (index 1)
  - Properly calculate capacity including the restored panel's width
  - Maintain visual order: Sidebar → Restored Panels → Other Panels

**Before**:
```typescript
const newPanels = [restoredPanel, ...visiblePanels];
```

**After**:
```typescript
const sidebarIndex = visiblePanels.findIndex(p => p.type === 'template-sidebar');
const newPanels = [
  ...visiblePanels.slice(0, sidebarIndex + 1),  // Sidebar
  restoredPanel,                                 // Restored panel
  ...visiblePanels.slice(sidebarIndex + 1)      // Other panels
];
```

**Files Modified**:
- `kit_playground/ui/src/stores/panelStore.ts` (scrollLeft method)

### 3. Carousel Threshold Too Aggressive ✅ FIXED
**Problem**: Panels were retiring at 75% capacity, which was too aggressive and didn't allow for dynamic resizing or slight overflow.

**Root Cause**: The arbitrary 75% threshold didn't account for:
- CSS flexible widths (panels with `width: 0` that take remaining space)
- Natural browser layout flexibility
- User expectation of seeing more content before retirement

**Fix**:
- Increased threshold from **0.75 (75%)** to **1.2 (120%)**
- This allows panels to overflow slightly before retirement
- Gives browsers more room for dynamic resizing
- Provides better UX by showing more content

**Rationale**:
- 120% allows panel `minWidth` values to be exceeded by 20%
- CSS flexbox can handle overflow gracefully
- Users on wide monitors will see more panels simultaneously
- Retirement happens only when truly necessary

**Before**:
```typescript
const CAPACITY_THRESHOLD = 0.75; // 75%
```

**After**:
```typescript
const CAPACITY_THRESHOLD = 1.2; // 120% - allows overflow/resizing
```

**Files Modified**:
- `kit_playground/ui/src/stores/panelStore.ts`

## Testing

### Build Test
1. Create a new project (e.g., "Kit Base Editor")
2. Click the **Build** button in the editor toolbar
3. ✅ Build Output panel should open
4. ✅ Build should start automatically
5. ✅ Real-time logs should stream to the panel

### Carousel Navigation Test
1. Open "All Templates" (sidebar → template-grid)
2. Click a template (template-detail opens)
3. Click "Create Application" (project-config opens)
4. Create project (code-editor opens)
5. Click "Build" (build-output opens)
6. **Verify**: Panels should retire when capacity > 120%
7. **Verify**: Left arrow (◀) should appear when panels are retired
8. Click left arrow repeatedly
9. **Verify**: Panels restore in correct order (most recent first)
10. **Verify**: Sidebar is always visible and first
11. **Verify**: Navigation goes all the way back to template-grid

### Capacity Threshold Test
1. On a wide monitor (>1920px), open multiple panels
2. **Verify**: More panels visible before retirement
3. **Verify**: Panels can slightly overflow before retiring
4. On a narrow window, resize browser
5. **Verify**: Panels retire when width actually constrains

## Debug Logging

Enhanced console logging for carousel behavior:

```javascript
[Carousel] Capacity check: {
  totalMinWidth: 1400,
  viewportWidth: 2159,
  capacityUsed: "64.8%",
  threshold: "120%",
  visiblePanelCount: 2,
  retiredPanelCount: 1,
  shouldRetire: false
}

[Carousel] scrollLeft called, retiredPanels: 2
[Carousel] Restoring panel: template-detail Template Details
[Carousel] Restoring panel without retirement

[Carousel] canScrollLeft: true (2 retired panels)
[Carousel] canScrollRight: true (3 visible panels)

[PanelContainer] Navigation state: {
  showLeftNav: true,
  showRightNav: true,
  visiblePanelCount: 3,
  visiblePanelTypes: ['template-sidebar', 'template-detail', 'code-editor']
}
```

## Architecture Notes

### Panel Retirement Strategy
- **LIFO (Last In First Out)**: Most recently opened panels retire first
- **Leftmost First**: Panels retire from left (after sidebar) to right
- **Sidebar Protected**: Sidebar (template-sidebar) never retires
- **Capacity-Based**: Retirement triggered when `totalMinWidth > viewportWidth * 1.2`

### Navigation Arrows
- **Left Arrow (◀)**: Shows when `retiredPanels.length > 0`
- **Right Arrow (▶)**: Shows when `visiblePanels.length > 2` (sidebar + 2+ content panels)
- **Positioning**: Fixed at viewport edges with NVIDIA green styling
- **Z-index**: 50 (above panels but below modals)

### State Management
- `panels`: Currently visible panels (rendered)
- `retiredPanels`: Hidden panels stored in retirement order
- `activePanel`: Currently focused panel (highlighted)
- All mutations go through Zustand store actions for consistency

## Future Improvements

1. **Smooth Animations**: Add CSS transitions when panels retire/restore
2. **Touch Gestures**: Swipe left/right for carousel navigation on mobile
3. **Panel History**: Track panel navigation history for "back" button
4. **Keyboard Shortcuts**: Alt+Left/Right for carousel navigation
5. **Panel Persistence**: Save panel state to localStorage
6. **Adaptive Threshold**: Dynamically adjust threshold based on viewport size

## Related Documents

- `ai-docs/PANEL_CAROUSEL_SYSTEM.md` - Original carousel design spec
- `ai-docs/KIT_FILE_CREATION_BUG_FIX.md` - Template generation fixes
- `kit_playground/ui/src/stores/panelStore.ts` - Panel state management
- `kit_playground/ui/src/components/layout/PanelContainer.tsx` - Panel rendering
- `kit_playground/ui/src/hooks/useJob.ts` - Job management for builds/launches
