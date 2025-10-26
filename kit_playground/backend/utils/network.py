#!/usr/bin/env python3
"""
Network utility functions for Kit Playground.

Provides helpers for getting appropriate hostnames and IP addresses
for different use cases (internal vs external communication).
"""

import os
import socket
import subprocess
from typing import Optional


def get_external_ip() -> str:
    """
    Get the external IP address for this machine.
    
    This IP should be used when returning URLs to clients
    that need to connect from remote machines.
    
    Returns:
        str: The external IP address, or "localhost" if detection fails
    """
    # Try multiple methods to get the external IP
    
    # Method 1: Use ip route command (most reliable on Linux)
    try:
        result = subprocess.run(
            ['ip', 'route', 'get', '1.1.1.1'],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            # Parse output like: "1.1.1.1 via ... src 10.176.222.115 ..."
            for part in result.stdout.split():
                if part.startswith('src'):
                    continue
                # The IP comes after 'src'
                parts = result.stdout.split('src')
                if len(parts) > 1:
                    ip = parts[1].strip().split()[0]
                    if ip and not ip.startswith('127.'):
                        return ip
    except (subprocess.SubprocessError, FileNotFoundError, IndexError):
        pass
    
    # Method 2: Use hostname -I command
    try:
        result = subprocess.run(
            ['hostname', '-I'],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            ips = result.stdout.strip().split()
            for ip in ips:
                if not ip.startswith('127.') and not ip.startswith('fe80:'):
                    return ip
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Method 3: Use socket to connect to external address
    try:
        # Create a socket and connect to an external address
        # (doesn't actually send data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.connect(('1.1.1.1', 80))
        ip = sock.getsockname()[0]
        sock.close()
        if ip and not ip.startswith('127.'):
            return ip
    except Exception:
        pass
    
    # Fallback: return localhost
    return 'localhost'


def get_hostname_for_client() -> str:
    """
    Get the appropriate hostname to return to clients in API responses.
    
    - In REMOTE=1 mode: Returns the external IP address
    - In REMOTE=0 mode: Returns "localhost"
    
    This should be used for URLs that are sent to clients (browsers, etc.)
    
    Returns:
        str: The hostname that clients should use to connect
    """
    if os.environ.get('REMOTE') == '1':
        return get_external_ip()
    return 'localhost'


def get_hostname_for_internal() -> str:
    """
    Get the appropriate hostname for internal service-to-service communication.
    
    This should ALWAYS return "localhost" or "127.0.0.1" since it's for
    health checks and internal HTTP requests on the same machine.
    
    Returns:
        str: Always returns "localhost"
    """
    return 'localhost'


def get_bind_address() -> str:
    """
    Get the appropriate bind address for servers.
    
    - In REMOTE=1 mode: Returns "0.0.0.0" (bind to all interfaces)
    - In REMOTE=0 mode: Returns "localhost" (bind only to loopback)
    
    Note: This address should NEVER be sent to clients. Use get_hostname_for_client() instead.
    
    Returns:
        str: The bind address for server sockets
    """
    if os.environ.get('REMOTE') == '1':
        return '0.0.0.0'
    return 'localhost'


def format_url(hostname: Optional[str] = None, port: int = 80, path: str = '', 
               protocol: str = 'http') -> str:
    """
    Format a complete URL using the appropriate hostname.
    
    Args:
        hostname: The hostname to use (if None, uses get_hostname_for_client())
        port: The port number
        path: The URL path (should start with / if provided)
        protocol: The protocol (http or https)
    
    Returns:
        str: The formatted URL
    """
    if hostname is None:
        hostname = get_hostname_for_client()
    
    # Don't include default ports in the URL
    if (protocol == 'http' and port == 80) or (protocol == 'https' and port == 443):
        return f"{protocol}://{hostname}{path}"
    
    return f"{protocol}://{hostname}:{port}{path}"

