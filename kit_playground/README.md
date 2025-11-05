# Kit Playground

Interactive development environment for NVIDIA Omniverse Kit applications.

## Overview

Kit Playground provides a web-based UI for creating, building, and launching Omniverse Kit applications. It simplifies the development workflow with:

- **Template-based project creation** - Choose from application, extension, and microservice templates
- **One-click builds** - Build projects with real-time log streaming
- **Integrated launching** - Run applications via Xpra or Kit App Streaming
- **Live development** - Hot-reload support for rapid iteration
- **Kit SDK version selection** - Choose which Kit SDK version to target
- **Container packaging** - Package applications as Docker containers

## Installation

### As a Package (Recommended)

Install Kit Playground as a Python package:

```bash
cd kit-app-template/kit_playground
pip install -e .
```

This makes `kit_playground` importable:

```python
from kit_playground import PlaygroundApp
from kit_playground.backend import PlaygroundWebServer

# Create and run the playground
app = PlaygroundApp()
server = PlaygroundWebServer(app, app.config)
server.run(host='localhost', port=8200)
```

### Standalone Usage

Run directly without installation:

```bash
cd kit-app-template
./kit_playground/playground.sh   # Linux/macOS
./kit_playground/playground.bat  # Windows
```

Or via Make:

```bash
make playground
```

## Package Structure

```
kit_playground/
├── __init__.py              # Package root
├── setup.py                 # Package installation script
├── pyproject.toml           # Modern packaging config
├── MANIFEST.in              # Package data inclusion rules
├── core/                    # Core application logic
│   ├── __init__.py
│   ├── playground_app.py   # Main PlaygroundApp class
│   └── config.py           # Configuration management
├── backend/                 # Flask web server
│   ├── __init__.py
│   ├── web_server.py       # PlaygroundWebServer class
│   ├── xpra_manager.py     # Xpra display server management
│   ├── routes/             # API endpoints (blueprints)
│   │   ├── project_routes.py
│   │   ├── template_routes.py
│   │   ├── filesystem_routes.py
│   │   └── ...
│   ├── source/             # Core backend modules
│   │   ├── __init__.py
│   │   ├── job_manager.py
│   │   ├── port_registry.py
│   │   └── process_monitor.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── network.py
└── ui/                      # React frontend (separate)
    └── src/
```

## Using as a Module

### Example: Custom Server Integration

```python
from kit_playground import PlaygroundApp
from kit_playground.backend import PlaygroundWebServer

# Initialize with custom config
app = PlaygroundApp()
app.config.set('api_port', 9000)

# Create server with custom settings
server = PlaygroundWebServer(app, app.config)

# Add custom routes
@server.app.route('/custom')
def custom_endpoint():
    return {'status': 'custom'}

# Run server
server.run(host='0.0.0.0', port=9000, debug=True)
```

### Example: Programmatic Project Creation

```python
from kit_playground.backend.source.apps.tools.repoman.template_api import TemplateAPI

# Initialize template API
api = TemplateAPI(repo_root="/path/to/kit-app-template")

# Create a new project
result = api.create_application(
    template_name="kit_base_editor",
    name="my_custom_app",
    display_name="My Custom App",
    version="1.0.0",
    accept_license=True
)

if result['success']:
    print(f"Created: {result['app_dir']}")
```

### Example: Job Management

```python
from kit_playground.backend.source import JobManager

# Create job manager
job_mgr = JobManager()

# Start a build job
job_id = job_mgr.create_job(
    type='build',
    project_name='my_app',
    project_path='source/apps/my_app'
)

# Monitor job status
status = job_mgr.get_job_status(job_id)
print(f"Job {job_id}: {status}")
```

## API Endpoints

The backend provides REST API endpoints:

- **`/api/v2/templates`** - List available templates
- **`/api/v2/templates/generate`** - Create project from template
- **`/api/projects/build`** - Build a project
- **`/api/projects/run`** - Launch an application
- **`/api/projects/package`** - Package as container
- **`/api/projects/kit-versions`** - List available Kit SDK versions
- **`/api/filesystem/read`** - Read file contents
- **`/api/filesystem/write`** - Write file contents

See `/api/docs` for full API documentation.

## Development

### Running Tests

```bash
cd kit_playground
pytest tests/
```

### Code Formatting

```bash
# Format code with Black
black kit_playground/

# Type checking
mypy kit_playground/
```

### Hot-Reload Development

The backend supports hot-reload for rapid development:

```bash
python playground.py --debug
```

## Dependencies

Core dependencies (from `backend/requirements.txt`):
- Flask >= 2.0.0
- Flask-CORS >= 3.0.0
- Flask-SocketIO >= 5.0.0
- python-socketio >= 5.0.0
- toml >= 0.10.0

## License

MIT License - See LICENSE file for details.

## Support

- Documentation: https://docs.omniverse.nvidia.com/kit/docs/kit-app-template
- Issues: https://github.com/NVIDIA-Omniverse/kit-app-template/issues

