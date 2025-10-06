"""
Xpra Session Manager
Manages Xpra virtual displays for running Kit applications
"""

import subprocess
import os
import logging
import time
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class XpraSession:
    """Represents an Xpra virtual display session."""

    def __init__(self, display_number: int, port: int):
        self.display_number = display_number
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.app_process: Optional[subprocess.Popen] = None
        self.started = False

    def start(self) -> bool:
        """Start the Xpra server."""
        if self.started:
            logger.warning(f"Xpra session :{self.display_number} already started")
            return True

        # Check if xpra is installed
        try:
            subprocess.run(['which', 'xpra'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.error("Xpra is not installed. Please install it first.")
            logger.error("See XPRA_SETUP.md for installation instructions")
            return False

        try:
            cmd = [
                'xpra', 'start',
                f':{self.display_number}',
                f'--bind-tcp=0.0.0.0:{self.port}',
                '--html=on',
                '--encodings=rgb,png,jpeg',
                '--compression=0',
                '--opengl=yes',
                '--speaker=off',
                '--microphone=off',
                '--daemon=no',  # Run in foreground so we can manage it
            ]

            logger.info(f"Starting Xpra session :{self.display_number} on port {self.port}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a bit for Xpra to start
            time.sleep(2)

            # Check if process is still running
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                logger.error(f"Xpra failed to start: {stderr}")
                return False

            self.started = True
            logger.info(f"Xpra session :{self.display_number} started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start Xpra session: {e}")
            return False

    def launch_app(self, app_command: str) -> bool:
        """Launch an application on this Xpra display.

        Args:
            app_command: Path to executable script (must be validated by caller)
        """
        if not self.started:
            logger.error("Xpra session not started")
            return False

        try:
            env = os.environ.copy()
            env['DISPLAY'] = f':{self.display_number}'

            logger.info(f"Launching app on :{self.display_number}: {app_command}")
            # SECURITY: Use list form instead of shell=True to prevent injection
            # Split on whitespace but preserve the script path as first arg
            import shlex
            cmd_list = shlex.split(app_command) if ' ' in app_command else [app_command]

            self.app_process = subprocess.Popen(
                cmd_list,
                shell=False,  # More secure than shell=True
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logger.info(f"App launched with PID {self.app_process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to launch app: {e}")
            return False

    def stop(self):
        """Stop the Xpra session and any running apps."""
        # Stop the app first
        if self.app_process and self.app_process.poll() is None:
            logger.info(f"Stopping app process {self.app_process.pid}")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()

        # Stop Xpra
        if self.started:
            logger.info(f"Stopping Xpra session :{self.display_number}")
            try:
                subprocess.run(
                    ['xpra', 'stop', f':{self.display_number}'],
                    check=True,
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Error stopping Xpra: {e}")

            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()

        self.started = False


class XpraManager:
    """Manages multiple Xpra sessions."""

    def __init__(self, base_display: int = 100, base_port: int = 10000):
        self.base_display = base_display
        self.base_port = base_port
        self.sessions: Dict[str, XpraSession] = {}
        self.next_display = base_display

    def create_session(self, session_id: str) -> Optional[XpraSession]:
        """Create a new Xpra session."""
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists")
            return self.sessions[session_id]

        display = self.next_display
        port = self.base_port + (display - self.base_display)
        self.next_display += 1

        session = XpraSession(display, port)
        if session.start():
            self.sessions[session_id] = session
            return session
        else:
            return None

    def get_session(self, session_id: str) -> Optional[XpraSession]:
        """Get an existing session."""
        return self.sessions.get(session_id)

    def stop_session(self, session_id: str):
        """Stop and remove a session."""
        session = self.sessions.get(session_id)
        if session:
            session.stop()
            del self.sessions[session_id]

    def stop_all(self):
        """Stop all sessions."""
        for session_id in list(self.sessions.keys()):
            self.stop_session(session_id)

    def get_session_url(self, session_id: str, host: str = None) -> Optional[str]:
        """Get the HTML5 client URL for a session.

        Args:
            session_id: ID of the session
            host: Optional host to use instead of localhost (for remote access)
        """
        session = self.sessions.get(session_id)
        if session and session.started:
            # Use provided host or default to localhost
            server_host = host if host else "localhost"
            return f"http://{server_host}:{session.port}"
        return None
