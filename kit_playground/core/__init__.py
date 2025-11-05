"""
Kit Playground Core - Central application logic and configuration.
"""

from kit_playground.core.playground_app import PlaygroundApp
from kit_playground.core.config import PlaygroundConfig

# Export PlaygroundConfig as Config for convenience
Config = PlaygroundConfig

__all__ = [
    "PlaygroundApp",
    "Config",
    "PlaygroundConfig",
]

