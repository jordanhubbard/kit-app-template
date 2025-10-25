# Kit Playground UI Redesign Plan

**Version**: 2.0 - Clean Slate Redesign
**Date**: October 24, 2025
**Approach**: Option B - Build from scratch for Phases 1-6

---

## Executive Summary

The Kit Playground UI will be completely redesigned from the ground up to provide a modern, elegant interface for novice users. Since the UI is fork-specific with no backward compatibility constraints, we can optimize every aspect for the enhanced system.

### Design Principles

1. **Novice-Friendly**: Clear, intuitive interface for users unfamiliar with CLI
2. **Modern & Beautiful**: Contemporary design following 2025 best practices
3. **Real-Time Feedback**: WebSocket integration for live progress
4. **Complete Feature Coverage**: Support for all 6 phases
5. **Responsive Design**: Works on desktop and tablet
6. **Performance**: Fast, efficient, optimized

---

## Target Users

### Primary: Novice Developers

**Profile**:
- New to Omniverse development
- Limited CLI experience
- Visual/interactive learners
- Need guidance and examples
- Want immediate feedback

**Needs**:
- Browse and discover templates
- Create projects with form inputs
- See build/launch progress
- Understand errors clearly
- Learn by example

### Secondary: Experienced Developers

**Profile**:
- Familiar with CLI
- Use UI for quick tasks
- Want visual monitoring
- Prefer efficiency

**Needs**:
- Quick template creation
- Job monitoring dashboard
- Log viewing
- Status at a glance

---

## UI Architecture

### Technology Stack

**Frontend**:
- React 18 (with Hooks)
- TypeScript (for type safety)
- Tailwind CSS (for modern styling)
- Socket.IO Client (for WebSocket)
- React Router (for navigation)
- React Query or SWR (for API state)
- Axios (for HTTP requests)

**State Management**:
- React Context for global state
- Local state for component state
- No Redux (too complex for this use case)

**Build Tools**:
- Vite (fast, modern build tool)
- ESLint + Prettier
- TypeScript compiler

### Architecture Pattern

**Component Structure**:
```
src/
├── components/
│   ├── common/          # Reusable components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ProgressBar.tsx
│   │
│   ├── layout/          # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── MainLayout.tsx
│   │
│   ├── templates/       # Template-related
│   │   ├── TemplateCard.tsx
│   │   ├── TemplateList.tsx
│   │   ├── TemplateDetail.tsx
│   │   └── TemplateCreateForm.tsx
│   │
│   ├── jobs/           # Job-related
│   │   ├── JobCard.tsx
│   │   ├── JobList.tsx
│   │   ├── JobDetail.tsx
│   │   └── JobLogViewer.tsx
│   │
│   └── projects/       # Project-related
│       ├── ProjectCard.tsx
│       ├── ProjectList.tsx
│       └── ProjectActions.tsx
│
├── pages/              # Page components
│   ├── HomePage.tsx
│   ├── TemplatesPage.tsx
│   ├── CreateProjectPage.tsx
│   ├── JobsPage.tsx
│   └── SettingsPage.tsx
│
├── hooks/              # Custom hooks
│   ├── useAPI.ts
│   ├── useWebSocket.ts
│   ├── useTemplates.ts
│   └── useJobs.ts
│
├── services/           # API services
│   ├── api.ts
│   ├── websocket.ts
│   └── types.ts
│
├── contexts/           # React contexts
│   ├── AppContext.tsx
│   └── WebSocketContext.tsx
│
├── utils/              # Utility functions
│   └── formatters.ts
│
└── App.tsx             # Root component
```

---

## Page Designs

### 1. Home Page

**Purpose**: Welcome and quick start

**Layout**:
```
┌────────────────────────────────────────────────┐
│  Kit App Template                    [Settings]│
├────────────────────────────────────────────────┤
│                                                │
│      Welcome to Kit App Template               │
│                                                │
│   Build GPU-accelerated applications with      │
│   NVIDIA Omniverse                             │
│                                                │
│   ┌──────────────┐  ┌──────────────┐          │
│   │   Browse     │  │    Create    │          │
│   │  Templates   │  │   Project    │          │
│   │              │  │              │          │
│   └──────────────┘  └──────────────┘          │
│                                                │
│   ┌──────────────────────────────────────┐    │
│   │  Recent Activity                     │    │
│   │  • my.app - Build completed ✓        │    │
│   │  • test.app - Created 2 mins ago     │    │
│   └──────────────────────────────────────┘    │
│                                                │
│   ┌──────────────────────────────────────┐    │
│   │  Quick Start                         │    │
│   │  1. Browse templates                 │    │
│   │  2. Create your first app            │    │
│   │  3. Build and launch                 │    │
│   └──────────────────────────────────────┘    │
│                                                │
└────────────────────────────────────────────────┘
```

**Features**:
- Clear call-to-action buttons
- Recent activity feed (via API)
- Quick start guide
- Clean, welcoming design

---

### 2. Templates Page

**Purpose**: Browse and discover templates

**Layout**:
```
┌────────────────────────────────────────────────┐
│  Templates                           [Filter ▾]│
├────────────────────────────────────────────────┤
│                                                │
│  [All] [Applications] [Extensions] [Services] │
│                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │Kit Base     │  │USD Viewer   │  │USD      ││
│  │Editor       │  │             │  │Explorer ││
│  │             │  │View USD     │  │         ││
│  │Full editor  │  │files        │  │Explore  ││
│  │[Create]     │  │[Create]     │  │[Create] ││
│  └─────────────┘  └─────────────┘  └─────────┘│
│                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │Basic Python │  │Basic C++    │  │Kit      ││
│  │Extension    │  │Extension    │  │Service  ││
│  │             │  │             │  │         ││
│  │Python ext   │  │C++ ext      │  │Micro-   ││
│  │[Create]     │  │[Create]     │  │service  ││
│  └─────────────┘  └─────────────┘  │[Create] ││
│                                    └─────────┘│
│                                                │
└────────────────────────────────────────────────┘
```

**Features**:
- Card-based layout
- Filter by type
- Search functionality
- Template details on click
- Quick create button

---

### 3. Create Project Page

**Purpose**: Create new project from template

**Layout**:
```
┌────────────────────────────────────────────────┐
│  Create Project                     [← Back]   │
├────────────────────────────────────────────────┤
│                                                │
│  Template: Kit Base Editor                     │
│  Full-featured Omniverse editor application    │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Project Details                        │    │
│  │                                        │    │
│  │ Name *                                 │    │
│  │ [com.company.myapp            ]        │    │
│  │                                        │    │
│  │ Display Name                           │    │
│  │ [My Application               ]        │    │
│  │                                        │    │
│  │ Version                                │    │
│  │ [1.0.0                        ]        │    │
│  │                                        │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Advanced Options              [Show ▾] │    │
│  │                                        │    │
│  │ ☐ Create as standalone project        │    │
│  │ ☐ Use per-app dependencies            │    │
│  │                                        │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  [Cancel]                    [Create Project]  │
│                                                │
└────────────────────────────────────────────────┘
```

**Features**:
- Form validation
- Real-time feedback
- Advanced options (collapsible)
- Clear error messages
- Progress indication after submit

---

### 4. Jobs Page

**Purpose**: Monitor running and completed jobs

**Layout**:
```
┌────────────────────────────────────────────────┐
│  Jobs                    [All ▾] [Refresh]     │
├────────────────────────────────────────────────┤
│                                                │
│  Active Jobs (2)                               │
│  ┌────────────────────────────────────────┐    │
│  │ Building my.app                        │    │
│  │ [████████░░░░░░░░░░] 45%              │    │
│  │ Started 2 minutes ago                  │    │
│  │                            [View Logs] │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Creating template: test.app            │    │
│  │ [██████████████████] 100%              │    │
│  │ Completed just now                  ✓  │    │
│  │                            [View Logs] │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  Completed Jobs (15)                    [Clear]│
│  ┌────────────────────────────────────────┐    │
│  │ Build my.app ✓       2 hours ago      │    │
│  │ Create demo.app ✓    Yesterday        │    │
│  │ Build old.app ✗      2 days ago       │    │
│  └────────────────────────────────────────┘    │
│                                                │
└────────────────────────────────────────────────┘
```

**Features**:
- Real-time progress (WebSocket)
- Live log streaming
- Filter by status
- Auto-refresh
- Job history

---

### 5. Job Detail / Logs Modal

**Layout**:
```
┌────────────────────────────────────────────────┐
│  Job: Building my.app               [× Close]  │
├────────────────────────────────────────────────┤
│                                                │
│  Status: Running                               │
│  Progress: 45%                                 │
│  Started: 2 minutes ago                        │
│                                                │
│  [████████░░░░░░░░░░] 45%                     │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Logs                  [Auto-scroll ☑]  │    │
│  │────────────────────────────────────────│    │
│  │ [10:30:05] Starting build process...   │    │
│  │ [10:30:10] Compiling extensions...     │    │
│  │ [10:30:15] Building application...     │    │
│  │ [10:30:20] Linking libraries...        │    │
│  │ [10:30:25] Processing assets...        │    │
│  │ [10:30:30] Copying resources...        │    │
│  │ [10:30:35] Almost done...              │    │
│  │                                        │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  [Cancel Job]                   [Download Logs]│
│                                                │
└────────────────────────────────────────────────┘
```

**Features**:
- Real-time log streaming (WebSocket)
- Auto-scroll toggle
- Cancel running jobs
- Download logs
- ANSI color support (optional)

---

## Key Features

### 1. Real-Time Updates

**WebSocket Integration**:
- Connect on app load
- Subscribe to job events
- Update UI instantly
- Reconnect on disconnect

**Events**:
- `job_log` → Add to log viewer
- `job_progress` → Update progress bar
- `job_status` → Update job status badge

### 2. Form Validation

**Project Name**:
- Required field
- Pattern: `[a-z0-9._]+`
- Real-time validation
- Clear error messages

**Example**:
```typescript
const validateProjectName = (name: string): string | null => {
  if (!name) return "Project name is required";
  if (!/^[a-z0-9._]+$/.test(name)) {
    return "Project name must contain only lowercase letters, numbers, dots, and underscores";
  }
  return null;
};
```

### 3. Error Handling

**API Errors**:
- Toast notifications for errors
- Detailed error messages
- Retry options
- Fallback UI

**Network Errors**:
- Offline indicator
- Retry mechanism
- Cached data display

### 4. Loading States

**Skeleton Screens**:
- Template cards
- Job list
- While loading data

**Progress Indicators**:
- Progress bars for jobs
- Spinners for API calls
- Percentage display

---

## Design System

### Color Palette

**Primary** (NVIDIA Green):
- `#76B900` - Primary actions
- `#5E9400` - Hover state
- `#4A7600` - Active state

**Secondary** (Neutral):
- `#1E1E1E` - Dark background
- `#2D2D2D` - Card background
- `#3D3D3D` - Hover state

**Status Colors**:
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Error: `#EF4444` (Red)
- Info: `#3B82F6` (Blue)

**Text**:
- Primary: `#FFFFFF`
- Secondary: `#A0A0A0`
- Disabled: `#606060`

### Typography

**Font Family**: Inter, system-ui, sans-serif

**Sizes**:
- Heading 1: 2.5rem (40px)
- Heading 2: 2rem (32px)
- Heading 3: 1.5rem (24px)
- Body: 1rem (16px)
- Small: 0.875rem (14px)

### Spacing

**Scale**: 4px base unit
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

### Components

**Button**:
- Primary: NVIDIA Green background
- Secondary: Transparent with border
- Hover: Slight scale + opacity
- Active: Pressed state
- Disabled: Grayed out

**Card**:
- Background: Dark (#2D2D2D)
- Border: 1px subtle
- Hover: Slight elevation
- Padding: 24px

**Input**:
- Background: Dark
- Border: 1px neutral
- Focus: Primary color border
- Error: Red border

---

## Implementation Plan

### Phase 1: Setup & Foundation (2-3 hours)

**Tasks**:
1. Set up Vite + React + TypeScript project
2. Install dependencies (Tailwind, Socket.IO, etc.)
3. Configure ESLint + Prettier
4. Create base folder structure
5. Set up routing
6. Create design system (colors, typography, spacing)
7. Build common components (Button, Card, Input, etc.)

**Deliverables**:
- Working dev environment
- Base component library
- Routing configured

---

### Phase 2: Core Pages (4-5 hours)

**Tasks**:
1. Build HomePage
2. Build TemplatesPage
   - Template card component
   - Template list
   - Filter/search
3. Build CreateProjectPage
   - Form with validation
   - API integration
4. Build layout components
   - Header
   - Sidebar (optional)
   - MainLayout

**Deliverables**:
- Working pages with navigation
- Template browsing
- Project creation form

---

### Phase 3: Jobs & Real-Time (3-4 hours)

**Tasks**:
1. Set up WebSocket connection
2. Build JobsPage
   - Job list
   - Status indicators
   - Progress bars
3. Build JobDetail modal
   - Log viewer
   - Real-time log streaming
   - Progress updates
4. Integrate WebSocket events

**Deliverables**:
- Real-time job monitoring
- Log streaming
- Progress visualization

---

### Phase 4: API Integration (2-3 hours)

**Tasks**:
1. Create API service layer
2. Implement error handling
3. Add loading states
4. Add toast notifications
5. Implement retry logic
6. Add offline detection

**Deliverables**:
- Complete API integration
- Error handling
- Loading states

---

### Phase 5: Polish & Testing (3-4 hours)

**Tasks**:
1. Responsive design testing
2. Cross-browser testing
3. Performance optimization
4. Accessibility improvements
5. UI polish
6. Documentation

**Deliverables**:
- Production-ready UI
- Responsive design
- Accessible components

---

## Total Estimate: 15-20 hours

**Breakdown**:
- Setup: 2-3 hours
- Core Pages: 4-5 hours
- Jobs & Real-Time: 3-4 hours
- API Integration: 2-3 hours
- Polish: 3-4 hours

---

## Success Criteria

✅ **Functional**:
- Browse templates
- Create projects
- Monitor jobs
- View logs
- Real-time updates

✅ **Usability**:
- Intuitive for novices
- Clear error messages
- Immediate feedback
- Helpful guidance

✅ **Quality**:
- No console errors
- Fast loading (<2s)
- Smooth animations
- Responsive design

✅ **Technical**:
- TypeScript (type-safe)
- Tested components
- Clean code
- Documented

---

## Future Enhancements (Optional)

1. **Dark/Light Mode Toggle**
2. **Project Dashboard** (list all projects)
3. **Settings Page** (API endpoint, preferences)
4. **Keyboard Shortcuts**
5. **Export/Import Projects**
6. **Template Search with Fuzzy Matching**
7. **Build Configuration UI** (release/debug)
8. **Launch Options UI** (headless, Xpra, etc.)
9. **Dependency Manager UI** (for per-app deps)
10. **Standalone Project Export UI**

---

## Next Step

Begin implementation with Phase 1: Setup & Foundation.

Create a new, modern UI from scratch using Vite + React + TypeScript + Tailwind CSS.

---

**Ready to build a beautiful, modern UI for Kit App Template!** 🚀
