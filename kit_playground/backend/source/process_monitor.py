"""
Process Monitor for Kit Applications

Monitors running Kit application processes and automatically manages Xpra displays.
When all processes using a specific Xpra display terminate, the display is automatically shut down.
"""

import logging
import os
import subprocess
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional

from flask_socketio import SocketIO

logger = logging.getLogger(__name__)


@dataclass
class ProcessInfo:
    """Information about a monitored process."""
    pid: int
    project_name: str
    xpra_display: Optional[int] = None
    streaming_port: Optional[int] = None
    is_streaming: bool = False
    start_time: float = 0.0


class ProcessMonitor:
    """
    Singleton process monitor for tracking Kit application processes.
    
    Automatically shuts down Xpra displays when no processes are using them.
    """
    _instance: Optional['ProcessMonitor'] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._processes: Dict[str, ProcessInfo] = {}
        self._xpra_displays: Dict[int, int] = defaultdict(int)  # display -> count
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._socketio: Optional[SocketIO] = None
        self._initialized = True
        
        logger.info("ProcessMonitor initialized")

    @classmethod
    def get_instance(cls) -> 'ProcessMonitor':
        """Get the singleton instance."""
        return cls()

    def register_socketio(self, socketio: SocketIO):
        """Register SocketIO instance for event emission."""
        self._socketio = socketio

    def _emit_log(self, level: str, message: str):
        """Emit log message via SocketIO if available."""
        if self._socketio:
            try:
                self._socketio.emit('log', {
                    'level': level,
                    'source': 'monitor',
                    'message': message
                })
            except Exception as e:
                logger.error(f"Failed to emit log via SocketIO: {e}")
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, message)

    def register_process(
        self,
        project_name: str,
        pid: int,
        xpra_display: Optional[int] = None,
        streaming_port: Optional[int] = None,
        is_streaming: bool = False
    ):
        """
        Register a new process for monitoring.

        Args:
            project_name: Name of the project/app
            pid: Process ID
            xpra_display: Xpra display number if using Xpra
            streaming_port: Streaming port if using WebRTC streaming
            is_streaming: Whether this is a streaming app
        """
        with self._lock:
            proc_info = ProcessInfo(
                pid=pid,
                project_name=project_name,
                xpra_display=xpra_display,
                streaming_port=streaming_port,
                is_streaming=is_streaming,
                start_time=time.time()
            )
            
            self._processes[project_name] = proc_info
            
            if xpra_display is not None:
                self._xpra_displays[xpra_display] += 1
                self._emit_log('info', 
                    f"Registered Xpra display :{xpra_display} for {project_name}. "
                    f"Count: {self._xpra_displays[xpra_display]}")
            
            self._emit_log('info',
                f"Registered process {project_name} (PID: {pid}, Streaming: {is_streaming})")

        # Start monitor thread if not running
        if not self._monitor_thread or not self._monitor_thread.is_alive():
            self.start_monitor()

    def unregister_process(self, project_name: str):
        """
        Unregister a process when it stops.

        Args:
            project_name: Name of the project to unregister
        """
        with self._lock:
            if project_name not in self._processes:
                return
            
            proc_info = self._processes.pop(project_name)
            
            if proc_info.xpra_display is not None:
                display = proc_info.xpra_display
                self._xpra_displays[display] -= 1
                
                self._emit_log('info',
                    f"Unregistered Xpra display :{display} for {project_name}. "
                    f"Count: {self._xpra_displays[display]}")
                
                if self._xpra_displays[display] <= 0:
                    # No more processes using this display
                    self._xpra_displays.pop(display, None)
                    self._emit_log('info',
                        f"Xpra display :{display} count is zero. Shutting down...")
                    self._stop_xpra_display(display)
            
            self._emit_log('info', f"Unregistered process {project_name}")

    def _stop_xpra_display(self, display: int):
        """
        Stop a specific Xpra display.

        Args:
            display: Display number to stop
        """
        self._emit_log('info', f"Attempting to stop Xpra display :{display}...")
        
        try:
            result = subprocess.run(
                ['xpra', 'stop', f':{display}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully shut down Xpra display :{display}")
                if self._socketio:
                    self._socketio.emit('xpra_shutdown', {'display': display})
            else:
                logger.warning(
                    f"Xpra stop command for :{display} failed: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout stopping Xpra display :{display}")
        except Exception as e:
            logger.error(f"Error stopping Xpra display :{display}: {e}")

    def _monitor_loop(self):
        """Background monitoring loop."""
        self._emit_log('info', "Process monitor started")
        
        while not self._stop_event.is_set():
            time.sleep(2)  # Check every 2 seconds
            
            with self._lock:
                # Create a copy to iterate over
                processes_to_check = list(self._processes.items())
            
            for project_name, proc_info in processes_to_check:
                try:
                    # Check if process still exists (signal 0)
                    os.kill(proc_info.pid, 0)
                except OSError:
                    # Process has exited
                    self._emit_log('info',
                        f"Detected {project_name} (PID: {proc_info.pid}) has exited")
                    self.unregister_process(project_name)
                except Exception as e:
                    logger.error(
                        f"Error checking process {project_name} (PID: {proc_info.pid}): {e}")
                    self.unregister_process(project_name)
        
        self._emit_log('info', "Process monitor stopped")

    def start_monitor(self):
        """Start the background monitoring thread."""
        if not self._monitor_thread or not self._monitor_thread.is_alive():
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self._monitor_thread.start()
            logger.info("Process monitor thread started")

    def stop_monitor(self):
        """Stop the background monitoring thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_event.set()
            self._monitor_thread.join(timeout=5)
            if self._monitor_thread.is_alive():
                logger.warning("Process monitor thread did not stop gracefully")
            self._monitor_thread = None
            logger.info("Process monitor thread stopped")

    def get_status(self) -> Dict:
        """
        Get current monitoring status.

        Returns:
            Dictionary with monitored processes and Xpra displays
        """
        with self._lock:
            return {
                'monitored_processes': {
                    name: {
                        'pid': p.pid,
                        'xpra_display': p.xpra_display,
                        'is_streaming': p.is_streaming
                    }
                    for name, p in self._processes.items()
                },
                'xpra_displays_in_use': dict(self._xpra_displays)
            }


def get_process_monitor() -> ProcessMonitor:
    """Get the singleton ProcessMonitor instance."""
    return ProcessMonitor.get_instance()

