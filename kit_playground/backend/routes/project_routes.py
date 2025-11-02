"""
Project build and run routes for Kit Playground.
"""
import os
import sys
import signal
import logging
import subprocess
import threading
import shutil
import time
from pathlib import Path
from typing import Dict

from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO

# Import PortRegistry for centralized port management
from kit_playground.backend.source.port_registry import PortRegistry
from kit_playground.backend.utils.network import get_hostname_for_client
from kit_playground.backend.source.process_monitor import get_process_monitor

logger = logging.getLogger(__name__)

# Create blueprint
project_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


def _wait_for_xpra_ready(display: int, port: int, timeout: int = 30) -> bool:
    """Wait for Xpra to be ready to accept connections.

    Args:
        display: Xpra display number
        port: Xpra TCP port
        timeout: Maximum time to wait in seconds

    Returns:
        True if Xpra is ready, False if timeout
    """
    import socket

    logger.info(f"Waiting for Xpra display :{display} to be ready...")

    start_time = time.time()
    port_ready = False
    x11_ready = False

    while time.time() - start_time < timeout:
        try:
            # Check if Xpra process is running
            result = subprocess.run(
                ['xpra', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and f':{display}' in result.stdout:
                # Xpra process is running, now check if port is listening
                # Note: Always use localhost for health checks (internal communication)
                if not port_ready:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    try:
                        result = sock.connect_ex(('localhost', port))
                        sock.close()
                        if result == 0:
                            logger.info(f"Xpra port {port} is listening...")
                            port_ready = True
                    except Exception:
                        pass
                    finally:
                        sock.close()

                # Once port is ready, check if X11 server is ready
                if port_ready and not x11_ready:
                    # Test X11 connection using xdpyinfo
                    try:
                        test_env = os.environ.copy()
                        test_env['DISPLAY'] = f':{display}'
                        result = subprocess.run(
                            ['xdpyinfo'],
                            env=test_env,
                            capture_output=True,
                            timeout=2
                        )
                        if result.returncode == 0:
                            logger.info(f"Xpra X11 server on :{display} is ready!")
                            x11_ready = True
                            # Give it one more second for stability
                            time.sleep(1)
                            return True
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        # xdpyinfo not available or timed out, wait a bit more
                        if time.time() - start_time > 5:  # After 5s, assume it's ready
                            logger.info(f"Xpra display :{display} port ready (X11 check unavailable)")
                            time.sleep(2)  # Additional safety delay
                            return True
        except Exception:
            pass

        time.sleep(0.5)

    logger.warning(f"Timeout waiting for Xpra display :{display} to be ready")
    return False


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent.parent


def create_project_routes(
    playground_app,
    socketio: SocketIO,
    processes: Dict[str, subprocess.Popen],
    xpra_manager,
    security_validator
):
    """
    Create and configure project routes.

    Args:
        playground_app: PlaygroundApp instance
        socketio: SocketIO instance for real-time logging
        processes: Dictionary tracking running processes
        xpra_manager: XpraManager instance
        security_validator: Object with security validation methods

    Returns:
        Flask Blueprint with project routes configured
    """

    @project_bp.route('/environment', methods=['GET'])
    def get_environment():
        """Get environment capabilities for smart launch decisions."""
        has_display = 'DISPLAY' in os.environ and os.environ['DISPLAY']
        return jsonify({
            'hasDisplay': has_display,
            'display': os.environ.get('DISPLAY', None),
            'canDirectLaunch': has_display,
            'xpraAvailable': True,  # Assume Xpra is always available
        })

    @project_bp.route('/build', methods=['POST'])
    def build_project():
        """Build a Kit project using repo.sh wrapper from the app directory."""
        try:
            data = request.json
            project_path = data.get('projectPath')
            project_name = data.get('projectName')

            # SECURITY: Validate project_name to prevent command injection
            if project_name and not security_validator._is_safe_project_name(project_name):
                return jsonify({
                    'error': 'Invalid project name. Avoid special characters like ; & | $ ` ( ) < > \\ " \' and control characters.'
                }), 400

            repo_root = Path(__file__).parent.parent.parent.parent
            logger.info("Building project: %s", project_name)

            # Determine which repo.sh to use
            if project_path:
                # SECURITY: Validate and normalize project_path
                app_dir = security_validator._validate_project_path(repo_root, project_path)
                if not app_dir:
                    return jsonify({'error': 'Invalid project path'}), 400

                wrapper_script = app_dir / 'repo.sh'

                if wrapper_script.exists():
                    logger.info("Using wrapper from: %s", app_dir)
                    cmd = ['./repo.sh', 'build', '--config', 'release']
                    cwd = str(app_dir)
                else:
                    logger.info("Wrapper not found, using repo root")
                    cmd = [str(repo_root / 'repo.sh'), 'build', '--config', 'release']
                    cwd = str(repo_root)
            else:
                cmd = [str(repo_root / 'repo.sh'), 'build', '--config', 'release']
                cwd = str(repo_root)

            # Log the command being executed (critical for user reproducibility)
            logger.info("=" * 80)
            logger.info(f"BUILD COMMAND: {project_name}")
            logger.info(f"Command: {' '.join(cmd)}")
            logger.info(f"Working directory: {cwd}")
            logger.info("=" * 80)

            # Emit command to UI so users can reproduce it
            socketio.emit('log', {
                'level': 'info',
                'source': 'build',
                'message': f'Building {project_name}...'
            })
            socketio.emit('log', {
                'level': 'info',
                'source': 'build',
                'message': f'$ cd {cwd}'
            })
            socketio.emit('log', {
                'level': 'info',
                'source': 'build',
                'message': f'$ {" ".join(cmd)}'
            })

            # Use script command to force PTY (pseudo-terminal) for unbuffered output
            # This makes the subprocess think it's running in a real terminal,
            # preventing output buffering
            import pty
            import select

            # Set environment to force unbuffered output
            build_env = os.environ.copy()
            build_env['PYTHONUNBUFFERED'] = '1'
            build_env['PYTHONIOENCODING'] = 'utf-8'
            build_env['TERM'] = 'xterm-256color'  # Ensure terminal features work

            # Use pty.spawn for true unbuffered output
            master_fd, slave_fd = pty.openpty()

            process = subprocess.Popen(
                cmd,
                stdout=slave_fd,
                stderr=slave_fd,
                stdin=slave_fd,
                cwd=cwd,
                env=build_env,
                bufsize=0,
                preexec_fn=os.setsid  # Create new session
            )

            # Close slave fd in parent process
            os.close(slave_fd)

            # Stream output in real-time from PTY
            stdout_lines = []

            try:
                while True:
                    # Check if process is still running
                    if process.poll() is not None:
                        # Read any remaining output
                        try:
                            while True:
                                rlist, _, _ = select.select([master_fd], [], [], 0)
                                if not rlist:
                                    break
                                data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                                if not data:
                                    break
                                for line in data.splitlines():
                                    if line.strip():
                                        stdout_lines.append(line)
                                        socketio.emit('log', {
                                            'level': 'info',
                                            'source': 'build',
                                            'message': line
                                        })
                        except OSError:
                            pass
                        break

                    # Read output with select
                    rlist, _, _ = select.select([master_fd], [], [], 0.1)
                    if rlist:
                        try:
                            data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                            if data:
                                for line in data.splitlines():
                                    if line.strip():
                                        stdout_lines.append(line)
                                        socketio.emit('log', {
                                            'level': 'info',
                                            'source': 'build',
                                            'message': line
                                        })
                        except OSError:
                            break
            finally:
                os.close(master_fd)

            # Wait for process to fully terminate and get exit code
            try:
                returncode = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate within timeout, forcing kill")
                process.kill()
                returncode = process.wait()

            # Log full output to backend logs
            if stdout_lines:
                logger.info("Build output: %s", '\n'.join(stdout_lines))

            # Emit completion message
            success = returncode == 0
            socketio.emit('log', {
                'level': 'info' if success else 'error',
                'source': 'build',
                'message': f'Build {"completed successfully" if success else "failed"} (exit code: {returncode})'
            })

            return jsonify({
                'success': success,
                'output': '\n'.join(stdout_lines),
                'error': None if success else f'Build failed with exit code {returncode}'
            })
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Build timeout (300s)'}), 500
        except Exception as e:
            logger.error(f"Failed to build project: {e}")
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/run', methods=['POST'])
    def run_project():
        """Run a Kit project using repo.sh launch."""
        try:
            data = request.json
            project_path = data.get('projectPath')
            project_name = data.get('projectName')
            use_xpra = data.get('useXpra', None)  # None means "auto-detect"
            use_web_preview = data.get('useWebPreview', False)
            streaming_port = data.get('streamingPort', 47995)

            if not project_name:
                return jsonify({'error': 'projectName required'}), 400

            # SECURITY: Validate project_name
            if not security_validator._is_safe_project_name(project_name):
                return jsonify({
                    'error': 'Invalid project name. Avoid special characters like ; & | $ ` ( ) < > \\ " \' and control characters.'
                }), 400

            kit_file = f"{project_name}.kit"
            repo_root = Path(__file__).parent.parent.parent.parent

            # Detect environment capabilities
            has_display = 'DISPLAY' in os.environ and os.environ['DISPLAY']
            logger.info(f"Environment check: DISPLAY={os.environ.get('DISPLAY', 'not set')}, has_display={has_display}")

            preview_url = None
            streaming_url = None
            is_streaming_app = False

            # Check if this is a streaming app (Kit App Streaming)
            try:
                from tools.repoman.streaming_utils import is_streaming_app as check_streaming
                kit_file_path = repo_root / "source" / "apps" / project_name / kit_file
                logger.info(f"Checking for streaming in: {kit_file_path}")
                logger.info(f"Kit file exists: {kit_file_path.exists()}")
                if kit_file_path.exists():
                    is_streaming_app = check_streaming(kit_file_path)
                    logger.info(f"Kit App Streaming (KAS) detection result: {is_streaming_app}")

                    # DEBUG: Let's verify what's in the file
                    if not is_streaming_app:
                        try:
                            content = kit_file_path.read_text()
                            has_dep = 'omni.kit.livestream.app' in content
                            logger.warning(f"Streaming detection returned False, but file contains dependency: {has_dep}")
                            if has_dep:
                                logger.warning("Forcing is_streaming_app = True based on file content")
                                is_streaming_app = True
                        except Exception as debug_e:
                            logger.error(f"Could not debug-read kit file: {debug_e}")
            except Exception as e:
                logger.warning(f"Could not check if app has Kit App Streaming: {e}")

            # SMART DECISION TREE for launch mode
            # 1. If KAS enabled → Always use KAS (user's explicit intent)
            # 2. If no DISPLAY and no KAS → Must use Xpra
            # 3. If DISPLAY set and no KAS → Use user's choice (default direct, optional Xpra)

            if is_streaming_app:
                # Rule 1: KAS enabled - always use it
                logger.info("DECISION: Using Kit App Streaming (KAS enabled)")
                use_xpra = False
                use_web_preview = True
            elif not has_display:
                # Rule 2: No DISPLAY - must use Xpra
                logger.info("DECISION: No DISPLAY available - forcing Xpra mode")
                use_xpra = True
                # Note: Log message will be emitted later after launch starts
            else:
                # Rule 3: DISPLAY available - respect user choice or default to direct
                if use_xpra is None:
                    use_xpra = False  # Default to direct display
                logger.info(f"DECISION: DISPLAY available - using {'Xpra preview' if use_xpra else 'direct display'}")

            logger.info(f"Final launch mode: KAS={is_streaming_app}, Xpra={use_xpra}, Direct={not use_xpra and not is_streaming_app}")

            # Determine launch mode
            # Mode 1: Kit App Streaming (always --no-window, URL on stdout)
            # Mode 2: Direct Launch (no Xpra, direct DISPLAY)
            # Mode 3: Xpra Display Server (browser preview of X display)

            if is_streaming_app or (use_web_preview and is_streaming_app):
                # MODE 1: Kit App Streaming
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': '=== Kit App Streaming Mode ==='
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'Port: {streaming_port}'
                })

                # Build launch command with --streaming flag
                launch_cmd = None
                launch_cwd = None

                if project_path:
                    app_dir = security_validator._validate_project_path(repo_root, project_path)
                    if app_dir:
                        wrapper_script = app_dir / 'repo.sh'
                        if wrapper_script.exists():
                            launch_cmd = ['./repo.sh', 'launch', '--name', kit_file, '--streaming', '--streaming-port', str(streaming_port)]
                            launch_cwd = str(app_dir)
                            logger.info(f"Using project wrapper for streaming launch in {launch_cwd}")

                # Fallback to repo root
                if not launch_cmd:
                    launch_cmd = [str(repo_root / 'repo.sh'), 'launch', '--name', kit_file, '--streaming', '--streaming-port', str(streaming_port)]
                    # Prefer opening file dialogs in the USD assets directory
                    assets_dir = Path.home() / 'OmniverseAssets' / 'USD'
                    assets_dir.mkdir(parents=True, exist_ok=True)
                    launch_cwd = str(assets_dir)

                # Log the launch command
                logger.info("=" * 80)
                logger.info(f"STREAMING LAUNCH COMMAND: {project_name}")
                logger.info(f"Command: {' '.join(launch_cmd)}")
                logger.info(f"Working directory: {launch_cwd}")
                logger.info("=" * 80)

                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'$ cd {launch_cwd}'
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'$ {" ".join(launch_cmd)}'
                })

                try:
                    # Set PYTHONUNBUFFERED for real-time output
                    env = os.environ.copy()
                    env['PYTHONUNBUFFERED'] = '1'

                    process = subprocess.Popen(
                        launch_cmd,
                        cwd=launch_cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env,
                        bufsize=1,
                        preexec_fn=os.setsid  # Create new process group
                    )

                    # Store process
                    processes[project_name] = process

                    # Register process with monitor (streaming doesn't use Xpra)
                    monitor = get_process_monitor()
                    monitor.register_socketio(socketio)
                    monitor.register_process(
                        project_name=project_name,
                        pid=process.pid,
                        streaming_port=streaming_port,
                        is_streaming=True
                    )

                    # Wait for streaming server to be ready
                    from tools.repoman.streaming_utils import wait_for_streaming_ready, get_streaming_url

                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': 'Starting streaming server...'
                    })

                    # Get PortRegistry instance for client host extraction
                    registry = PortRegistry.get_instance()

                    # Extract client host from request headers (same logic as Xpra)
                    # Check X-Forwarded-Host first (set by proxy), then fall back to Host header
                    original_host = request.headers.get('X-Forwarded-Host', request.host)
                    client_host = registry.extract_client_host(original_host)

                    # Get streaming URL with remote hostname. Default to HTTP unless explicitly configured.
                    streaming_url = get_streaming_url(port=streaming_port, hostname=client_host, protocol='http')

                    logger.info(f"[STREAMING URL] Request.host: {request.host}")
                    logger.info(f"[STREAMING URL] X-Forwarded-Host: {request.headers.get('X-Forwarded-Host', 'not set')}")
                    logger.info(f"[STREAMING URL] Client host: {client_host}")
                    logger.info(f"[STREAMING URL] Constructed URL: {streaming_url}")

                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Waiting for streaming server on port {streaming_port}...'
                    })

                    # Wait for server (in a thread to avoid blocking)
                    def wait_and_notify():
                        # Check localhost for readiness (local check), but provide remote URL to client
                        if wait_for_streaming_ready(streaming_port, 'localhost', timeout=30):
                            socketio.emit('log', {
                                'level': 'success',
                                'source': 'runtime',
                                'message': '=== Streaming Ready! ==='
                            })
                            socketio.emit('log', {
                                'level': 'info',
                                'source': 'runtime',
                                'message': f'URL: {streaming_url}'
                            })
                            # Note: If your deployment serves HTTPS for streaming,
                            # switch protocol to https in the backend configuration.
                            # Emit streaming ready event
                            socketio.emit('streaming_ready', {
                                'project': project_name,
                                'url': streaming_url,
                                'port': streaming_port
                            })
                        else:
                            socketio.emit('log', {
                                'level': 'warning',
                                'source': 'runtime',
                                'message': (
                                    'Streaming server did not respond '
                                    'within 30 seconds.'
                                )
                            })
                            socketio.emit('log', {
                                'level': 'info',
                                'source': 'runtime',
                                'message': (
                                    f'Try connecting anyway: {streaming_url}'
                                )
                            })

                    threading.Thread(target=wait_and_notify, daemon=True).start()

                    # Stream output from process
                    def stream_output():
                        """Stream output from both stdout and stderr."""
                        while True:
                            if process.poll() is not None:
                                # Process finished
                                remaining_stdout = process.stdout.read()
                                remaining_stderr = process.stderr.read()

                                if remaining_stdout:
                                    for line in remaining_stdout.strip().split('\n'):
                                        if line:
                                            socketio.emit('log', {
                                                'level': 'info',
                                                'source': 'runtime',
                                                'message': line
                                            })

                                if remaining_stderr:
                                    for line in remaining_stderr.strip().split('\n'):
                                        if line:
                                            socketio.emit('log', {
                                                'level': 'error',
                                                'source': 'runtime',
                                                'message': line
                                            })

                                socketio.emit('log', {
                                    'level': 'info',
                                    'source': 'runtime',
                                    'message': f'Process exited with code: {process.returncode}'
                                })
                                break

                            # Read stdout
                            line = process.stdout.readline()
                            if line:
                                socketio.emit('log', {
                                    'level': 'info',
                                    'source': 'runtime',
                                    'message': line.rstrip()
                                })

                            # Read stderr
                            err_line = process.stderr.readline()
                            if err_line:
                                socketio.emit('log', {
                                    'level': 'error',
                                    'source': 'runtime',
                                    'message': err_line.rstrip()
                                })

                            if not line and not err_line:
                                time.sleep(0.1)

                    threading.Thread(target=stream_output, daemon=True).start()

                    # Return response immediately with streaming URL
                    response_data = {
                        'success': True,
                        'previewUrl': streaming_url,
                        'streamingUrl': streaming_url,
                        'streaming': True,
                        'port': streaming_port
                    }
                    logger.info(f"[STREAMING URL] Returning response: {response_data}")
                    return jsonify(response_data)

                except Exception as e:
                    logger.error(f"Failed to launch with streaming: {e}", exc_info=True)
                    socketio.emit('log', {
                        'level': 'error',
                        'source': 'runtime',
                        'message': f'Launch failed: {str(e)}'
                    })
                    return jsonify({'success': False, 'error': str(e)}), 500

            elif use_xpra:
                # Launch with Xpra using repo.sh --xpra flag
                # This delegates Xpra management to the CLI tool
                if not has_display:
                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': '=== No DISPLAY detected - using Xpra mode ==='
                    })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': 'Using Xpra for browser preview...'
                })

                # Build launch command using repo.sh with --xpra flag
                launch_cmd = None
                launch_cwd = None

                if project_path:
                    app_dir = security_validator._validate_project_path(repo_root, project_path)
                    if app_dir:
                        wrapper_script = app_dir / 'repo.sh'
                        if wrapper_script.exists():
                            # Use project wrapper with --xpra flag
                            launch_cmd = ['./repo.sh', 'launch', '--name', kit_file, '--xpra']
                            launch_cwd = str(app_dir)
                            logger.info(f"Using project wrapper for Xpra launch in {launch_cwd}")

                # Fallback to repo root
                if not launch_cmd:
                    launch_cmd = [str(repo_root / 'repo.sh'), 'launch', '--name', kit_file, '--xpra']
                    # Prefer opening file dialogs in the USD assets directory
                    assets_dir = Path.home() / 'OmniverseAssets' / 'USD'
                    assets_dir.mkdir(parents=True, exist_ok=True)
                    launch_cwd = str(assets_dir)

                # Log the launch command for reproducibility
                logger.info("=" * 80)
                logger.info(f"XPRA LAUNCH COMMAND: {project_name}")
                logger.info(f"Command: {' '.join(launch_cmd)}")
                logger.info(f"Working directory: {launch_cwd}")
                logger.info("=" * 80)

                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'$ cd {launch_cwd}'
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'$ {" ".join(launch_cmd)}'
                })

                # Launch using repo.sh (which handles Xpra setup)
                try:
                    # Set PYTHONUNBUFFERED to ensure Python scripts output in real-time
                    env = os.environ.copy()
                    env['PYTHONUNBUFFERED'] = '1'

                    process = subprocess.Popen(
                        launch_cmd,
                        cwd=launch_cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env,
                        bufsize=1  # Line buffered
                    )

                    # Store process for later management
                    processes[project_name] = process

                    # Get preview URL from PortRegistry (centralized port management)
                    registry = PortRegistry.get_instance()

                    # Register Xpra display if not already registered
                    xpra_display = 100  # Default display
                    xpra_port = 10000 + (xpra_display - 100)
                    registry.register_xpra_display(display=xpra_display, port=xpra_port)

                    # Register process with monitor for automatic Xpra cleanup
                    monitor = get_process_monitor()
                    monitor.register_socketio(socketio)
                    monitor.register_process(
                        project_name=project_name,
                        pid=process.pid,
                        xpra_display=xpra_display,
                        is_streaming=False
                    )

                    # Wait for Xpra to be ready before returning preview URL
                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Waiting for Xpra display :{xpra_display} to be ready...'
                    })

                    # Check if Xpra is ready
                    xpra_ready = _wait_for_xpra_ready(xpra_display, xpra_port, timeout=30)

                    if not xpra_ready:
                        socketio.emit('log', {
                            'level': 'warning',
                            'source': 'runtime',
                            'message': 'Xpra may not be fully ready, but continuing...'
                        })

                    # Extract client host from request
                    # Check X-Forwarded-Host first (set by proxy), then fall back to Host header
                    original_host = request.headers.get('X-Forwarded-Host', request.host)
                    client_host = registry.extract_client_host(original_host)

                    # Construct preview URL using registry
                    preview_url = registry.get_preview_url(display=xpra_display, client_host=client_host)

                    logger.info(f"[PREVIEW URL] Request.host: {request.host}")
                    logger.info(f"[PREVIEW URL] X-Forwarded-Host: {request.headers.get('X-Forwarded-Host', 'not set')}")
                    logger.info(f"[PREVIEW URL] Original host: {original_host}")
                    logger.info(f"[PREVIEW URL] Client host: {client_host}")
                    logger.info(f"[PREVIEW URL] Constructed URL: {preview_url}")

                    socketio.emit('log', {
                        'level': 'success',
                        'source': 'runtime',
                        'message': f'Application launched with Xpra'
                    })
                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Preview: {preview_url}'
                    })

                    # Emit xpra_ready event for frontend to auto-open
                    socketio.emit('xpra_ready', {
                        'project': project_name,
                        'url': preview_url,
                        'display': xpra_display,
                        'port': xpra_port
                    })

                    # Start thread to stream output from both stdout and stderr concurrently
                    def stream_output():
                        """Stream output from both stdout and stderr without blocking."""
                        while True:
                            # Check if process is still running
                            if process.poll() is not None:
                                # Process finished, read any remaining output
                                remaining_stdout = process.stdout.read()
                                remaining_stderr = process.stderr.read()

                                if remaining_stdout:
                                    for line in remaining_stdout.strip().split('\n'):
                                        if line:
                                            socketio.emit('log', {
                                                'level': 'info',
                                                'source': 'runtime',
                                                'message': line
                                            })

                                if remaining_stderr:
                                    for line in remaining_stderr.strip().split('\n'):
                                        if line:
                                            socketio.emit('log', {
                                                'level': 'error',
                                                'source': 'runtime',
                                                'message': line
                                            })

                                socketio.emit('log', {
                                    'level': 'info',
                                    'source': 'runtime',
                                    'message': f'Process exited with code: {process.returncode}'
                                })
                                break

                            # Read from stdout (non-blocking)
                            line = process.stdout.readline()
                            if line:
                                socketio.emit('log', {
                                    'level': 'info',
                                    'source': 'runtime',
                                    'message': line.rstrip()
                                })

                            # Read from stderr (non-blocking)
                            err_line = process.stderr.readline()
                            if err_line:
                                socketio.emit('log', {
                                    'level': 'error',
                                    'source': 'runtime',
                                    'message': err_line.rstrip()
                                })

                            # Small sleep to prevent busy waiting if no output
                            if not line and not err_line:
                                time.sleep(0.1)

                    threading.Thread(target=stream_output, daemon=True).start()

                except Exception as e:
                    logger.error(f"Failed to launch with Xpra: {e}", exc_info=True)
                    socketio.emit('log', {
                        'level': 'error',
                        'source': 'runtime',
                        'message': f'Launch failed: {str(e)}'
                    })
                    return jsonify({'success': False, 'error': str(e)}), 500

            else:
                # Direct launch (normal mode)
                cmd = None
                cwd = None

                if project_path:
                    # SECURITY: Validate and normalize project_path
                    app_dir = security_validator._validate_project_path(repo_root, project_path)
                    if not app_dir:
                        return jsonify({'error': 'Invalid project path'}), 400

                    wrapper_script = app_dir / 'repo.sh'

                    if wrapper_script.exists():
                        logger.info("Launching from: %s", app_dir)
                        cmd = ['./repo.sh', 'launch', '--name', kit_file]
                        cwd = str(app_dir)
                    else:
                        cmd = [str(repo_root / 'repo.sh'), 'launch', '--name', kit_file]
                        cwd = str(repo_root)
                else:
                    cmd = [str(repo_root / 'repo.sh'), 'launch', '--name', kit_file]
                    # Prefer opening file dialogs in the USD assets directory
                    assets_dir = Path.home() / 'OmniverseAssets' / 'USD'
                    assets_dir.mkdir(parents=True, exist_ok=True)
                    cwd = str(assets_dir)

                # Log the command being executed (critical for user reproducibility)
                logger.info("=" * 80)
                logger.info(f"LAUNCH COMMAND: {project_name}")
                logger.info(f"Command: {' '.join(cmd)}")
                logger.info(f"Working directory: {cwd}")
                logger.info("=" * 80)

                # Emit command to UI so users can reproduce it
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'$ cd {cwd}'
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'$ {" ".join(cmd)}'
                })

                # Set PYTHONUNBUFFERED for real-time output
                env = os.environ.copy()
                env['PYTHONUNBUFFERED'] = '1'

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=cwd,
                    env=env,
                    bufsize=1,  # Line buffered
                    preexec_fn=os.setsid  # Create new process group for clean termination
                )

                # SECURITY: Limit number of concurrent processes
                if len(processes) >= 10:
                    return jsonify({
                        'error': 'Too many running processes. Please stop some before starting new ones.'
                    }), 429

                processes[project_name] = process

                socketio.emit('log', {
                    'level': 'success',
                    'source': 'runtime',
                    'message': f'Launching {kit_file}...'
                })

                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': 'Note: The application window will appear on the host machine.'
                })

                # Start a thread to stream output from both stdout and stderr concurrently
                def stream_output():
                    """Stream output from both stdout and stderr without blocking."""
                    while True:
                        # Check if process is still running
                        if process.poll() is not None:
                            # Process finished, read any remaining output
                            remaining_stdout = process.stdout.read()
                            remaining_stderr = process.stderr.read()

                            if remaining_stdout:
                                for line in remaining_stdout.strip().split('\n'):
                                    if line:
                                        socketio.emit('log', {
                                            'level': 'info',
                                            'source': 'runtime',
                                            'message': line
                                        })

                            if remaining_stderr:
                                for line in remaining_stderr.strip().split('\n'):
                                    if line:
                                        socketio.emit('log', {
                                            'level': 'error',
                                            'source': 'runtime',
                                            'message': line
                                        })

                            socketio.emit('log', {
                                'level': 'info',
                                'source': 'runtime',
                                'message': f'Process exited with code: {process.returncode}'
                            })
                            break

                        # Read from stdout (non-blocking)
                        line = process.stdout.readline()
                        if line:
                            socketio.emit('log', {
                                'level': 'info',
                                'source': 'runtime',
                                'message': line.rstrip()
                            })

                        # Read from stderr (non-blocking)
                        err_line = process.stderr.readline()
                        if err_line:
                            socketio.emit('log', {
                                'level': 'error',
                                'source': 'runtime',
                                'message': err_line.rstrip()
                            })

                        # Small sleep to prevent busy waiting if no output
                        if not line and not err_line:
                            time.sleep(0.1)

                threading.Thread(target=stream_output, daemon=True).start()

            response_data = {
                'success': True,
                'previewUrl': preview_url
            }
            logger.info(f"[PREVIEW URL] Returning response: {response_data}")
            return jsonify(response_data)
        except Exception as e:
            logger.error(f"Failed to run project: {e}")
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/discover', methods=['GET'])
    def discover_projects():
        """Discover existing Kit projects in a directory."""
        try:
            path = request.args.get('path')
            if not path:
                return jsonify({'error': 'path parameter required'}), 400

            # Basic path validation
            validated_path = security_validator._validate_filesystem_path(path)
            if not validated_path:
                return jsonify({'error': 'Invalid or inaccessible path'}), 400

            # Find .kit files in the directory
            projects = []
            if validated_path.exists() and validated_path.is_dir():
                # Get repo root for calculating full relative paths
                repo_root = get_repo_root()

                for kit_file in validated_path.glob('*/*.kit'):
                    project_name = kit_file.stem
                    project_dir = kit_file.parent

                    projects.append({
                        'id': project_name,
                        'name': project_name,
                        'displayName': project_name,
                        'path': str(project_dir.relative_to(repo_root)),  # Full path from repo root
                        'kitFile': str(kit_file),
                        'relativePath': str(project_dir.relative_to(repo_root)),  # Full path from repo root
                        'status': 'ready'
                    })

            return jsonify({'projects': projects})
        except Exception as e:
            logger.error(f"Failed to discover projects: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/stop', methods=['POST'])
    def stop_project_body():
        """Stop a running project (accepts project name in request body)."""
        try:
            data = request.json
            project_name = data.get('projectName')

            if not project_name:
                return jsonify({'error': 'projectName required'}), 400

            if project_name in processes:
                process = processes[project_name]

                # Terminate the entire process group to ensure child processes are stopped
                # This is necessary because repo.sh spawns the Kit application as a child process
                try:
                    # Send SIGTERM to the process group
                    import signal
                    pgid = os.getpgid(process.pid)
                    os.killpg(pgid, signal.SIGTERM)

                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Sending SIGTERM to {project_name} (PID {process.pid}, PGID {pgid})...'
                    })

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        socketio.emit('log', {
                            'level': 'success',
                            'source': 'runtime',
                            'message': f'Application stopped gracefully'
                        })
                    except subprocess.TimeoutExpired:
                        # Force kill if process doesn't terminate gracefully
                        socketio.emit('log', {
                            'level': 'warning',
                            'source': 'runtime',
                            'message': f'Application did not stop gracefully, sending SIGKILL...'
                        })
                        os.killpg(pgid, signal.SIGKILL)
                        process.wait(timeout=2)

                except ProcessLookupError:
                    # Process already terminated
                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Process already terminated'
                    })

                # Unregister from process monitor
                monitor = get_process_monitor()
                monitor.unregister_process(project_name)

                del processes[project_name]
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Project not running'}), 404
        except Exception as e:
            logger.error(f"Failed to stop project: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/stop/<project_name>', methods=['POST'])
    def stop_project(project_name: str):
        """Stop a running project (legacy endpoint with URL parameter)."""
        try:
            if project_name in processes:
                process = processes[project_name]

                # Terminate the entire process group to ensure child processes are stopped
                try:
                    import signal
                    pgid = os.getpgid(process.pid)
                    os.killpg(pgid, signal.SIGTERM)

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if process doesn't terminate gracefully
                        os.killpg(pgid, signal.SIGKILL)
                        process.wait(timeout=2)

                except ProcessLookupError:
                    # Process already terminated
                    pass

                # Unregister from process monitor
                monitor = get_process_monitor()
                monitor.unregister_process(project_name)

                del processes[project_name]
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Project not running'}), 404
        except Exception as e:
            logger.error(f"Failed to stop project: {e}")
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/delete', methods=['POST'])
    def delete_project():
        """Delete a project directory and all its contents."""
        try:
            data = request.json
            project_id = data.get('projectId')
            projects_path = data.get('projectsPath', '_build/apps')

            if not project_id:
                return jsonify({'error': 'projectId required'}), 400

            # SECURITY: Validate project_id to prevent path traversal
            if not security_validator._is_safe_project_name(project_id):
                return jsonify({
                    'error': 'Invalid project ID. Avoid special characters and path traversal attempts.'
                }), 400

            # Get repo root
            repo_root = Path(__file__).parent.parent.parent.parent

            # Validate projects path
            validated_projects_path = security_validator._validate_filesystem_path(projects_path)
            if not validated_projects_path:
                return jsonify({'error': 'Invalid projects path'}), 400

            # Construct project directory path
            project_dir = validated_projects_path / project_id

            # Security check: Ensure project_dir is within the validated projects path
            try:
                project_dir = project_dir.resolve()
                validated_projects_path = validated_projects_path.resolve()
                if not str(project_dir).startswith(str(validated_projects_path)):
                    return jsonify({'error': 'Invalid project path - outside projects directory'}), 403
            except Exception as e:
                logger.error(f"Path resolution error: {e}")
                return jsonify({'error': 'Invalid project path'}), 400

            # Check if project directory exists
            if not project_dir.exists():
                return jsonify({'error': 'Project not found'}), 404

            if not project_dir.is_dir():
                return jsonify({'error': 'Project path is not a directory'}), 400

            # Stop the project if it's running
            if project_id in processes:
                logger.info(f"Stopping running project before deletion: {project_id}")
                process = processes[project_id]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                # Unregister from process monitor
                monitor = get_process_monitor()
                monitor.unregister_process(project_id)
                del processes[project_id]

            # Delete the project directory from _build/apps
            logger.info(f"Deleting project directory: {project_dir}")
            shutil.rmtree(project_dir)

            # Also delete associated setup extension and source files
            setup_ext_name = f"{project_id}_setup"

            # Remove from source/extensions/
            source_ext_dir = repo_root / "source" / "extensions" / setup_ext_name
            if source_ext_dir.exists():
                logger.info(f"Removing setup extension: {source_ext_dir}")
                shutil.rmtree(source_ext_dir)

            # Remove from source/apps/ (if it exists there)
            source_app_dir = repo_root / "source" / "apps" / project_id
            if source_app_dir.exists():
                logger.info(f"Removing source app: {source_app_dir}")
                shutil.rmtree(source_app_dir)

            # Remove from build directories (all platforms)
            build_dir = repo_root / "_build"
            if build_dir.exists():
                for platform_dir in build_dir.iterdir():
                    if not platform_dir.is_dir():
                        continue
                    for config_dir in platform_dir.iterdir():
                        if not config_dir.is_dir():
                            continue

                        # Remove .kit files and scripts
                        for pattern in [f"{project_id}.kit*", f"tests-{project_id}*"]:
                            for file in config_dir.glob(pattern):
                                if file.is_file():
                                    logger.info(f"Removing build artifact: {file}")
                                    file.unlink()

                        # Remove extensions
                        exts_dir = config_dir / "exts"
                        if exts_dir.exists():
                            for ext_name in [setup_ext_name, project_id]:
                                ext_path = exts_dir / ext_name
                                if ext_path.exists():
                                    logger.info(f"Removing built extension: {ext_path}")
                                    shutil.rmtree(ext_path)

            socketio.emit('log', {
                'level': 'info',
                'source': 'system',
                'message': f'Project and all associated files deleted: {project_id}'
            })

            return jsonify({'success': True})

        except Exception as e:
            logger.error(f"Failed to delete project: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/clean-all', methods=['POST'])
    def clean_all_projects():
        """Clean all user-created applications and extensions using make clean-apps."""
        try:
            repo_root = get_repo_root()

            # Log the operation
            logger.info("=" * 80)
            logger.info("CLEAN ALL PROJECTS")
            logger.info(f"Command: make clean-apps")
            logger.info(f"Working directory: {repo_root}")
            logger.info("=" * 80)

            # Emit to UI
            if socketio:
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'system',
                    'message': 'Cleaning all user-created applications and extensions...'
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'system',
                    'message': f'$ cd {repo_root}'
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'system',
                    'message': '$ make clean-apps'
                })

            # Execute make clean-apps
            process = subprocess.Popen(
                ['make', 'clean-apps'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(repo_root),
                bufsize=1,
                universal_newlines=True
            )

            # Stream output in real-time
            stdout_lines = []
            stderr_lines = []

            while True:
                if process.poll() is not None:
                    # Process finished, read any remaining output
                    remaining_stdout = process.stdout.read()
                    remaining_stderr = process.stderr.read()

                    if remaining_stdout:
                        for line in remaining_stdout.strip().split('\n'):
                            if line:
                                stdout_lines.append(line)
                                if socketio:
                                    socketio.emit('log', {
                                        'level': 'info',
                                        'source': 'system',
                                        'message': line
                                    })

                    if remaining_stderr:
                        for line in remaining_stderr.strip().split('\n'):
                            if line:
                                stderr_lines.append(line)
                                if socketio:
                                    socketio.emit('log', {
                                        'level': 'error',
                                        'source': 'system',
                                        'message': line
                                    })
                    break

                # Read stdout
                line = process.stdout.readline()
                if line:
                    line = line.rstrip()
                    stdout_lines.append(line)
                    if socketio:
                        socketio.emit('log', {
                            'level': 'info',
                            'source': 'system',
                            'message': line
                        })

                # Read stderr
                err_line = process.stderr.readline()
                if err_line:
                    err_line = err_line.rstrip()
                    stderr_lines.append(err_line)
                    if socketio:
                        socketio.emit('log', {
                            'level': 'error',
                            'source': 'system',
                            'message': err_line
                        })

                if not line and not err_line:
                    time.sleep(0.1)

            returncode = process.returncode

            # Log to backend
            if stdout_lines:
                logger.info("Clean output: %s", '\n'.join(stdout_lines))
            if stderr_lines:
                logger.info("Clean stderr: %s", '\n'.join(stderr_lines))

            success = returncode == 0

            if success and socketio:
                socketio.emit('log', {
                    'level': 'success',
                    'source': 'system',
                    'message': 'All projects cleaned successfully!'
                })

            return jsonify({
                'success': success,
                'output': '\n'.join(stdout_lines),
                'error': '\n'.join(stderr_lines) if not success else None
            })

        except Exception as e:
            logger.error(f"Failed to clean projects: {e}", exc_info=True)
            if socketio:
                socketio.emit('log', {
                    'level': 'error',
                    'source': 'system',
                    'message': f'Clean failed: {str(e)}'
                })
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/cancel', methods=['POST'])
    def cancel_job():
        """Cancel a running job (build or launch).

        Request body:
            - jobId: Job ID (optional, for future use)
            - projectName: Project name (required)

        Returns:
            JSON response with cancellation status
        """
        try:
            data = request.json
            project_name = data.get('projectName')
            job_id = data.get('jobId')

            if not project_name:
                return jsonify({'error': 'projectName required'}), 400

            logger.info(f"Canceling job for project: {project_name}")

            # Check if process exists
            if project_name not in processes:
                logger.warning(f"No running process found for project: {project_name}")
                return jsonify({
                    'success': True,
                    'message': f'No running process found for {project_name}',
                    'wasRunning': False
                })

            process = processes[project_name]

            # Check if process is still alive
            if process.poll() is not None:
                logger.info(f"Process for {project_name} already terminated")
                # Unregister from process monitor
                monitor = get_process_monitor()
                monitor.unregister_process(project_name)
                del processes[project_name]
                return jsonify({
                    'success': True,
                    'message': f'Process for {project_name} was already terminated',
                    'wasRunning': False
                })

            # Terminate the process group (SIGTERM first, then SIGKILL if needed)
            try:
                # Get the process group ID
                pgid = os.getpgid(process.pid)
                logger.info(f"Sending SIGTERM to process group {pgid}")

                # Send SIGTERM to the entire process group
                os.killpg(pgid, signal.SIGTERM)

                # Wait up to 3 seconds for graceful shutdown
                try:
                    process.wait(timeout=3)
                    logger.info(f"Process {project_name} terminated gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it didn't terminate
                    logger.warning(f"Process {project_name} didn't terminate gracefully, sending SIGKILL")
                    os.killpg(pgid, signal.SIGKILL)
                    process.wait(timeout=1)

                # Emit log message
                if socketio:
                    socketio.emit('log', {
                        'level': 'info',
                        'source': 'system',
                        'message': f'✓ Canceled {project_name}'
                    })

                # Unregister from process monitor
                monitor = get_process_monitor()
                monitor.unregister_process(project_name)

                # Remove from tracking
                del processes[project_name]

                logger.info(f"Successfully canceled job for {project_name}")

                return jsonify({
                    'success': True,
                    'message': f'Successfully canceled {project_name}',
                    'wasRunning': True
                })

            except ProcessLookupError:
                # Process already gone
                logger.info(f"Process {project_name} already terminated (ProcessLookupError)")
                if project_name in processes:
                    # Unregister from process monitor
                    monitor = get_process_monitor()
                    monitor.unregister_process(project_name)
                    del processes[project_name]
                return jsonify({
                    'success': True,
                    'message': f'Process for {project_name} was already terminated',
                    'wasRunning': False
                })
            except Exception as e:
                logger.error(f"Error terminating process {project_name}: {e}")
                # Still remove from tracking
                if project_name in processes:
                    # Unregister from process monitor
                    monitor = get_process_monitor()
                    monitor.unregister_process(project_name)
                    del processes[project_name]
                return jsonify({
                    'success': False,
                    'error': f'Error terminating process: {str(e)}',
                    'wasRunning': True
                }), 500

        except Exception as e:
            logger.error(f"Failed to cancel job: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @project_bp.route('/list', methods=['GET'])
    def list_projects():
        """List all user-created projects.

        Scans the source/apps directory for user-created projects,
        excluding system directories (exts, extscache) and test projects.

        Returns:
            JSON response with list of projects and their metadata
        """
        try:
            from datetime import datetime

            # Get the repo root
            repo_root = get_repo_root()
            apps_dir = repo_root / 'source' / 'apps'

            if not apps_dir.exists():
                logger.warning(f"Apps directory not found: {apps_dir}")
                return jsonify({
                    'success': True,
                    'projects': [],
                    'count': 0
                })

            projects = []

            # Scan the apps directory
            for item in apps_dir.iterdir():
                # Skip system directories and hidden files
                if item.name in ['exts', 'extscache', '.', '..'] or item.name.startswith('.'):
                    continue

                # Only process directories
                if not item.is_dir():
                    continue

                # Look for a .kit file
                kit_files = list(item.glob('*.kit'))
                if not kit_files:
                    continue

                kit_file = kit_files[0]  # Use the first .kit file found

                # Get file stats
                stats = kit_file.stat()
                modified = datetime.fromtimestamp(stats.st_mtime).isoformat()
                created = datetime.fromtimestamp(stats.st_ctime).isoformat()

                # Determine project type from directory name or kit file content
                # Convention: if name contains 'test', it's a test project
                is_test = 'test' in item.name.lower()

                # Try to determine type from template
                project_type = 'application'  # default
                if 'extension' in item.name.lower():
                    project_type = 'extension'
                elif 'service' in item.name.lower():
                    project_type = 'microservice'

                project = {
                    'id': item.name,
                    'name': item.name,
                    'displayName': item.name.replace('_', ' ').title(),
                    'type': project_type,
                    'path': str(item),
                    'kitFile': str(kit_file),
                    'lastModified': modified,
                    'createdAt': created,
                    'isTest': is_test
                }

                projects.append(project)

            # Sort by last modified (newest first)
            projects.sort(key=lambda p: p['lastModified'], reverse=True)

            logger.info(f"Found {len(projects)} user project(s)")

            return jsonify({
                'success': True,
                'projects': projects,
                'count': len(projects)
            })

        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'projects': [],
                'count': 0
            }), 500

    @project_bp.route('/clean', methods=['POST'])
    def clean_projects():
        """Clean all user-created projects.

        Deletes all user-created applications and extensions from source/apps,
        excluding system directories (exts, extscache).

        Query params:
            - include_test: bool (default False) - Whether to include test projects

        Returns:
            JSON response with cleanup results
        """
        try:
            include_test = request.args.get('include_test', 'false').lower() == 'true'

            # Get the repo root
            repo_root = get_repo_root()
            apps_dir = repo_root / 'source' / 'apps'
            extensions_dir = repo_root / 'source' / 'extensions'

            deleted_projects = []
            deleted_extensions = []
            errors = []

            # Clean apps directory
            if apps_dir.exists():
                for item in apps_dir.iterdir():
                    # Skip system directories and hidden files
                    if item.name in ['exts', 'extscache', '.', '..'] or item.name.startswith('.'):
                        continue

                    # Only process directories
                    if not item.is_dir():
                        continue

                    # Skip test projects unless include_test is True
                    if not include_test and 'test' in item.name.lower():
                        logger.info(f"Skipping test project: {item.name}")
                        continue

                    try:
                        logger.info(f"Deleting project: {item.name}")
                        shutil.rmtree(item)
                        deleted_projects.append(item.name)
                    except Exception as e:
                        logger.error(f"Failed to delete {item.name}: {e}")
                        errors.append({
                            'project': item.name,
                            'error': str(e)
                        })

            # Clean template-generated extensions
            if extensions_dir.exists():
                # Extension patterns: match both old (*_setup) and new (*.setup) naming conventions
                extension_patterns = [
                    '*viewer_messaging',
                    '*.viewer_messaging',
                    '*viewer_setup',
                    '*.viewer_setup',
                    '*_viewer_setup',
                    '*editor_setup',
                    '*.editor_setup',
                    '*_editor_setup',
                    '*composer_setup',
                    '*.composer_setup',
                    '*_composer_setup',
                    '*usd_composer_setup',
                    '*.usd_composer_setup',
                    '*explorer_setup',
                    '*.explorer_setup',
                    '*_explorer_setup'
                ]

                for pattern in extension_patterns:
                    for ext_dir in extensions_dir.glob(pattern):
                        if not ext_dir.is_dir():
                            continue

                        try:
                            logger.info(f"Deleting extension: {ext_dir.name}")
                            shutil.rmtree(ext_dir)
                            deleted_extensions.append(ext_dir.name)
                        except Exception as e:
                            logger.error(f"Failed to delete {ext_dir.name}: {e}")
                            errors.append({
                                'extension': ext_dir.name,
                                'error': str(e)
                            })

            # Clean repo.toml apps list
            repo_toml = repo_root / 'repo.toml'
            if repo_toml.exists():
                try:
                    import re
                    content = repo_toml.read_text()
                    # Replace apps = [...] with apps = []
                    new_content = re.sub(r'^apps\s*=\s*\[.*\]', 'apps = []', content, flags=re.MULTILINE)
                    repo_toml.write_text(new_content)
                    logger.info("Cleared repo.toml apps list")
                except Exception as e:
                    logger.error(f"Failed to clean repo.toml: {e}")
                    errors.append({
                        'file': 'repo.toml',
                        'error': str(e)
                    })

            response = {
                'success': True,
                'deleted': {
                    'projects': deleted_projects,
                    'extensions': deleted_extensions,
                },
                'counts': {
                    'projects': len(deleted_projects),
                    'extensions': len(deleted_extensions),
                    'total': len(deleted_projects) + len(deleted_extensions)
                },
                'errors': errors
            }

            if errors:
                response['warning'] = f"{len(errors)} item(s) failed to delete"

            logger.info(f"Clean complete: {len(deleted_projects)} projects, {len(deleted_extensions)} extensions")

            return jsonify(response)

        except Exception as e:
            logger.error(f"Failed to clean projects: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'deleted': {'projects': [], 'extensions': []},
                'counts': {'projects': 0, 'extensions': 0, 'total': 0}
            }), 500

    return project_bp
