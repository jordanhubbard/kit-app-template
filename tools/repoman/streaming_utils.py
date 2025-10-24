#!/usr/bin/env python3
"""
Kit App Streaming Utilities

Provides detection, configuration, and management for NVIDIA Kit App Streaming
via WebRTC. Kit apps can host their own HTTPS/WebRTC signaling server for
remote rendering without requiring local GPU resources.

Usage:
    from streaming_utils import (
        is_streaming_app,
        get_streaming_flags,
        get_streaming_url,
        wait_for_streaming_ready
    )
    
    # Detect if app uses streaming
    if is_streaming_app(Path("my_app.kit")):
        # Get flags to enable streaming
        flags = get_streaming_flags(port=47995)
        
        # Construct URL
        url = get_streaming_url(port=47995)
        
        # Launch and wait
        subprocess.Popen(["./my_app.sh"] + flags)
        if wait_for_streaming_ready(47995):
            print(f"Stream ready: {url}")
"""

import socket
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from omni.repo.kit_template.backend import read_toml
except ImportError:
    # Fallback for standalone usage
    import toml as read_toml


def is_streaming_app(kit_file_path: Path) -> bool:
    """
    Detect if a .kit file uses Kit App Streaming.
    
    Checks for WebRTC streaming extensions in the .kit file dependencies:
    - omni.services.streaming.webrtc (primary)
    - omni.kit.streamhelper (helper utilities)
    - omni.kit.livestream.* (legacy streaming)
    
    Also checks template metadata for streaming indicators.
    
    Args:
        kit_file_path: Path to .kit file to check
        
    Returns:
        True if the app uses streaming extensions
        
    Example:
        >>> is_streaming_app(Path("source/apps/my_app/my_app.kit"))
        True
    """
    if not kit_file_path.exists():
        return False
    
    try:
        content = read_toml(kit_file_path)
        
        # Check dependencies section for streaming extensions
        dependencies = content.get('dependencies', {})
        streaming_deps = [
            'omni.services.streaming.webrtc',  # Primary WebRTC streaming
            'omni.kit.streamhelper',           # Stream helper utilities
            'omni.kit.livestream.app',         # Legacy livestream (app)
            'omni.kit.livestream.core',        # Legacy livestream (core)
            'omni.kit.livestream.native',      # Legacy livestream (native)
        ]
        
        for dep in streaming_deps:
            if dep in dependencies:
                return True
        
        # Check template metadata for streaming indicator
        package = content.get('package', {})
        template_name = package.get('template_name', '')
        if 'streaming' in template_name.lower():
            return True
        
        return False
        
    except Exception as e:
        # If we can't read the file, assume it's not a streaming app
        print(f"Warning: Could not read {kit_file_path}: {e}")
        return False


def get_streaming_url(
    port: int = 47995,
    hostname: str = 'localhost',
    use_https: bool = True
) -> str:
    """
    Construct the streaming URL for a Kit app.
    
    Kit apps host their own HTTPS/WebRTC signaling server on the specified
    port. The URL is deterministic based on hostname and port - no stdout
    parsing needed.
    
    Args:
        port: WebRTC listen port (default: 47995)
        hostname: Hostname or IP address (default: 'localhost')
                 Use '0.0.0.0' for remote access
        use_https: Use HTTPS protocol (default: True)
                   Self-signed certificate warning is normal
        
    Returns:
        Complete streaming URL (e.g., 'https://localhost:47995')
        
    Example:
        >>> get_streaming_url(port=47995)
        'https://localhost:47995'
        
        >>> get_streaming_url(port=48000, hostname='192.168.1.100')
        'https://192.168.1.100:48000'
    """
    protocol = 'https' if use_https else 'http'
    return f'{protocol}://{hostname}:{port}'


def get_streaming_flags(
    port: int = 47995,
    draw_mouse: bool = False,
    cert_path: Optional[Path] = None,
    key_path: Optional[Path] = None,
    allow_root: bool = True
) -> List[str]:
    """
    Generate command-line flags for Kit App Streaming.
    
    Returns the standard flags needed to enable WebRTC streaming:
    - Enable streaming extensions (omni.services.streaming.webrtc, streamhelper)
    - Set headless/no-window mode
    - Configure WebRTC settings (port, rendering)
    - Optional: Custom SSL certificates
    
    These flags should be passed to the Kit executable to enable streaming.
    
    Args:
        port: WebRTC listen port (default: 47995)
        draw_mouse: Show mouse cursor in stream (default: False)
        cert_path: Custom SSL certificate path (optional)
        key_path: Custom SSL private key path (optional)
        allow_root: Allow running as root user (default: True)
        
    Returns:
        List of command-line flags ready to pass to Kit
        
    Example:
        >>> flags = get_streaming_flags(port=47995)
        >>> subprocess.run(["./my_app.sh"] + flags)
        
        >>> flags = get_streaming_flags(
        ...     port=48000,
        ...     draw_mouse=True,
        ...     cert_path=Path("/etc/ssl/cert.pem"),
        ...     key_path=Path("/etc/ssl/key.pem")
        ... )
    """
    flags = [
        '--enable', 'omni.services.streaming.webrtc',
        '--enable', 'omni.kit.streamhelper',
        '--no-window',
        f'--/app/window/drawMouse={str(draw_mouse).lower()}',
        '--/renderer/headless=true',
        '--/rtx/webrtc/enable=true',
        f'--/rtx/webrtc/listenPort={port}',
    ]
    
    if allow_root:
        flags.insert(0, '--allow-root')
    
    if cert_path:
        flags.append(f'--/rtx/webrtc/certificatePath={cert_path}')
    
    if key_path:
        flags.append(f'--/rtx/webrtc/privateKeyPath={key_path}')
    
    return flags


def wait_for_streaming_ready(
    port: int = 47995,
    hostname: str = 'localhost',
    timeout: int = 60
) -> bool:
    """
    Wait for Kit streaming server to be ready.
    
    Polls the streaming port until it responds or timeout occurs.
    Uses a simple TCP connection test to check if the port is open
    and accepting connections.
    
    Args:
        port: WebRTC listen port to check
        hostname: Hostname to check (default: 'localhost')
        timeout: Maximum seconds to wait (default: 60)
        
    Returns:
        True if server is ready and port is open
        False if timeout occurred
        
    Example:
        >>> process = subprocess.Popen(["./my_app.sh"] + flags)
        >>> if wait_for_streaming_ready(47995, timeout=30):
        ...     print("Streaming ready!")
        ... else:
        ...     print("Timeout waiting for streaming server")
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((hostname, port))
            sock.close()
            
            if result == 0:
                # Port is open and accepting connections
                return True
                
        except (socket.error, socket.timeout):
            # Connection failed, keep trying
            pass
        except Exception:
            # Unexpected error, keep trying
            pass
        
        # Wait before next attempt
        time.sleep(0.5)
    
    # Timeout reached
    return False


def get_streaming_info(kit_file_path: Path, port: int = 47995) -> Optional[Dict[str, any]]:
    """
    Get comprehensive streaming information for a Kit app.
    
    Combines detection, URL construction, and configuration into a single
    convenient function.
    
    Args:
        kit_file_path: Path to .kit file
        port: WebRTC port to use
        
    Returns:
        Dictionary with streaming info, or None if not a streaming app:
        {
            'is_streaming': bool,
            'url': str,
            'port': int,
            'flags': List[str],
            'ssl_warning': str
        }
        
    Example:
        >>> info = get_streaming_info(Path("my_app.kit"), port=47995)
        >>> if info:
        ...     print(f"Streaming URL: {info['url']}")
        ...     flags = info['flags']
    """
    if not is_streaming_app(kit_file_path):
        return None
    
    return {
        'is_streaming': True,
        'url': get_streaming_url(port=port),
        'port': port,
        'flags': get_streaming_flags(port=port),
        'ssl_warning': 'Self-signed SSL certificate warning is normal. Accept in browser.'
    }


# Convenience constants
DEFAULT_STREAMING_PORT = 47995
DEFAULT_STREAMING_TIMEOUT = 60

# Known streaming extensions (for reference)
STREAMING_EXTENSIONS = [
    'omni.services.streaming.webrtc',
    'omni.kit.streamhelper',
    'omni.kit.livestream.app',
    'omni.kit.livestream.core',
    'omni.kit.livestream.native',
]

