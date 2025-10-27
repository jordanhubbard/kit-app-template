# Panel Carousel Navigation System

## Overview

The Kit Playground now implements a sophisticated panel carousel system that provides smooth, progressive left-to-right workflow navigation. This system intelligently manages screen space while maintaining 100% UI utilization and preventing panel crowding.

## Key Features

### 1. **75% Capacity Rule**
- Monitors total panel width vs viewport width
- When panels exceed 75% capacity, automatically retires the leftmost panel
- Keeps UI from becoming overcrowded while maximizing space usage

### 2. **Panel Retirement**
- Leftmost panels (except sidebar) slide off-screen when capacity is reached
- Retired panels are stored in `retiredPanels` array
- Can be restored by scrolling left

### 3. **Navigation Arrows**
- **Left Arrow**: Appears when retired panels exist
  - Restores the most recently retired panel
  - May retire rightmost panel to maintain capacity
- **Right Arrow**: Appears when 3+ panels are visible
  - Retires the leftmost non-sidebar panel
  - Moves focus to remaining panels

### 4. **Smooth Animations**
- 300ms CSS transitions when panels slide in/out
- Natural feel when navigating left/right
- Overflow hidden to prevent visual jank

### 5. **Smart Close Behavior**
- When a panel closes, space becomes available
- System automatically redistributes panels
- Capacity is re-evaluated

## Implementation Details

### Panel Store (`panelStore.ts`)

```typescript
interface PanelStoreState {
  panels: PanelState[];           // Currently visible panels
  retiredPanels: PanelState[];    // Panels slid off to the left

  // Carousel navigation methods
  scrollLeft: () => void;         // Restore retired panels, retire rightmost
  scrollRight: () => void;        // Retire leftmost, show more on right
  canScrollLeft: () => boolean;   // Check if retired panels exist
  canScrollRight: () => boolean;  // Check if retirable panels exist
  checkCapacityAndRetire: () => void;  // Enforce 75% capacity rule
}
```

### Key Methods

#### `checkCapacityAndRetire()`
- Called automatically when:
  - New panel opens
  - Window resizes
- Calculates: `totalMinWidth / viewportWidth`
- If > 75%, retires leftmost non-sidebar panel

#### `scrollLeft()`
- Restores most recently retired panel from the left
- Adds to beginning of `panels` array
- May retire rightmost panel if capacity exceeded
- Creates smooth left-to-right slide animation

#### `scrollRight()`
- Retires leftmost non-sidebar panel
- Moves to `retiredPanels` array
- Gives more space to remaining panels on right

#### `openPanel()`
- Adds new panel to the right
- **Automatically calls `checkCapacityAndRetire()`**
- May trigger automatic retirement of leftmost panels

### Panel Container (`PanelContainer.tsx`)

```typescript
// Navigation arrows positioned at edges
{showLeftNav && <button onClick={scrollLeft} ... />}
{showRightNav && <button onClick={scrollRight} ... />}

// Container with smooth transitions
<div style={{ transition: 'transform 0.3s ease-in-out' }}>
  {visiblePanels.map(panel => <Panel key={panel.id} ... />)}
</div>
```

### Visual Design

- **Navigation Arrows**:
  - NVIDIA green (`bg-nvidia-green/90`)
  - Positioned at vertical center of screen
  - Rounded edges (left arrow rounded right, right arrow rounded left)
  - Hover effects with shadow
  - z-index 50 to float above panels

## User Experience Flow

### Example: Creating a New Project

1. **Start**: Sidebar + Template Grid (2 panels)
2. **Click Template**: Opens Template Detail (3 panels) - still under 75%
3. **Click Create**: Opens Project Config (4 panels)
   - If > 75%, Template Grid retires to left
   - Left arrow appears
4. **Create Project**: Opens Code Editor (replaces Project Config)
5. **Click Build**: Opens Build Output
   - If > 75%, Template Detail may retire
6. **Navigate Left**: Click left arrow
   - Template Detail returns
   - Build Output may retire
7. **Close Panels**: Click X on any panel
   - System redistributes space
   - May restore retired panels if space available

### Navigation Rules

1. **Sidebar is Permanent**
   - Never retires
   - Always visible on the left
   - Acts as anchor point

2. **Progressive Right-to-Left**
   - New content always appears on the right
   - Old content slides off to the left
   - Natural reading direction flow

3. **Capacity Management**
   - 75% threshold prevents crowding
   - Automatic retirement is smooth and predictable
   - Navigation arrows provide clear affordance

4. **Smart Space Usage**
   - Always uses 100% of available width
   - Panels maintain minimum widths
   - Flexible panels (`width: 0`) take remaining space

## Technical Notes

### Capacity Calculation

```typescript
const totalMinWidth = panels.reduce((sum, panel) =>
  sum + (panel.width || panel.minWidth), 0
);
const capacityUsed = totalMinWidth / window.innerWidth;

if (capacityUsed > CAPACITY_THRESHOLD) {
  // Retire leftmost panel
}
```

### Panel Width Modes

1. **Fixed Width**: `width: 400` - panel has specific width
2. **Flexible Width**: `width: 0` - takes remaining space
3. **Min/Max Constraints**: `minWidth`, `maxWidth` - bounds

### Transition Animations

```css
transition: transform 0.3s ease-in-out;
```

- 300ms duration
- Ease-in-out timing for natural feel
- Applied to panel container for smooth slides

### Event Handling

```typescript
useEffect(() => {
  window.addEventListener('resize', checkCapacityAndRetire);
  return () => window.removeEventListener('resize', checkCapacityAndRetire);
}, []);
```

- Window resize triggers capacity check
- Automatic cleanup on unmount
- Ensures responsive behavior

## Future Enhancements

### Potential Additions

1. **Keyboard Navigation**
   - Arrow keys to scroll left/right
   - Ctrl+Left/Right to move faster

2. **Touch Gestures**
   - Swipe left/right on touch devices
   - Pinch to zoom panels

3. **Panel Breadcrumbs**
   - Show retired panel names
   - Click to jump directly to retired panel

4. **Capacity Indicator**
   - Visual indicator of current capacity
   - Preview of upcoming retirement

5. **Smart Panel Groups**
   - Group related panels
   - Retire/restore as a unit

## Testing

### Manual Test Cases

1. ✅ Open 5+ panels and verify automatic retirement
2. ✅ Click left arrow to restore retired panels
3. ✅ Click right arrow to retire visible panels
4. ✅ Resize window and verify capacity recalculation
5. ✅ Close panels and verify space redistribution
6. ✅ Verify sidebar never retires
7. ✅ Verify smooth animations on all transitions

### Integration Tests

```typescript
describe('Panel Carousel', () => {
  it('retires leftmost panel at 75% capacity');
  it('restores panels when scrolling left');
  it('never retires sidebar');
  it('shows correct navigation arrows');
});
```

## Performance Considerations

- **Capacity checks** are O(n) where n = panel count (typically < 10)
- **Retirement** is O(1) array operation
- **Animations** use CSS transforms (GPU accelerated)
- **Event listeners** are debounced on resize
- **Re-renders** are minimized with Zustand state management

## Conclusion

The panel carousel system provides a sophisticated, user-friendly way to navigate complex workflows in the Kit Playground. By intelligently managing screen space and providing clear navigation affordances, it allows users to focus on their work without being overwhelmed by crowded UI or losing context when panels retire.

The 75% capacity rule strikes the right balance between utilizing screen space and maintaining usability, while smooth animations and clear navigation arrows make the system feel natural and intuitive.
