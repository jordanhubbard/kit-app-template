"""
Port Registry - Centralized port management for Kit Playground services.

This module provides a singleton registry that tracks all allocated ports
for the playground services (backend, frontend, Xpra displays) and provides
utilities for constructing correct URLs for inter-service communication.

Architecture:
- Backend API: Dynamically allocated port (default 8000+)
- Frontend UI: Dynamically allocated port in dev mode (default 8001+)
- Xpra Displays: Port 10000 + (display_number - 100)

The registry solves the problem where request.host might reflect a proxy
port rather than the actual service port, leading to incorrect URLs.
"""

import os
import socket
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Import network utilities for consistent hostname handling
from kit_playground.backend.utils.network import get_hostname_for_client, get_hostname_for_internal

logger = logging.getLogger(__name__)


@dataclass
class ServiceInfo:
    """Information about a registered service."""
    name: str
    port: int
    host: str
    protocol: str = "http"

    @property
    def url(self) -> str:
        """Get the full URL for this service."""
        return f"{self.protocol}://{self.host}:{self.port}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'port': self.port,
            'host': self.host,
            'protocol': self.protocol,
            'url': self.url
        }


class PortRegistry:
    """
    Centralized registry for all service ports in Kit Playground.

    This singleton tracks backend, frontend, and Xpra display ports,
    and provides methods to construct correct URLs for inter-service
    communication.

    Usage:
        registry = PortRegistry.get_instance()
        registry.register_backend(port=8000, host="localhost")
        registry.register_frontend(port=8001, host="localhost")
        registry.register_xpra_display(display=100, port=10000)

        # Get preview URL for a specific host
        preview_url = registry.get_preview_url(display=100, client_host="10.176.222.115")
    """

    _instance: Optional['PortRegistry'] = None

    def __init__(self):
        """Initialize the port registry."""
        self._services: Dict[str, ServiceInfo] = {}
        self._xpra_displays: Dict[int, int] = {}  # display_number -> port
        self._default_host = self._detect_default_host()
        logger.info(f"PortRegistry initialized with default host: {self._default_host}")

    @classmethod
    def get_instance(cls) -> 'PortRegistry':
        """Get the singleton instance of the port registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton instance (for testing)."""
        cls._instance = None

    def _detect_default_host(self) -> str:
        """
        Detect the default host for this system.

        Returns the actual hostname/IP that can be used to reach this
        machine from remote clients.
        
        Uses the centralized network utility to ensure consistent hostname detection.
        """
        hostname = get_hostname_for_client()
        logger.info(f"Using hostname for URLs: {hostname} (REMOTE={os.environ.get('REMOTE', '0')})")
        return hostname

    def register_backend(self, port: int, host: Optional[str] = None):
        """
        Register the backend API service.

        Args:
            port: The port the backend is listening on
            host: Optional hostname/IP (defaults to detected host)
        """
        host = host or self._default_host
        self._services['backend'] = ServiceInfo(
            name='backend',
            port=port,
            host=host,
            protocol='http'
        )
        logger.info(f"Registered backend service: {self._services['backend'].url}")

    def register_frontend(self, port: int, host: Optional[str] = None):
        """
        Register the frontend UI service.

        Args:
            port: The port the frontend is listening on
            host: Optional hostname/IP (defaults to detected host)
        """
        host = host or self._default_host
        self._services['frontend'] = ServiceInfo(
            name='frontend',
            port=port,
            host=host,
            protocol='http'
        )
        logger.info(f"Registered frontend service: {self._services['frontend'].url}")

    def register_xpra_display(self, display: int, port: int):
        """
        Register an Xpra display and its port.

        Args:
            display: The X11 display number (e.g., 100)
            port: The Xpra HTML5 server port
        """
        self._xpra_displays[display] = port
        logger.info(f"Registered Xpra display :{display} on port {port}")

    def get_backend_info(self) -> Optional[ServiceInfo]:
        """Get backend service information."""
        return self._services.get('backend')

    def get_frontend_info(self) -> Optional[ServiceInfo]:
        """Get frontend service information."""
        return self._services.get('frontend')

    def get_xpra_port(self, display: int) -> Optional[int]:
        """Get the port for a specific Xpra display."""
        return self._xpra_displays.get(display)

    def get_preview_url(self, display: int = 100, client_host: Optional[str] = None) -> str:
        """
        Construct a preview URL for an Xpra display.

        Args:
            display: The X11 display number (default 100)
            client_host: The hostname/IP to use (extracted from request)
                        If None, uses the default host from the registry

        Returns:
            The full HTTP URL to the Xpra HTML5 client

        Example:
            # Local mode
            get_preview_url(100) -> "http://localhost:10000"

            # Remote mode with client host
            get_preview_url(100, "10.176.222.115") -> "http://10.176.222.115:10000"
        """
        # Get the port (use formula if not registered)
        port = self._xpra_displays.get(display)
        if port is None:
            # Use standard Xpra port formula
            port = 10000 + (display - 100)
            logger.warning(f"Xpra display :{display} not registered, using calculated port {port}")

        # Determine the host to use
        if client_host:
            # Use the provided client host (from request)
            host = client_host
        elif self._default_host == "0.0.0.0":
            # In remote mode with 0.0.0.0, we need a client host
            # This shouldn't happen if client_host is properly provided
            logger.error("Cannot construct preview URL: REMOTE mode but no client_host provided")
            host = "localhost"  # Fallback
        else:
            # Use default host (localhost in local mode)
            host = self._default_host

        url = f"http://{host}:{port}"
        logger.info(f"Constructed preview URL for display :{display} -> {url}")
        return url

    def get_all_services(self) -> Dict[str, Any]:
        """
        Get information about all registered services.

        Returns:
            Dictionary with all service information
        """
        return {
            'backend': self._services.get('backend').to_dict() if 'backend' in self._services else None,
            'frontend': self._services.get('frontend').to_dict() if 'frontend' in self._services else None,
            'xpra_displays': {
                display: {
                    'display': display,
                    'port': port,
                    'url': f"http://{self._default_host}:{port}"
                }
                for display, port in self._xpra_displays.items()
            },
            'default_host': self._default_host,
            'remote_mode': os.environ.get('REMOTE') == '1'
        }

    def is_port_reachable(self, port: int, host: str = 'localhost', timeout: float = 1.0) -> bool:
        """
        Test if a port is reachable.

        Args:
            port: The port to test
            host: The host to test (default localhost)
            timeout: Connection timeout in seconds

        Returns:
            True if the port is reachable, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Port {port} on {host} not reachable: {e}")
            return False

    def validate_all_services(self) -> Dict[str, bool]:
        """
        Validate that all registered services are reachable.

        Returns:
            Dictionary mapping service names to reachability status
        """
        results = {}

        for name, service in self._services.items():
            # Always use localhost for internal health checks
            test_host = get_hostname_for_internal()
            results[name] = self.is_port_reachable(service.port, test_host)
            logger.info(f"Service {name} ({test_host}:{service.port}): {'✓ reachable' if results[name] else '✗ not reachable'}")

        for display, port in self._xpra_displays.items():
            # Always use localhost for internal health checks
            test_host = get_hostname_for_internal()
            key = f"xpra_display_{display}"
            results[key] = self.is_port_reachable(port, test_host)
            logger.info(f"Xpra display :{display} ({test_host}:{port}): {'✓ reachable' if results[key] else '✗ not reachable'}")

        return results

    def extract_client_host(self, request_host: str) -> str:
        """
        Extract the client's hostname/IP from the request host header.

        The request.host typically includes the port (e.g., "hostname:8000"),
        so we need to extract just the hostname part.

        Args:
            request_host: The value of request.host from Flask

        Returns:
            Just the hostname/IP portion (e.g., "hostname")
        """
        if ':' in request_host:
            return request_host.split(':')[0]
        return request_host
