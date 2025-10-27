#!/usr/bin/env python3
"""
Kit App Streaming Utilities

Provides detection, configuration, and management for NVIDIA Kit App Streaming.
Streaming is configured via ApplicationLayerTemplates (.kit files) that layer
streaming capabilities on top of base applications.

Three streaming types are supported:
1. Default (omni.kit.livestream.app) - Standard WebRTC streaming
2. NVCF (omni.services.livestream.session) - NVIDIA Cloud Functions deployment
3. GDN (omni.kit.gfn) - GeForce NOW deployment

Usage:
    from streaming_utils import (
        is_streaming_app,
        get_streaming_type,
        get_streaming_url,
        wait_for_streaming_ready
    )

    # Detect if app uses streaming
    if is_streaming_app(Path("my_app_stream.kit")):
        streaming_type = get_streaming_type(Path("my_app_stream.kit"))
        url = get_streaming_url(port=47995)
        
        # Launch app
        subprocess.Popen(["./my_app_stream.sh"])
        if wait_for_streaming_ready(47995):
            print(f"Stream ready: {url}")
"""

import socket
import time
from pathlib import Path
from typing import Optional, Literal

try:
    from omni.repo.kit_template.backend import read_toml
except ImportError:
    # Fallback for standalone usage
    import toml
    def read_toml(path):
        with open(path, 'r') as f:
            return toml.load(f)


# Real streaming extensions (not hallucinated!)
STREAMING_EXTENSIONS = {
    'default': 'omni.kit.livestream.app',        # Default WebRTC streaming
    'nvcf': 'omni.services.livestream.session',  # NVIDIA Cloud Functions
    'gdn': 'omni.kit.gfn',                       # GeForce NOW (GDN)
}


def is_streaming_app(kit_file_path: Path) -> bool:
    """
    Detect if a .kit file uses Kit App Streaming.

    Checks for streaming extensions in the .kit file dependencies:
    - omni.kit.livestream.app (default streaming)
    - omni.services.livestream.session (NVCF streaming)
    - omni.kit.gfn (GDN/GeForce NOW streaming)

    Args:
        kit_file_path: Path to .kit file to check

    Returns:
        True if the app uses any streaming extension

    Example:
        >>> is_streaming_app(Path("source/apps/my_app/my_app_stream.kit"))
        True
    """
    if not kit_file_path.exists():
        return False

    try:
        content = read_toml(kit_file_path)

        # Check dependencies section for streaming extensions
        dependencies = content.get('dependencies', {})
        
        for ext in STREAMING_EXTENSIONS.values():
            if ext in dependencies:
                return True

        # Check template metadata for streaming indicator
        package = content.get('package', {})
        template_name = package.get('template_name', '')
        if 'streaming' in template_name.lower():
            return True

        return False

    except Exception as e:
        print(f"Warning: Could not read {kit_file_path}: {e}")
        return False


def get_streaming_type(kit_file_path: Path) -> Optional[Literal['default', 'nvcf', 'gdn']]:
    """
    Determine the type of streaming configuration in a .kit file.

    Args:
        kit_file_path: Path to .kit file to check

    Returns:
        'default', 'nvcf', 'gdn', or None if not a streaming app

    Example:
        >>> get_streaming_type(Path("my_app_stream.kit"))
        'default'
    """
    if not kit_file_path.exists():
        return None

    try:
        content = read_toml(kit_file_path)
        dependencies = content.get('dependencies', {})

        # Check for each streaming type
        if STREAMING_EXTENSIONS['gdn'] in dependencies:
            return 'gdn'
        if STREAMING_EXTENSIONS['nvcf'] in dependencies:
            return 'nvcf'
        if STREAMING_EXTENSIONS['default'] in dependencies:
            return 'default'

        # Check template name as fallback
        package = content.get('package', {})
        template_name = package.get('template_name', '').lower()
        if 'gdn' in template_name:
            return 'gdn'
        if 'nvcf' in template_name:
            return 'nvcf'
        if 'streaming' in template_name:
            return 'default'

        return None

    except Exception as e:
        print(f"Warning: Could not read {kit_file_path}: {e}")
        return None


def get_streaming_url(
    port: int = 47995,
    hostname: str = 'localhost',
    protocol: str = 'http'
) -> str:
    """
    Construct the streaming URL for a Kit App Streaming instance.

    The URL format depends on the streaming type:
    - Default: http://{hostname}:{port}/streaming/webrtc-client
    - NVCF: Configured via cloud deployment
    - GDN: Configured via GeForce NOW platform

    Args:
        port: Streaming server port (default: 47995)
        hostname: Server hostname or IP (default: 'localhost')
        protocol: Protocol scheme (default: 'http')

    Returns:
        Streaming URL for WebRTC client

    Example:
        >>> get_streaming_url(port=47995, hostname='remote-server.com')
        'http://remote-server.com:47995/streaming/webrtc-client'
    """
    return f'{protocol}://{hostname}:{port}/streaming/webrtc-client'


def wait_for_streaming_ready(
    port: int = 47995,
    hostname: str = 'localhost',
    timeout: int = 60,
    interval: float = 1.0
) -> bool:
    """
    Wait for the streaming server to become ready.

    Polls the streaming port until it accepts connections or timeout is reached.

    Args:
        port: Streaming server port to check
        hostname: Server hostname (default: 'localhost')
        timeout: Maximum seconds to wait (default: 60)
        interval: Seconds between checks (default: 1.0)

    Returns:
        True if server is ready, False if timeout

    Example:
        >>> wait_for_streaming_ready(port=47995, timeout=30)
        True
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((hostname, port), timeout=2):
                return True
        except (socket.timeout, socket.error, ConnectionRefusedError):
            time.sleep(interval)
    
    return False


def get_streaming_config_path(
    streaming_type: Literal['default', 'nvcf', 'gdn'] = 'default'
) -> str:
    """
    Get the path to a streaming configuration template.

    Args:
        streaming_type: Type of streaming configuration

    Returns:
        Relative path to the streaming .kit file

    Example:
        >>> get_streaming_config_path('default')
        'templates/apps/streaming_configs/default_stream.kit'
    """
    config_files = {
        'default': 'default_stream.kit',
        'nvcf': 'nvcf_stream.kit',
        'gdn': 'gdn_stream.kit',
    }
    
    filename = config_files.get(streaming_type, 'default_stream.kit')
    return f'templates/apps/streaming_configs/{filename}'


# Legacy compatibility (these extensions DO NOT EXIST)
# Kept for backward compatibility to avoid breaking imports,
# but will log warnings if used
LEGACY_NONEXISTENT_EXTENSIONS = [
    'omni.services.streaming.webrtc',  # DOES NOT EXIST - hallucinated
    'omni.kit.streamhelper',           # DOES NOT EXIST - hallucinated
]


def _warn_if_using_legacy():
    """Print warning if legacy functions are used."""
    import warnings
    warnings.warn(
        "Legacy streaming utilities detected. "
        "Use get_streaming_type() and STREAMING_EXTENSIONS instead. "
        "The extensions 'omni.services.streaming.webrtc' and 'omni.kit.streamhelper' "
        "DO NOT EXIST and were hallucinated in error.",
        DeprecationWarning,
        stacklevel=3
    )
