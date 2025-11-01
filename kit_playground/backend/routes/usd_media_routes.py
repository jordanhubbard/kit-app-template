"""
USD Media Library Routes

Provides API endpoints for managing and downloading USD sample files.
Users can browse well-known USD samples, add their own URLs, and download
assets to a well-known location accessible by Kit applications.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# Create blueprint
usd_media_bp = Blueprint('usd_media', __name__, url_prefix='/api/usd-media')

# Well-known USD assets directory (accessible by Kit apps)
USD_ASSETS_DIR = Path.home() / "OmniverseAssets" / "USD"
USD_LIBRARY_FILE = Path(__file__).parent.parent / "data" / "usd_library.json"

# Default well-known USD samples
BUILTIN_DIR = Path(__file__).parent.parent / "static" / "usd"

DEFAULT_USD_SAMPLES = [
    {
        "id": "nvidia_stage",
        "name": "NVIDIA Stage",
        "description": "Basic NVIDIA demo stage with lighting",
        "url": "builtin:nvidia_stage.usda",
        "category": "scenes",
        "size_mb": 0.5,
        "tags": ["demo", "stage", "lighting"]
    },
    {
        "id": "mars_rover",
        "name": "Mars Rover",
        "description": "NASA Mars Perseverance Rover model",
        "url": "builtin:mars_rover.usda",
        "category": "vehicles",
        "size_mb": 45.0,
        "tags": ["nasa", "rover", "vehicle"]
    },
    {
        "id": "warehouse",
        "name": "Warehouse",
        "description": "Industrial warehouse environment",
        "url": "builtin:warehouse.usda",
        "category": "scenes",
        "size_mb": 120.0,
        "tags": ["warehouse", "industrial", "environment"]
    },
    {
        "id": "simple_room",
        "name": "Simple Room",
        "description": "Basic architectural interior",
        "url": "builtin:simple_room.usda",
        "category": "interiors",
        "size_mb": 85.0,
        "tags": ["interior", "room", "architecture"]
    },
    {
        "id": "kitchen",
        "name": "Modern Kitchen",
        "description": "Contemporary kitchen design",
        "url": "builtin:kitchen.usda",
        "category": "interiors",
        "size_mb": 250.0,
        "tags": ["kitchen", "interior", "modern"]
    }
]


def ensure_usd_assets_dir():
    """Ensure the USD assets directory exists."""
    USD_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"USD assets directory: {USD_ASSETS_DIR}")
    return USD_ASSETS_DIR


def ensure_data_dir():
    """Ensure the data directory exists for JSON storage."""
    data_dir = USD_LIBRARY_FILE.parent
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def load_usd_library() -> List[Dict[str, Any]]:
    """Load USD library from JSON file, or initialize with defaults."""
    try:
        if USD_LIBRARY_FILE.exists():
            with open(USD_LIBRARY_FILE, 'r') as f:
                return json.load(f)
        else:
            # Initialize with defaults
            ensure_data_dir()
            save_usd_library(DEFAULT_USD_SAMPLES)
            return DEFAULT_USD_SAMPLES
    except Exception as e:
        logger.error(f"Error loading USD library: {e}")
        return DEFAULT_USD_SAMPLES


def save_usd_library(library: List[Dict[str, Any]]):
    """Save USD library to JSON file."""
    try:
        ensure_data_dir()
        with open(USD_LIBRARY_FILE, 'w') as f:
            json.dump(library, f, indent=2)
        logger.info(f"USD library saved to {USD_LIBRARY_FILE}")
    except Exception as e:
        logger.error(f"Error saving USD library: {e}")


def create_usd_media_routes():
    """Create and configure USD media routes."""

    @usd_media_bp.route('/library', methods=['GET'])
    def get_library():
        """Get the complete USD library with download status."""
        try:
            library = load_usd_library()
            assets_dir = ensure_usd_assets_dir()

            # Check which files have been downloaded
            for item in library:
                filename = secure_filename(item['name'] + '.usd')
                local_path = assets_dir / filename
                item['downloaded'] = local_path.exists()
                if item['downloaded']:
                    item['local_path'] = str(local_path)

            return jsonify({
                'success': True,
                'library': library,
                'assets_dir': str(assets_dir)
            })
        except Exception as e:
            logger.error(f"Error getting USD library: {e}")
            return jsonify({'error': str(e)}), 500

    @usd_media_bp.route('/add', methods=['POST'])
    def add_asset():
        """Add a new USD asset to the library."""
        try:
            data = request.json
            required_fields = ['id', 'name', 'url']

            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400

            library = load_usd_library()

            # Check if ID already exists
            if any(item['id'] == data['id'] for item in library):
                return jsonify({'error': 'Asset ID already exists'}), 400

            # Add new asset
            new_asset = {
                'id': data['id'],
                'name': data['name'],
                'description': data.get('description', ''),
                'url': data['url'],
                'category': data.get('category', 'custom'),
                'size_mb': data.get('size_mb', 0),
                'tags': data.get('tags', ['custom']),
                'custom': True
            }

            library.append(new_asset)
            save_usd_library(library)

            return jsonify({
                'success': True,
                'asset': new_asset
            })
        except Exception as e:
            logger.error(f"Error adding USD asset: {e}")
            return jsonify({'error': str(e)}), 500

    @usd_media_bp.route('/remove/<asset_id>', methods=['DELETE'])
    def remove_asset(asset_id: str):
        """Remove a custom USD asset from the library."""
        try:
            library = load_usd_library()

            # Find and remove the asset (only allow removal of custom assets)
            asset = next((item for item in library if item['id'] == asset_id), None)
            if not asset:
                return jsonify({'error': 'Asset not found'}), 404

            if not asset.get('custom', False):
                return jsonify({'error': 'Cannot remove built-in assets'}), 400

            library = [item for item in library if item['id'] != asset_id]
            save_usd_library(library)

            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error removing USD asset: {e}")
            return jsonify({'error': str(e)}), 500

    @usd_media_bp.route('/download/<asset_id>', methods=['POST'])
    def download_asset(asset_id: str):
        """Download a USD asset to the local assets directory."""
        try:
            library = load_usd_library()
            asset = next((item for item in library if item['id'] == asset_id), None)

            if not asset:
                return jsonify({'error': 'Asset not found'}), 404

            assets_dir = ensure_usd_assets_dir()
            filename = secure_filename(asset['name'] + '.usd')
            local_path = assets_dir / filename

            url = asset['url']
            if url.startswith('builtin:'):
                # Copy embedded sample
                src = BUILTIN_DIR / url.split(':', 1)[1]
                if not src.exists():
                    return jsonify({'error': f'Built-in asset not found: {src.name}'}), 404
                logger.info(f"Copying built-in USD sample {src} -> {local_path}")
                data = src.read_bytes()
                with open(local_path, 'wb') as f:
                    f.write(data)
            else:
                # Download the file
                logger.info(f"Downloading {asset['name']} from {url}")
                response = requests.get(url, stream=True, timeout=60)
                response.raise_for_status()

                # Save to file
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            logger.info(f"Downloaded to {local_path}")

            return jsonify({
                'success': True,
                'local_path': str(local_path),
                'size_bytes': local_path.stat().st_size
            })
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading asset: {e}")
            return jsonify({'error': f'Download failed: {str(e)}'}), 500
        except Exception as e:
            logger.error(f"Error downloading asset: {e}")
            return jsonify({'error': str(e)}), 500

    @usd_media_bp.route('/delete/<asset_id>', methods=['DELETE'])
    def delete_local_file(asset_id: str):
        """Delete a downloaded USD file from local storage."""
        try:
            library = load_usd_library()
            asset = next((item for item in library if item['id'] == asset_id), None)

            if not asset:
                return jsonify({'error': 'Asset not found'}), 404

            assets_dir = ensure_usd_assets_dir()
            filename = secure_filename(asset['name'] + '.usd')
            local_path = assets_dir / filename

            if local_path.exists():
                local_path.unlink()
                logger.info(f"Deleted local file: {local_path}")

            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error deleting local file: {e}")
            return jsonify({'error': str(e)}), 500

    @usd_media_bp.route('/assets-dir', methods=['GET'])
    def get_assets_dir():
        """Get the path to the USD assets directory."""
        assets_dir = ensure_usd_assets_dir()
        return jsonify({
            'success': True,
            'path': str(assets_dir),
            'exists': assets_dir.exists()
        })

    return usd_media_bp

