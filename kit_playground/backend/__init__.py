"""
Kit Playground Backend - Flask-based web server and APIs.

Provides REST API endpoints for:
- Template management and project creation
- Build and launch orchestration
- File system operations
- WebSocket-based real-time communication
- Xpra display server management
"""

from kit_playground.backend.web_server import PlaygroundWebServer
from kit_playground.backend.xpra_manager import XpraManager

__all__ = [
    "PlaygroundWebServer",
    "XpraManager",
]

