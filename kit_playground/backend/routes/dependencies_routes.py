"""
Dependency management routes for Kit Playground.

Handles extension dependency status, preparation, and caching.
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Generator

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

# Create blueprint
dependencies_bp = Blueprint('dependencies', __name__, url_prefix='/api/dependencies')


def format_size(bytes_size: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def get_extension_cache_path() -> Path:
    """Get the path to Kit SDK extension cache."""
    return Path.home() / '.local/share/ov/data/exts'


def get_cache_status() -> dict:
    """
    Get current extension cache status.

    Returns:
        dict with cache information
    """
    cache_path = get_extension_cache_path()

    if not cache_path.exists():
        return {
            'cached': False,
            'exists': False,
            'size': '0 B',
            'size_bytes': 0,
            'count': 0,
            'path': str(cache_path)
        }

    try:
        # Count extension directories (v2 subdirectory structure)
        v2_path = cache_path / 'v2'
        if v2_path.exists():
            ext_count = len([d for d in v2_path.iterdir() if d.is_dir()])
        else:
            ext_count = len([d for d in cache_path.iterdir() if d.is_dir()])

        # Calculate total size
        total_size = 0
        for root, dirs, files in os.walk(cache_path):
            for file in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, file))
                except (OSError, FileNotFoundError):
                    pass

        # Consider cached if we have a reasonable number of extensions
        is_cached = ext_count > 50

        return {
            'cached': is_cached,
            'exists': True,
            'size': format_size(total_size),
            'size_bytes': total_size,
            'count': ext_count,
            'path': str(cache_path),
            'threshold': 50  # Minimum extensions to consider "cached"
        }
    except Exception as e:
        logger.error(f"Error checking cache status: {e}")
        return {
            'cached': False,
            'exists': True,
            'size': 'Unknown',
            'size_bytes': 0,
            'count': 0,
            'path': str(cache_path),
            'error': str(e)
        }


def create_dependencies_routes(socketio: SocketIO):
    """
    Create and configure dependency management routes.

    Args:
        socketio: SocketIO instance for real-time updates
    """

    @dependencies_bp.route('/status', methods=['GET'])
    def get_status():
        """
        Get current dependency cache status.

        Returns:
            JSON with cache status information
        """
        try:
            status = get_cache_status()
            # Add success flag for frontend compatibility
            return jsonify({
                'success': True,
                **status
            })
        except Exception as e:
            logger.error(f"Error getting dependency status: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @dependencies_bp.route('/estimate', methods=['GET'])
    def get_estimate():
        """
        Get estimated download size and time for dependencies.

        Query params:
            bandwidth: Network bandwidth in Mbps (default: 50)

        Returns:
            JSON with size and time estimates
        """
        try:
            bandwidth_mbps = float(request.args.get('bandwidth', 50))

            # Approximate values based on typical Kit SDK extension cache
            estimated_size_bytes = 12 * 1024 * 1024 * 1024  # ~12 GB
            estimated_extension_count = 130  # Typical count

            # Calculate time based on bandwidth (Mbps to bytes/sec)
            bytes_per_second = (bandwidth_mbps * 1024 * 1024) / 8
            estimated_seconds = estimated_size_bytes / bytes_per_second

            # Format time
            if estimated_seconds < 60:
                time_str = f"{int(estimated_seconds)} seconds"
            elif estimated_seconds < 3600:
                minutes = int(estimated_seconds / 60)
                time_str = f"{minutes} minutes"
            else:
                hours = int(estimated_seconds / 3600)
                minutes = int((estimated_seconds % 3600) / 60)
                time_str = f"{hours}h {minutes}m"

            return jsonify({
                'success': True,
                'estimated_size': format_size(estimated_size_bytes),
                'estimated_size_bytes': estimated_size_bytes,
                'estimated_time': time_str,
                'estimated_seconds': int(estimated_seconds),
                'extension_count': estimated_extension_count,
                'bandwidth_mbps': bandwidth_mbps
            })
        except Exception as e:
            logger.error(f"Error getting estimate: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @dependencies_bp.route('/prepare', methods=['POST'])
    def prepare_dependencies():
        """
        Prepare (pre-fetch) extension dependencies.

        Uses Server-Sent Events (SSE) for real-time progress updates.

        Request body:
            {
                "config": "release" | "debug"  # Optional, defaults to "release"
            }

        Returns:
            SSE stream with progress updates
        """
        data = request.json or {}
        config = data.get('config', 'release')

        # Get repo root
        repo_root = Path(__file__).parent.parent.parent.parent
        validation_script = repo_root / 'tools' / 'repoman' / 'validate_kit_deps.py'

        if not validation_script.exists():
            return jsonify({'error': 'Validation script not found'}), 500

        def generate() -> Generator[str, None, None]:
            """Generate SSE stream with progress updates."""
            try:
                logger.info(f"Starting dependency preparation (config={config})")

                # Send initial status
                yield f"data: {json.dumps({'type': 'start', 'message': 'Starting dependency preparation...'})}\n\n"

                # Start pre-fetch process
                cmd = [
                    'python',
                    str(validation_script),
                    '--prefetch',
                    '--config', config,
                    '-v'  # Verbose for detailed output
                ]

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    cwd=repo_root
                )

                # Track progress
                start_time = time.time()
                line_count = 0

                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue

                    line_count += 1
                    elapsed = time.time() - start_time

                    # Parse different types of output
                    if 'installed' in line.lower():
                        # Extension installed
                        yield f"data: {json.dumps({'type': 'extension_installed', 'message': line, 'elapsed': elapsed})}\n\n"
                    elif 'pulling' in line.lower():
                        # Extension downloading
                        yield f"data: {json.dumps({'type': 'extension_download', 'message': line, 'elapsed': elapsed})}\n\n"
                    elif 'error' in line.lower() or 'failed' in line.lower():
                        # Error occurred
                        yield f"data: {json.dumps({'type': 'error', 'message': line, 'elapsed': elapsed})}\n\n"
                    elif 'success' in line.lower() or 'complete' in line.lower():
                        # Success message
                        yield f"data: {json.dumps({'type': 'success', 'message': line, 'elapsed': elapsed})}\n\n"
                    else:
                        # General progress
                        yield f"data: {json.dumps({'type': 'progress', 'message': line, 'elapsed': elapsed})}\n\n"

                    # Periodic progress update
                    if line_count % 10 == 0:
                        status = get_cache_status()
                        yield f"data: {json.dumps({'type': 'status_update', 'status': status, 'elapsed': elapsed})}\n\n"

                # Wait for process to complete
                returncode = process.wait()
                elapsed = time.time() - start_time

                # Send final status
                final_status = get_cache_status()

                if returncode == 0:
                    logger.info(f"Dependency preparation completed successfully in {elapsed:.1f}s")
                    yield f"data: {json.dumps({
                        'type': 'complete',
                        'success': True,
                        'message': 'All dependencies prepared successfully!',
                        'status': final_status,
                        'elapsed': elapsed
                    })}\n\n"
                else:
                    logger.error(f"Dependency preparation failed with code {returncode}")
                    yield f"data: {json.dumps({
                        'type': 'complete',
                        'success': False,
                        'message': f'Preparation failed with exit code {returncode}',
                        'status': final_status,
                        'elapsed': elapsed
                    })}\n\n"

            except Exception as e:
                logger.error(f"Error during dependency preparation: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )


    @dependencies_bp.route('/clear-cache', methods=['POST'])
    def clear_cache():
        """
        Clear extension cache (for testing/troubleshooting).

        WARNING: This will delete all cached extensions.

        Returns:
            JSON with operation result
        """
        try:
            cache_path = get_extension_cache_path()

            if not cache_path.exists():
                return jsonify({
                    'success': True,
                    'message': 'Cache directory does not exist'
                })

            # Get size before deletion
            status_before = get_cache_status()

            # Delete cache
            import shutil
            shutil.rmtree(cache_path)

            logger.info(f"Cleared extension cache: {status_before['size']} freed")

            return jsonify({
                'success': True,
                'message': f"Cache cleared: {status_before['size']} freed",
                'freed_bytes': status_before['size_bytes'],
                'extensions_removed': status_before['count']
            })

        except Exception as e:
            logger.error(f"Error clearing cache: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    return dependencies_bp
