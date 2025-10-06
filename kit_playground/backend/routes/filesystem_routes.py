"""
Filesystem operation routes for Kit Playground.
"""
import logging
from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# Create blueprint
filesystem_bp = Blueprint('filesystem', __name__, url_prefix='/api/filesystem')


def create_filesystem_routes(security_validator):
    """
    Create and configure filesystem routes.
    
    Args:
        security_validator: Object with security validation methods
    
    Returns:
        Flask Blueprint with filesystem routes configured
    """
    
    @filesystem_bp.route('/cwd', methods=['GET'])
    def get_current_directory():
        """Get current working directory (repo root)."""
        try:
            repo_root = Path(__file__).parent.parent.parent.parent
            return jsonify({
                'cwd': str(repo_root),
                'realpath': str(repo_root.resolve())
            })
        except Exception as e:
            logger.error(f"Failed to get current directory: {e}")
            return jsonify({'error': str(e)}), 500

    @filesystem_bp.route('/list', methods=['GET'])
    def list_directory():
        """List directory contents."""
        try:
            path = request.args.get('path', str(Path.home()))
            
            # SECURITY: Validate path to prevent path traversal
            path_obj = security_validator._validate_filesystem_path(path)
            if not path_obj:
                return jsonify({'error': 'Access denied to this path'}), 403

            if not path_obj.exists():
                return jsonify({'error': 'Path does not exist'}), 404

            if not path_obj.is_dir():
                return jsonify({'error': 'Path is not a directory'}), 400

            items = []
            for item in path_obj.iterdir():
                try:
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'isDirectory': item.is_dir(),
                        'size': item.stat().st_size if item.is_file() else 0,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
                except (OSError, PermissionError):
                    continue  # Skip items we can't access

            return jsonify(items)
        except Exception as e:
            logger.error(f"Failed to list directory: {e}")
            return jsonify({'error': str(e)}), 500

    @filesystem_bp.route('/mkdir', methods=['POST'])
    def create_directory():
        """Create a new directory."""
        try:
            data = request.json
            path = data.get('path')

            if not path:
                return jsonify({'error': 'path required'}), 400

            # SECURITY: Validate path to prevent path traversal
            path_obj = security_validator._validate_filesystem_path(path, allow_creation=True)
            if not path_obj:
                return jsonify({'error': 'Access denied to this path'}), 403

            path_obj.mkdir(parents=True, exist_ok=True)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Failed to create directory: {e}")
            return jsonify({'error': str(e)}), 500

    @filesystem_bp.route('/read', methods=['GET'])
    def read_file():
        """Read file contents."""
        try:
            path = request.args.get('path')

            if not path:
                return jsonify({'error': 'path required'}), 400

            # SECURITY: Validate path to prevent path traversal
            path_obj = security_validator._validate_filesystem_path(path)
            if not path_obj:
                return jsonify({'error': 'Access denied to this path'}), 403

            if not path_obj.exists():
                return jsonify({'error': 'File does not exist'}), 404

            if not path_obj.is_file():
                return jsonify({'error': 'Path is not a file'}), 400

            # Read file content
            content = path_obj.read_text(encoding='utf-8')
            return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return jsonify({'error': str(e)}), 500

    return filesystem_bp

