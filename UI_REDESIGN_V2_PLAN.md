# Kit App Template Playground - UI Redesign V2
## Progressive Disclosure + Visual Browsing

**Date**: October 25, 2025
**Status**: Planning
**Goal**: Transform the UI into a VSCode-style progressive disclosure interface with NVIDIA NIM-style visual browsing

---

## 🎯 Vision

### Current Problems
1. **Flat navigation** - No progressive disclosure, everything in separate pages
2. **Text-heavy** - Templates shown as text lists, not visually engaging
3. **Disconnected flow** - Create → Build → Launch feel like separate actions
4. **No context** - Each step loses context from previous steps
5. **Not a "playground"** - Feels like a form, not an exploration tool

### Target Experience
1. **Left-to-right panels** - VSCode-style progressive reveal
2. **Visual browsing** - NVIDIA NIM-style card layouts with imagery
3. **Contextual actions** - Actions appear based on current selection
4. **Seamless flow** - Create → Configure → Build → Launch in one view
5. **True playground** - Exploration, experimentation, visual feedback

---

## 🏗️ Architecture: Panel-Based Progressive Disclosure

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Header: Kit App Template Playground                     [Jobs] [Docs]   │
├──────────┬──────────────────┬──────────────────┬──────────────────┬─────┤
│          │                  │                  │                  │     │
│ PANEL 1  │ PANEL 2         │ PANEL 3         │ PANEL 4         │ ... │
│ Always   │ Opens on        │ Opens on        │ Opens on        │     │
│ Visible  │ Selection       │ Action          │ Next Action     │     │
│          │                  │                  │                  │     │
│ ┌──────┐ │ ┌──────────────┐│ ┌──────────────┐│ ┌──────────────┐│     │
│ │Search││ │ Template     ││ │ Configuration││ │ Build Output ││     │
│ └──────┘ │ │ Details      ││ │ Editor       ││ │ & Logs       ││     │
│          │ │              ││ │              ││ │              ││     │
│ Templates│ │ [Create]     ││ │ [Build]      ││ │ [Launch]     ││     │
│ ├─App   │ │ [Edit .kit]  ││ │ [Save]       ││ │ [Stream]     ││     │
│ ├─Ext   │ │ [Docs]       ││ │              ││ │              ││     │
│ └─Svc   │ └──────────────┘│ └──────────────┘│ └──────────────┘│     │
│          │                  │                  │                  │     │
└──────────┴──────────────────┴──────────────────┴──────────────────┴─────┘
```

### Panel Flow Examples

**Example 1: Browse → Create**
```
Panel 1 (Always)     Panel 2 (On Click)           Panel 3 (On Create)
┌──────────────┐    ┌───────────────────────┐    ┌─────────────────┐
│ 🔍 Search    │    │ Kit Base Editor       │    │ Creating...     │
├──────────────┤    ├───────────────────────┤    ├─────────────────┤
│ Applications │ -> │ [Visual Preview]      │ -> │ ✓ Created       │
│ ┌──────────┐ │    │                       │    │ my_app.kit      │
│ │●Kit Base │ │    │ Tags: editor, usd     │    │                 │
│ └──────────┘ │    │                       │    │ [Edit .kit]     │
│ ┌──────────┐ │    │ [Create Application]  │    │ [Build]         │
│ │ USD View │ │    │  Name: ___________    │    └─────────────────┘
│ └──────────┘ │    │  Output: _________    │
└──────────────┘    │  ☑ Streaming          │
                    └───────────────────────┘
```

**Example 2: Edit → Build → Launch**
```
Panel 1              Panel 2                Panel 3              Panel 4
┌──────────────┐    ┌──────────────────┐    ┌────────────────┐  ┌──────────────┐
│ My Projects  │    │ my_app           │    │ Building...    │  │ Streaming    │
├──────────────┤    ├──────────────────┤    ├────────────────┤  ├──────────────┤
│ ┌──────────┐ │    │ [Edit .kit]      │    │ ▓▓▓▓▓▓░░ 75%  │  │ ✓ Ready      │
│ │●my_app   │ │ -> │ [Build]          │ -> │                │->│ [Preview]    │
│ └──────────┘ │    │ [Launch]         │    │ Log:           │  │              │
│ ┌──────────┐ │    │ [Delete]         │    │ Compiling...   │  │ 🖼️ [Live]   │
│ │ test_app │ │    │                  │    └────────────────┘  └──────────────┘
│ └──────────┘ │    │ Status: Built    │
└──────────────┘    │ Type: Application│
                    └──────────────────┘
```

---

## 🎨 Visual Design: NVIDIA NIM-Style Cards

### Template Browser (Panel 1)

```
┌─────────────────────────────────────────┐
│ 🔍 Search templates...                  │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────┐ ┌─────────────┐       │
│ │ 🎮          │ │ 🔧          │       │ <- Icons/Thumbnails
│ │ Kit Base    │ │ USD Viewer  │       │
│ │ Editor      │ │             │       │
│ │             │ │ #usd #view  │       │
│ │ #editor     │ │             │       │
│ │ [Quick →]   │ │ [Quick →]   │       │
│ └─────────────┘ └─────────────┘       │
│                                         │
│ ┌─────────────┐ ┌─────────────┐       │
│ │ 🚀          │ │ ⚡          │       │
│ │ USD         │ │ Kit         │       │
│ │ Explorer    │ │ Service     │       │
│ │             │ │             │       │
│ │ #3d #nav    │ │ #service    │       │
│ │ [Quick →]   │ │ [Quick →]   │       │
│ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────┘
```

### Card Design Specification

```typescript
interface TemplateCard {
  // Visual
  icon: string;           // Emoji or SVG
  thumbnail?: string;     // Optional preview image
  gradient: string;       // Background gradient (like NIM cards)

  // Content
  name: string;
  description: string;
  tags: string[];

  // Actions
  quickActions: Action[]; // [Create, Docs, Clone]

  // Metadata
  type: 'app' | 'ext' | 'service';
  popularity?: number;    // Usage count
  lastUsed?: Date;
}
```

### Visual Hierarchy

```
Category Filters (Tabs)
├── Applications     [Most prominent]
├── Extensions
└── Microservices

Sort Options
├── Alphabetical
├── Recently Used
├── Most Popular
└── Type

Card States
├── Default          [Subtle shadow]
├── Hover            [Lift + highlight]
├── Selected         [Green border]
└── Creating         [Pulsing animation]
```

---

## 🎬 User Flows

### Flow 1: First-Time User - Create Application

**Step 1: Browse Templates**
- User sees visual card grid
- Hover shows more info
- Tags help identify capabilities
- "Quick Create" button on each card

**Step 2: Click Template**
- Panel 2 slides in from right
- Shows larger preview + detailed description
- "Create Application" form appears
- Options: Name, Output Dir, Streaming toggle

**Step 3: Create**
- Panel 3 slides in
- Shows creation progress
- Success: Shows created files
- Quick actions: [Edit .kit] [Build Now]

**Step 4: Build** (Optional)
- Panel 4 slides in
- Shows build progress with logs
- Success: [Launch] [Launch with Streaming]

**Step 5: Launch**
- Panel 5 (or modal) opens
- Shows streaming URL or local preview
- Live application preview (if streaming)

### Flow 2: Power User - Iterate Existing App

**Step 1: My Projects**
- Panel 1 shows "My Projects" tab
- Lists all created applications
- Status badges: Built, Running, Failed

**Step 2: Select Project**
- Panel 2 shows project details
- Quick actions: Edit, Build, Launch, Delete
- Shows last build time, status

**Step 3: Edit .kit**
- Panel 3 opens code editor
- Syntax highlighting for .kit files
- Real-time validation
- [Save] [Build After Save]

**Step 4: Auto-build**
- Panel 4 shows build output
- Auto-launches on success (if configured)

### Flow 3: Advanced - Multi-Template Workflow

**Panel 1**: Template browser
**Panel 2**: Create extension
**Panel 3**: Add to existing app
**Panel 4**: Build combined
**Panel 5**: Launch preview

---

## 🛠️ Technical Implementation

### Phase 1: Layout Foundation (Week 1)
**Goal**: Implement panel-based layout system

#### Deliverables
1. **New Layout Components**
   ```
   src/components/layout/
   ├── PanelContainer.tsx      - Container for all panels
   ├── Panel.tsx               - Individual panel component
   ├── PanelHeader.tsx         - Panel header with actions
   └── PanelResizer.tsx        - Drag-to-resize between panels
   ```

2. **Panel State Management**
   ```typescript
   interface PanelState {
     id: string;
     type: 'template-browser' | 'template-detail' |
           'project-config' | 'build-output' | 'preview';
     width: number;
     data: any;
     isVisible: boolean;
   }

   interface PanelStore {
     panels: PanelState[];
     activePanel: string;

     openPanel(type, data): void;
     closePanel(id): void;
     resizePanel(id, width): void;
   }
   ```

3. **Responsive Behavior**
   - Desktop: Up to 5 panels side-by-side
   - Tablet: Max 3 panels, scroll horizontally
   - Mobile: Stack panels vertically

#### Files to Create/Modify
- `src/components/layout/PanelContainer.tsx` (NEW)
- `src/components/layout/Panel.tsx` (NEW)
- `src/stores/panelStore.ts` (NEW - Zustand or Context)
- `src/App.tsx` (MODIFY - Replace router with panel system)

---

### Phase 2: Visual Template Browser (Week 2)
**Goal**: NVIDIA NIM-style card grid

#### Deliverables
1. **Card Components**
   ```
   src/components/templates/
   ├── TemplateCard.tsx        - Visual card component
   ├── TemplateGrid.tsx        - Grid layout with filtering
   ├── TemplateFilters.tsx     - Category tabs + sort
   └── TemplateSearch.tsx      - Search with live filtering
   ```

2. **Card Visuals**
   - Icon system (emoji or custom SVG)
   - Gradient backgrounds (per template type)
   - Hover effects (lift, glow, scale)
   - Loading skeletons

3. **Template Metadata Enhancement**
   - Add icon/thumbnail URLs to template API
   - Add tags/categories
   - Track usage statistics
   - Store preview images

#### API Changes
```typescript
// Backend: Enhance template metadata
interface TemplateInfo {
  // Existing fields...

  // NEW Visual fields
  icon?: string;           // Emoji or icon name
  thumbnail?: string;      // URL to preview image
  gradient?: string;       // CSS gradient
  tags: string[];          // Searchable tags
  category: string;        // For filtering

  // NEW Stats
  usageCount?: number;     // How many times created
  lastUsed?: Date;         // Last creation date
}
```

#### Files to Create/Modify
- `src/components/templates/TemplateCard.tsx` (NEW)
- `src/components/templates/TemplateGrid.tsx` (NEW)
- `backend/routes/template_routes.py` (MODIFY - Add metadata)
- `tools/repoman/template_engine.py` (MODIFY - Track usage)

---

### Phase 3: Template Detail Panel (Week 2-3)
**Goal**: Rich detail view with quick actions

#### Deliverables
1. **Detail Panel Component**
   ```
   src/components/templates/
   ├── TemplateDetail.tsx      - Main detail view
   ├── TemplatePreview.tsx     - Large preview/screenshot
   ├── TemplateActions.tsx     - Quick action buttons
   └── TemplateDocs.tsx        - Embedded documentation
   ```

2. **Quick Create Flow**
   - Inline form for project creation
   - Smart defaults (auto-generate names)
   - Real-time validation
   - Progressive options (basic → advanced)

3. **Visual Feedback**
   - Animated transitions between panels
   - Progress indicators
   - Success/error toasts
   - Confetti on first successful create 🎉

---

### Phase 4: Project Management Panel (Week 3)
**Goal**: Manage existing applications

#### Deliverables
1. **My Projects View**
   ```
   src/components/projects/
   ├── ProjectList.tsx         - List of user projects
   ├── ProjectCard.tsx         - Individual project card
   ├── ProjectDetail.tsx       - Project detail panel
   └── ProjectActions.tsx      - Edit, Build, Launch, Delete
   ```

2. **Project Status**
   - Visual status badges (Built, Running, Failed)
   - Last modified timestamp
   - Build/launch history
   - Quick stats (build time, size)

3. **Project Actions**
   - Edit .kit file (opens code editor panel)
   - Build (opens build output panel)
   - Launch (opens preview panel)
   - Delete (with confirmation)

---

### Phase 5: Code Editor Panel (Week 4)
**Goal**: In-browser .kit file editing

#### Deliverables
1. **Monaco Editor Integration**
   ```bash
   npm install @monaco-editor/react
   ```

2. **Editor Features**
   - Syntax highlighting for .kit files (TOML)
   - Auto-completion for extensions
   - Real-time validation
   - Diff view for changes
   - [Save] [Save & Build] actions

3. **Editor Panel**
   ```
   src/components/editor/
   ├── KitFileEditor.tsx       - Monaco wrapper
   ├── EditorToolbar.tsx       - Save, Format, Undo/Redo
   └── ValidationPanel.tsx     - Show errors/warnings
   ```

---

### Phase 6: Build & Launch Panels (Week 4-5)
**Goal**: Real-time build output and live preview

#### Deliverables
1. **Build Output Panel**
   - WebSocket streaming of logs
   - ANSI color support
   - Auto-scroll with manual override
   - Build progress bar
   - [Cancel Build] [Launch on Success]

2. **Preview Panel**
   - Kit App Streaming preview (iframe)
   - Connection status indicator
   - [Open in New Tab] action
   - [Stop Application] action

3. **Multi-Panel Coordination**
   - Build success → Auto-open preview panel
   - Application running → Show live indicator
   - Error → Highlight relevant panel

---

## 🎨 Design System

### Color Palette (NVIDIA-Inspired)

```css
/* Primary */
--nvidia-green: #76b900;
--nvidia-green-dark: #5a9100;
--nvidia-green-light: #8fd400;

/* Backgrounds */
--bg-dark: #0f0f0f;
--bg-panel: #1a1a1a;
--bg-card: #252525;
--bg-card-hover: #2d2d2d;

/* Borders */
--border-subtle: rgba(255, 255, 255, 0.1);
--border-panel: rgba(255, 255, 255, 0.15);
--border-active: var(--nvidia-green);

/* Text */
--text-primary: #ffffff;
--text-secondary: #b3b3b3;
--text-muted: #808080;

/* Status */
--status-success: #76b900;
--status-warning: #ffb700;
--status-error: #ff5252;
--status-info: #00b8d4;
```

### Typography

```css
/* Headers */
--font-display: 'Inter', -apple-system, system-ui, sans-serif;
--font-body: 'Inter', -apple-system, system-ui, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Sizes */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 1.875rem;
```

### Spacing

```css
/* Consistent spacing scale */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
```

### Panel Dimensions

```css
/* Default panel widths */
--panel-min: 240px;
--panel-template-browser: 280px;
--panel-detail: 400px;
--panel-editor: 600px;
--panel-output: 500px;
--panel-preview: 800px;
```

---

## 📋 Implementation Checklist

### Phase 1: Layout Foundation ✓ (Week 1)
- [ ] Create `PanelContainer` component
- [ ] Create `Panel` component with resize handles
- [ ] Implement panel state management (Zustand)
- [ ] Add panel open/close/resize logic
- [ ] Responsive breakpoints for mobile/tablet
- [ ] Panel transition animations
- [ ] Test: Open 5 panels, resize, close, reopen

### Phase 2: Visual Template Browser (Week 2)
- [ ] Design template card component
- [ ] Implement card grid with masonry layout
- [ ] Add category filters (Apps, Exts, Services)
- [ ] Add search with fuzzy matching
- [ ] Add sort options (A-Z, Recent, Popular)
- [ ] Implement hover effects and animations
- [ ] Add loading skeletons
- [ ] Backend: Enhance template metadata API
- [ ] Test: Filter by category, search, sort

### Phase 3: Template Detail Panel (Week 2-3)
- [ ] Create template detail panel component
- [ ] Add large preview/thumbnail display
- [ ] Create inline creation form
- [ ] Add streaming toggle and advanced options
- [ ] Implement real-time validation
- [ ] Add success animations (confetti!)
- [ ] Connect to backend create API
- [ ] Test: Create app, create ext, create service

### Phase 4: Project Management Panel (Week 3)
- [ ] Create "My Projects" tab in Panel 1
- [ ] Implement project list with cards
- [ ] Add project status badges
- [ ] Create project detail panel
- [ ] Add quick actions (Edit, Build, Launch, Delete)
- [ ] Implement delete confirmation dialog
- [ ] Backend: Add project listing API
- [ ] Test: List projects, view details, delete

### Phase 5: Code Editor Panel (Week 4)
- [ ] Install and configure Monaco Editor
- [ ] Create `.kit` file syntax highlighting
- [ ] Implement editor panel component
- [ ] Add toolbar (Save, Format, Undo/Redo)
- [ ] Add validation panel for errors
- [ ] Implement auto-save (debounced)
- [ ] Backend: Add file update API
- [ ] Test: Edit .kit file, save, validate

### Phase 6: Build & Launch Panels (Week 4-5)
- [ ] Create build output panel
- [ ] Implement WebSocket log streaming
- [ ] Add ANSI color support for logs
- [ ] Add build progress indicator
- [ ] Create preview panel for streaming
- [ ] Implement iframe integration
- [ ] Add [Stop Application] action
- [ ] Test: Build → Launch → Preview workflow
- [ ] Test: Kit App Streaming mode

### Phase 7: Polish & Testing (Week 5)
- [ ] Add keyboard shortcuts (Cmd+B, Cmd+L, etc.)
- [ ] Implement dark/light theme toggle
- [ ] Add onboarding tour for first-time users
- [ ] Add tooltips and help text
- [ ] Optimize bundle size (code splitting)
- [ ] Add analytics events
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Performance testing (Lighthouse)
- [ ] User testing with 3-5 developers

---

## 🎯 Success Metrics

### User Experience
- ✅ First-time user creates app in < 2 minutes
- ✅ Visual browsing increases template discovery by 50%+
- ✅ Progressive disclosure reduces cognitive load
- ✅ Click-to-success: 80% of users complete full flow

### Technical
- ✅ Panel transitions < 100ms
- ✅ Card grid renders 100+ templates smoothly
- ✅ Build logs stream in real-time (< 500ms latency)
- ✅ Bundle size < 1MB (gzipped)
- ✅ Lighthouse score > 90

### Delight
- ✅ Users describe it as a "playground" not a "tool"
- ✅ Positive feedback on visual design
- ✅ Users discover features through exploration
- ✅ Confetti moment on first success 🎉

---

## 🚀 Timeline

**Week 1**: Layout Foundation + Panel System
**Week 2**: Visual Template Browser + Detail Panel
**Week 3**: Project Management + Editor Setup
**Week 4**: Code Editor + Build Output
**Week 5**: Launch Preview + Polish + Testing

**Total**: 5 weeks for complete transformation

---

## 🎬 Next Steps

1. **Review this plan** with stakeholders
2. **Create design mockups** (Figma or similar)
3. **Set up new UI branch**: `git checkout -b ui-redesign-v2`
4. **Start Phase 1**: Layout foundation
5. **Weekly demos**: Show progress every Friday

---

## 📸 Reference Screenshots

**Inspiration 1**: VSCode Panel Layout
- Left: File explorer (always visible)
- Right: Editor panel, then terminal, then preview
- Resizable, closable, reorderable

**Inspiration 2**: NVIDIA NIM Discovery
- Card-based browsing
- Visual thumbnails + gradients
- Tag-based filtering
- Clear call-to-action buttons

**Inspiration 3**: Vercel Dashboard
- Clean, modern design
- Smooth transitions
- Real-time status updates
- Progressive disclosure

---

## 🏁 Definition of Done

The UI redesign is complete when:
1. ✅ All 6 phases implemented and tested
2. ✅ Design system documented and consistent
3. ✅ All existing functionality preserved
4. ✅ Performance metrics met (Lighthouse > 90)
5. ✅ User testing completed with positive feedback
6. ✅ Documentation updated (docs/UI_GUIDE.md)
7. ✅ Demo video recorded
8. ✅ Merged to main and deployed

---

**End of Plan** 🎉
