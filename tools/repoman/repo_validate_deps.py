#!/usr/bin/env python3
"""
Repo tool wrapper for Kit dependency validation.

Integrates validate_kit_deps into the repo tool system.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from validate_kit_deps import (
    validate_kit_file,
    validate_all_kit_files,
    prefetch_extensions
)

logger = logging.getLogger(__name__)


def main(config: dict):
    """
    Main entry point for repo tool integration.

    Args:
        config: Configuration dict from repo tool system
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Validate Kit dependencies',
        prog='repo validate_deps'
    )
    parser.add_argument(
        '--kit-file',
        type=Path,
        help='Specific .kit file to validate'
    )
    parser.add_argument(
        '--no-registry',
        action='store_true',
        help='Skip online registry checks'
    )
    parser.add_argument(
        '--prefetch',
        action='store_true',
        help='Pre-fetch all extensions'
    )
    parser.add_argument(
        '--config',
        '-c',
        default='release',
        choices=['release', 'debug'],
        help='Build configuration'
    )
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop on first error'
    )

    args, _ = parser.parse_known_args()

    # Get repo root from config
    repo_root = Path(config.get('root', Path.cwd()))

    print(f"\n{'='*70}")
    print("Kit Dependency Validation")
    print(f"{'='*70}")

    # Prefetch mode
    if args.prefetch:
        print("\nMode: Pre-fetch extensions")
        if args.kit_file:
            success = prefetch_extensions(args.kit_file, repo_root, args.config)
        else:
            # Use dummy path - prefetch_extensions will run pull_extensions
            success = prefetch_extensions(
                repo_root / 'source' / 'apps' / '_dummy.kit',
                repo_root,
                args.config
            )
        return 0 if success else 1

    # Validation mode
    print(f"\nMode: Validate dependencies")
    check_registry = not args.no_registry

    if args.kit_file:
        valid, errors = validate_kit_file(
            args.kit_file,
            repo_root,
            check_registry,
            args.config
        )

        if not valid:
            print(f"\n{'='*70}")
            print(f"✗ VALIDATION FAILED")
            print(f"{'='*70}")
            for error in errors:
                print(f"  {error}")
            return 1
        else:
            print(f"\n{'='*70}")
            print(f"✓ VALIDATION PASSED")
            print(f"{'='*70}")
            return 0
    else:
        # Validate all
        all_valid, all_errors = validate_all_kit_files(
            repo_root,
            check_registry,
            args.config,
            args.fail_fast
        )

        if not all_valid:
            print(f"\n{'='*70}")
            print(f"✗ VALIDATION FAILED")
            print(f"{'='*70}")
            for kit_file, errors in all_errors.items():
                print(f"\n{kit_file}:")
                for error in errors:
                    print(f"  - {error}")
            return 1
        else:
            print(f"\n{'='*70}")
            print(f"✓ ALL VALIDATIONS PASSED")
            print(f"{'='*70}")
            return 0


if __name__ == '__main__':
    # Standalone execution
    config = {'root': str(Path.cwd())}
    sys.exit(main(config))
