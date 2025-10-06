"""
Xpra management routes for Kit Playground.
"""
import logging
import subprocess
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

    return xpra_bp

