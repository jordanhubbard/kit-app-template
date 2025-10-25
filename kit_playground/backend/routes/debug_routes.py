#!/usr/bin/env python3
"""
Debug Routes for Kit Playground.

Provides debugging endpoints to help diagnose UI issues.
"""

from flask import Blueprint, jsonify
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


def create_debug_routes() -> Blueprint:
    """Create and configure debug routes."""

    debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')

    @debug_bp.route('/ui-source/<path:file_path>', methods=['GET'])
    def get_ui_source(file_path):
        """
        Get the source code of a UI file for debugging.
        
        This helps verify what's actually in the source files.
        """
        try:
            # Get the UI directory
            backend_dir = Path(__file__).parent.parent
            ui_dir = backend_dir.parent / 'ui' / 'src'
            
            # Construct the full path
            full_path = ui_dir / file_path
            
            # Security check - ensure the path is within the UI directory
            if not str(full_path.resolve()).startswith(str(ui_dir.resolve())):
                return jsonify({'error': 'Invalid path'}), 403
            
            if not full_path.exists():
                return jsonify({'error': f'File not found: {file_path}'}), 404
            
            # Read the file
            with open(full_path, 'r') as f:
                content = f.read()
            
            return jsonify({
                'path': file_path,
                'full_path': str(full_path),
                'exists': True,
                'size': len(content),
                'content': content,
                'line_count': content.count('\n') + 1,
            })
        except Exception as e:
            logger.error(f"Error reading UI source: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @debug_bp.route('/ui-check', methods=['GET'])
    def check_ui_files():
        """
        Check key UI files to verify their state.
        """
        try:
            backend_dir = Path(__file__).parent.parent
            ui_dir = backend_dir.parent / 'ui'
            src_dir = ui_dir / 'src'
            
            checks = {}
            
            # Check key files
            key_files = [
                'main.tsx',
                'App.tsx',
                'components/templates/TemplateCard.tsx',
                'components/panels/TemplateGrid.tsx',
            ]
            
            for file_path in key_files:
                full_path = src_dir / file_path
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        content = f.read()
                    checks[file_path] = {
                        'exists': True,
                        'size': len(content),
                        'has_min_h_320': 'min-h-[320px]' in content,
                        'has_grid_cols': 'grid-cols-' in content,
                        'has_v2_redesign': 'v2.0-redesign' in content or 'v2-redesign' in content,
                    }
                else:
                    checks[file_path] = {'exists': False}
            
            # Check dist directory
            dist_dir = ui_dir / 'dist'
            checks['dist_exists'] = dist_dir.exists()
            if dist_dir.exists():
                checks['dist_files'] = [f.name for f in dist_dir.glob('**/*') if f.is_file()][:10]
            
            # Check node_modules/.vite cache
            vite_cache_dir = ui_dir / 'node_modules' / '.vite'
            checks['vite_cache_exists'] = vite_cache_dir.exists()
            
            return jsonify({
                'ui_dir': str(ui_dir),
                'src_dir': str(src_dir),
                'checks': checks,
                'environment': {
                    'VITE_API_BASE_URL': os.environ.get('VITE_API_BASE_URL'),
                    'VITE_WS_BASE_URL': os.environ.get('VITE_WS_BASE_URL'),
                    'REMOTE': os.environ.get('REMOTE'),
                },
            })
        except Exception as e:
            logger.error(f"Error checking UI files: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @debug_bp.route('/vite-status', methods=['GET'])
    def check_vite_status():
        """
        Check if Vite dev server is running and what it's serving.
        """
        try:
            import subprocess
            
            # Find Vite process
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            
            vite_processes = [
                line for line in result.stdout.split('\n')
                if 'vite' in line.lower() and 'grep' not in line.lower()
            ]
            
            # Get working directory of Vite process
            vite_pids = []
            for line in vite_processes:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    try:
                        pwd_result = subprocess.run(
                            ['pwdx', pid],
                            capture_output=True,
                            text=True
                        )
                        vite_pids.append({
                            'pid': pid,
                            'cwd': pwd_result.stdout.strip(),
                            'cmd_line': ' '.join(parts[10:]) if len(parts) > 10 else 'unknown',
                        })
                    except:
                        pass
            
            return jsonify({
                'vite_running': len(vite_processes) > 0,
                'process_count': len(vite_processes),
                'processes': vite_pids,
            })
        except Exception as e:
            logger.error(f"Error checking Vite status: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return debug_bp

