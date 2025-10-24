# Kit App Template UI

Modern, novice-friendly web interface for the Kit App Template system.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Socket.IO Client** - Real-time WebSocket updates
- **Axios** - HTTP client

## Features

- 🎨 Modern, clean NVIDIA-themed UI
- 🔄 Real-time job monitoring with WebSocket
- 📝 Template browsing and filtering
- ✅ Form validation for project creation
- 📊 Live progress tracking
- 🎯 Novice-friendly interface

## Development

### Prerequisites

- Node.js 18+ and npm
- Kit App Template backend running on `http://localhost:5000`

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Configuration

The UI connects to the backend API at `http://localhost:5000` by default.

To change the API endpoint, create a `.env` file:

```env
VITE_API_BASE_URL=http://your-api-host:port/api
VITE_WS_BASE_URL=http://your-api-host:port
```

## Project Structure

```
src/
├── components/
│   ├── common/          # Reusable UI components
│   ├── layout/          # Layout components
│   ├── templates/       # Template-specific components
│   ├── jobs/            # Job-related components
│   └── projects/        # Project-related components
│
├── pages/               # Page components
│   ├── HomePage.tsx
│   ├── TemplatesPage.tsx
│   ├── CreateProjectPage.tsx
│   └── JobsPage.tsx
│
├── services/            # API & WebSocket services
│   ├── api.ts          # REST API wrapper
│   ├── websocket.ts    # WebSocket client
│   └── types.ts        # TypeScript types
│
├── hooks/              # Custom React hooks
├── contexts/           # React contexts
├── utils/              # Utility functions
│
├── App.tsx             # Root component with routing
├── main.tsx            # Entry point
└── index.css           # Global styles
```

## Pages

### Home Page (`/`)
- Welcome screen
- Quick actions (Browse Templates, Create Project)
- Quick start guide
- Feature showcase

### Templates Page (`/templates`)
- Browse all available templates
- Filter by type (application, extension, microservice)
- Template cards with descriptions
- Create project from template

### Create Project Page (`/templates/create/:templateName`)
- Project creation form
- Real-time validation
- Advanced options (standalone, per-app dependencies)
- Success navigation to jobs page

### Jobs Page (`/jobs`)
- Real-time job monitoring
- Active jobs with progress bars
- Completed jobs history
- Job detail modal with log streaming
- Filter by status

## Components

### Common Components
- **Button** - Variants: primary, secondary, danger, ghost
- **Card** - Container with optional hover effect
- **Input** - Form input with validation
- **LoadingSpinner** - Animated loading indicator
- **ProgressBar** - Progress visualization

### Layout Components
- **Header** - Top navigation with active link highlighting
- **MainLayout** - Main app layout with header and footer

## Services

### API Service (`services/api.ts`)
Type-safe REST API wrapper with:
- Template management (list, get, create)
- Job management (list, get, cancel, delete, stats)
- Error handling
- Timeout configuration

### WebSocket Service (`services/websocket.ts`)
Socket.IO client for real-time updates:
- `job_log` - Job log messages
- `job_progress` - Progress updates
- `job_status` - Status changes
- Auto-reconnection

## Styling

### Theme
- **Primary Color**: NVIDIA Green (#76B900)
- **Background**: Dark (#1E1E1E)
- **Card Background**: Dark Card (#2D2D2D)
- **Text**: White with gray variants

### Tailwind Configuration
Custom colors defined in `tailwind.config.js`:
- `nvidia-green`, `nvidia-green-hover`, `nvidia-green-active`
- `dark-bg`, `dark-card`, `dark-hover`

## Development Tips

### Hot Module Replacement (HMR)
Vite provides instant HMR for fast development iteration.

### TypeScript
All components are fully typed. Run `npm run build` to check for type errors.

### Linting
```bash
npm run lint
```

### Adding New Pages
1. Create page component in `src/pages/`
2. Export from `src/pages/index.ts`
3. Add route in `src/App.tsx`
4. Add navigation link in `src/components/layout/Header.tsx`

### Adding New Components
1. Create component in appropriate `src/components/` subdirectory
2. Export from subdirectory's `index.ts`
3. Import and use in pages/components

## Building for Production

```bash
# Build
npm run build

# Preview build locally
npm run preview

# Output directory
dist/
```

The production build is optimized and minified, ready for deployment.

## Backend API

The UI requires the Kit App Template backend to be running:

```bash
# From kit-app-template root
cd kit_playground/backend
python3 web_server.py
```

Backend provides:
- REST API at `http://localhost:5000/api`
- WebSocket at `http://localhost:5000`
- Swagger UI at `http://localhost:5000/api/docs/ui`

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Known Issues

None at this time.

## Future Enhancements

- Dark/Light mode toggle
- Settings page for API configuration
- Keyboard shortcuts
- Project dashboard
- Export/import projects
- Build configuration UI
- Launch options UI

---

**Version**: 2.0  
**Last Updated**: October 24, 2025
