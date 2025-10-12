"""
Port Configuration Routes

Provides API endpoints for exposing port mappings and service
information to the frontend.
"""

import logging
from flask import Blueprint, jsonify
from kit_playground.backend.source.port_registry import PortRegistry

logger = logging.getLogger(__name__)

port_bp = Blueprint('port', __name__, url_prefix='/api/config')


@port_bp.route('/ports', methods=['GET'])
def get_ports():
    """
    Get all registered service ports and URLs.

    Returns:
        JSON response with:
        - backend: {name, port, host, protocol, url}
        - frontend: {name, port, host, protocol, url}
        - xpra_displays: {display_number: {display, port, url}}
        - default_host: The default hostname used for URLs
        - remote_mode: Whether running in REMOTE=1 mode

    Example response:
    {
        "backend": {
            "name": "backend",
            "port": 8000,
            "host": "jordanh-dev.hrd.nvidia.com",
            "protocol": "http",
            "url": "http://jordanh-dev.hrd.nvidia.com:8000"
        },
        "frontend": {
            "name": "frontend",
            "port": 8001,
            "host": "jordanh-dev.hrd.nvidia.com",
            "protocol": "http",
            "url": "http://jordanh-dev.hrd.nvidia.com:8001"
        },
        "xpra_displays": {
            "100": {
                "display": 100,
                "port": 10000,
                "url": "http://jordanh-dev.hrd.nvidia.com:10000"
            }
        },
        "default_host": "jordanh-dev.hrd.nvidia.com",
        "remote_mode": true
    }
    """
    try:
        registry = PortRegistry.get_instance()
        services = registry.get_all_services()
        return jsonify(services), 200
    except Exception as e:
        logger.error(f"Failed to get port configuration: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@port_bp.route('/ports/validate', methods=['GET'])
def validate_ports():
    """
    Validate that all registered services are reachable.

    This endpoint tests connectivity to all registered services
    and returns their reachability status.

    Returns:
        JSON response with service names mapped to boolean reachability

    Example response:
    {
        "backend": true,
        "frontend": true,
        "xpra_display_100": true
    }
    """
    try:
        registry = PortRegistry.get_instance()
        results = registry.validate_all_services()
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Failed to validate ports: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
