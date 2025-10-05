#!/usr/bin/env python3
"""
Utility to find available network ports.
Used by dev.sh and playground.sh to dynamically allocate ports.
"""

import socket
import sys
from contextlib import closing

def find_free_port(start_port=3000, max_attempts=100):
    """
    Find an available port starting from start_port.

    Args:
        start_port: Port number to start searching from
        max_attempts: Maximum number of ports to try

    Returns:
        int: Available port number

    Raises:
        RuntimeError: If no free port found within max_attempts
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                return port
        except OSError:
            continue

    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")


def find_free_ports(count=2, start_port=3000):
    """
    Find multiple available ports.

    Args:
        count: Number of free ports to find
        start_port: Port number to start searching from

    Returns:
        list: List of available port numbers
    """
    ports = []
    current_port = start_port

    for _ in range(count):
        port = find_free_port(current_port)
        ports.append(port)
        current_port = port + 1

    return ports


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Find specific number of ports
        count = int(sys.argv[1])
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
        ports = find_free_ports(count, start)
        print(' '.join(map(str, ports)))
    else:
        # Find single port
        port = find_free_port()
        print(port)
