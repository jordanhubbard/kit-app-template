#!/usr/bin/env python3
"""
Kit Playground - Visual Development Environment for Omniverse Kit SDK
Main entry point for the cross-platform application.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kit_playground.core.playground_app import PlaygroundApp
from kit_playground.core.config import PlaygroundConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Kit Playground - Visual Development Environment for Omniverse Kit SDK"
    )

    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode with hot reload'
    )

    parser.add_argument(
        '--ui',
        choices=['web', 'native', 'headless'],
        default='web',
        help='UI mode to use (default: web)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port for web server (default: 8080)'
    )

    parser.add_argument(
        '--host',
        default='localhost',
        help='Host for web server (default: localhost)'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--project',
        type=str,
        help='Open an existing project'
    )

    parser.add_argument(
        '--template',
        type=str,
        help='Start with a specific template'
    )

    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically (web mode)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def setup_environment():
    """Set up the environment for Kit Playground."""
    # Ensure required directories exist
    playground_dir = Path.home() / '.kit_playground'
    playground_dir.mkdir(exist_ok=True)

    (playground_dir / 'projects').mkdir(exist_ok=True)
    (playground_dir / 'cache').mkdir(exist_ok=True)
    (playground_dir / 'logs').mkdir(exist_ok=True)

    # Set environment variables
    os.environ['KIT_PLAYGROUND_HOME'] = str(playground_dir)

    return playground_dir


async def main():
    """Main entry point."""
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Setup environment
    playground_home = setup_environment()
    logger.info(f"Kit Playground home: {playground_home}")

    # Load configuration
    config = PlaygroundConfig()
    if args.config:
        config.load_from_file(args.config)
    else:
        config.load_defaults()

    # Override with command line arguments
    if args.dev:
        config.set('development_mode', True)
        config.set('hot_reload', True)

    config.set('server.port', args.port)
    config.set('server.host', args.host)
    config.set('ui.mode', args.ui)

    # Create and start the application
    app = PlaygroundApp(config)

    # Load initial project or template if specified
    if args.project:
        await app.load_project(args.project)
    elif args.template:
        await app.new_project_from_template(args.template)

    # Start the application based on UI mode
    if args.ui == 'web':
        await app.start_web_mode(open_browser=not args.no_browser)
    elif args.ui == 'native':
        await app.start_native_mode()
    elif args.ui == 'headless':
        await app.start_headless_mode()
    else:
        logger.error(f"Unknown UI mode: {args.ui}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("Error: Kit Playground requires Python 3.8 or higher")
            sys.exit(1)

        # Run the application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down Kit Playground...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)