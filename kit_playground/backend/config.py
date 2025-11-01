from __future__ import annotations

from pathlib import Path


# Path to Kit SDK extension cache
CACHE_PATH: Path = Path.home() / ".local/share/ov/data/exts"

# Minimum number of extensions to consider cache "ready"
CACHED_THRESHOLD: int = 50

# Estimated total download size for first-time dependency preparation (~12 GB)
ESTIMATED_SIZE_BYTES: int = 12 * 1024 * 1024 * 1024

# Default bandwidth used for time estimate (Mbps)
DEFAULT_BANDWIDTH_MBPS: float = 50.0

# Emit periodic status update every N lines of subprocess output
PREPARE_STATUS_UPDATE_EVERY: int = 10


