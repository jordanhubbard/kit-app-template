#!/usr/bin/env python3
"""
Configuration management for Kit Playground
"""

import json
from pathlib import Path
from typing import Any, Optional


class PlaygroundConfig:
    """Configuration manager for Kit Playground."""

    def __init__(self):
        self.config = {
            'development_mode': False,
            'hot_reload': False,
            'server': {
                'host': 'localhost',
                'port': 8200,
            },
            'ui': {
                'mode': 'web',  # web, native, headless
                'theme': 'dark',
            },
            'build': {
                'parallel': True,
                'cache_enabled': True,
            },
        }
        self.config_file = Path.home() / '.kit_playground' / 'config.json'

    def load_defaults(self):
        """Load default configuration."""
        pass  # Already set in __init__

    def load_from_file(self, path: str):
        """Load configuration from file."""
        config_path = Path(path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                loaded = json.load(f)
                self._merge_config(loaded)

    def _merge_config(self, new_config: dict):
        """Merge new configuration into existing."""
        def deep_merge(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value

        deep_merge(self.config, new_config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)