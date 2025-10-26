"""
Xpra management routes for Kit Playground.
"""
import logging
import subprocess
import time
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

# Create blueprint
xpra_bp = Blueprint('xpra', __name__, url_prefix='/api/xpra')


def create_xpra_routes(xpra_manager):
    """
    Create and configure Xpra routes.
    
    Args:
        xpra_manager: XpraManager instance
    
    Returns:
        Flask Blueprint with Xpra routes configured
    """
    
    @xpra_bp.route('/check', methods=['GET'])
    def check_xpra():
        """Check if Xpra is installed and available."""
        try:
            # Try to run xpra --version to check if it's installed
            result = subprocess.run(
                ['xpra', '--version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            available = result.returncode == 0
            version = None
            
            if available:
                # Parse version from output
                output = result.stdout or result.stderr
                for line in output.split('\n'):
                    if 'xpra' in line.lower() and any(c.isdigit() for c in line):
                        version = line.strip()
                        break
            
            return jsonify({
                'available': available,
                'version': version,
                'installed': available
            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Xpra not found or timed out
            return jsonify({
                'available': False,
                'version': None,
                'installed': False,
                'error': 'Xpra is not installed or not in PATH'
            })
        except Exception as e:
            logger.error(f"Failed to check Xpra availability: {e}", exc_info=True)
            return jsonify({
                'available': False,
                'version': None,
                'installed': False,
                'error': str(e)
            })

    @xpra_bp.route('/sessions', methods=['GET'])
    def list_sessions():
        """List active Xpra sessions."""
        try:
            sessions = []
            for session_id, session in xpra_manager.sessions.items():
                sessions.append({
                    'id': session_id,
                    'display': session.display,
                    'port': session.port,
                    'started': session.started,
                    'url': xpra_manager.get_session_url(session_id)
                })
            return jsonify({'sessions': sessions})
        except Exception as e:
            logger.error(f"Failed to list Xpra sessions: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @xpra_bp.route('/status/<int:display>', methods=['GET'])
    def check_display_status(display: int):
        """Check if a specific Xpra display is ready.
        
        Args:
            display: Xpra display number to check
            
        Returns:
            JSON with ready status and details
        """
        try:
            import socket
            
            # Check if Xpra process is running
            result = subprocess.run(
                ['xpra', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            process_running = result.returncode == 0 and f':{display}' in result.stdout
            
            # Check if port is listening
            port = 10000 + (display - 100)
            
            # Always use localhost for internal health checks
            port_listening = False
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                port_listening = result == 0
            except Exception:
                pass
            
            # Check if we can get a response from the web interface
            # Use localhost for internal HTTP request
            web_ready = False
            if port_listening:
                try:
                    import urllib.request
                    import urllib.error
                    url = f"http://localhost:{port}"
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
                    with urllib.request.urlopen(req, timeout=2) as response:
                        web_ready = response.status == 200
                except Exception:
                    pass
            
            # Get the hostname for the client-facing URL
            from kit_playground.backend.utils.network import get_hostname_for_client
            client_hostname = get_hostname_for_client()
            
            return jsonify({
                'display': display,
                'port': port,
                'process_running': process_running,
                'port_listening': port_listening,
                'web_ready': web_ready,
                'ready': process_running and port_listening and web_ready,
                'url': f"http://{client_hostname}:{port}" if port_listening else None
            })
            
        except Exception as e:
            logger.error(f"Failed to check Xpra display status: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return xpra_bp

