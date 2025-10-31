#!/usr/bin/env python3
"""
Kit Dependency Validation

Validates that extensions declared in .kit files can be resolved
from local cache or online registries. Optionally pre-fetches extensions
to enable fast first launches.

Usage:
    from validate_kit_deps import validate_kit_file, prefetch_extensions

    # Validate dependencies
    valid, errors = validate_kit_file(Path("my_app.kit"))

    # Pre-fetch for offline/fast launch
    success = prefetch_extensions(Path("my_app.kit"))
"""

import json
import logging
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

try:
    import tomli as toml
except ImportError:
    try:
        import toml
    except ImportError:
        import tomllib as toml  # Python 3.11+


def read_toml(path: Path) -> Dict:
    """Read TOML file."""
    with open(path, 'rb') as f:
        return toml.load(f)


def get_registry_urls(repo_root: Path) -> List[Dict[str, str]]:
    """
    Get extension registry URLs from repo.toml.

    Returns:
        List of registry dicts with 'name' and 'url' keys
    """
    repo_toml = repo_root / "repo.toml"
    if not repo_toml.exists():
        logger.warning(f"repo.toml not found at {repo_toml}")
        return []

    config = read_toml(repo_toml)
    registries = config.get('repo_precache_exts', {}).get('registries', [])

    if not registries:
        # Fallback to default registries
        logger.info("No registries in repo.toml, using defaults")
        registries = [
            {
                'name': 'kit/default',
                'url': 'https://ovextensionsprod.blob.core.windows.net/exts/kit/prod/shared'
            },
            {
                'name': 'kit/sdk',
                'url': 'https://ovextensionsprod.blob.core.windows.net/exts/kit/prod/sdk'
            }
        ]

    return registries


def query_extension_in_registry(
    extension_name: str,
    registry_url: str,
    timeout: int = 5
) -> Optional[str]:
    """
    Query if extension exists in registry.

    Args:
        extension_name: Extension name (e.g., "omni.kit.livestream.app")
        registry_url: Base registry URL
        timeout: Request timeout in seconds

    Returns:
        Extension version if found, None otherwise
    """
    # Extension registry typically has index.json or we can probe specific versions
    try:
        # Try to fetch extension metadata
        # Most registries have a structure like: {registry}/{extension_name}/
        ext_url = urljoin(registry_url.rstrip('/') + '/', extension_name + '/')

        # Try to get any version (probe for existence)
        # Many registries support latest or have an index
        index_url = urljoin(ext_url, 'index.json')

        logger.debug(f"Querying: {index_url}")

        req = urllib.request.Request(
            index_url,
            headers={'User-Agent': 'kit-app-template-validator/1.0'}
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read())
                # Registry index typically has versions list
                versions = data.get('versions', [])
                if versions:
                    return versions[0]  # Return first available version
                return "found"  # Found but no version info

    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.debug(f"Extension {extension_name} not found in {registry_url}")
        else:
            logger.debug(f"HTTP error {e.code} querying {extension_name}: {e}")
    except urllib.error.URLError as e:
        logger.debug(f"URL error querying {extension_name}: {e}")
    except Exception as e:
        logger.debug(f"Error querying {extension_name}: {e}")

    return None


def check_local_extension(
    extension_name: str,
    repo_root: Path,
    config: str = 'release'
) -> bool:
    """
    Check if extension exists in local build directories.

    Args:
        extension_name: Extension name
        repo_root: Repository root path
        config: Build config (release/debug)

    Returns:
        True if found locally
    """
    # Check common local locations
    search_paths = [
        repo_root / 'source' / 'extensions' / extension_name,
        repo_root / '_build' / f'linux-x86_64' / config / 'exts' / extension_name,
        repo_root / '_build' / f'windows-x86_64' / config / 'exts' / extension_name,
    ]

    for path in search_paths:
        if path.exists() and (path / 'extension.toml').exists():
            logger.debug(f"Found local extension: {extension_name} at {path}")
            return True

    return False


def validate_kit_file(
    kit_file: Path,
    repo_root: Path,
    check_registry: bool = True,
    config: str = 'release'
) -> Tuple[bool, List[str]]:
    """
    Validate all dependencies in a .kit file can be resolved.

    Args:
        kit_file: Path to .kit file
        repo_root: Repository root path
        check_registry: Whether to query online registries
        config: Build config (release/debug)

    Returns:
        Tuple of (all_valid, list_of_error_messages)
    """
    if not kit_file.exists():
        return False, [f"Kit file not found: {kit_file}"]

    try:
        config_data = read_toml(kit_file)
    except Exception as e:
        return False, [f"Failed to parse {kit_file}: {e}"]

    dependencies = config_data.get('dependencies', {})
    if not dependencies:
        logger.info(f"No dependencies found in {kit_file}")
        return True, []

    errors = []
    checked = 0
    found_local = 0
    found_registry = 0

    registries = get_registry_urls(repo_root) if check_registry else []

    print(f"\n{'='*70}")
    print(f"Validating {kit_file.name}")
    print(f"{'='*70}")
    print(f"Found {len(dependencies)} dependencies to validate")

    for ext_name in dependencies.keys():
        checked += 1

        # Check local first (faster)
        if check_local_extension(ext_name, repo_root, config):
            found_local += 1
            print(f"  ✓ {ext_name:<50} [local]")
            continue

        # Check registries
        found_in_registry = False
        if check_registry:
            for registry in registries:
                version = query_extension_in_registry(
                    ext_name,
                    registry['url']
                )
                if version:
                    found_registry += 1
                    found_in_registry = True
                    print(f"  ✓ {ext_name:<50} [{registry['name']}]")
                    break

        if not found_in_registry and check_registry:
            errors.append(f"Cannot resolve extension: {ext_name}")
            print(f"  ✗ {ext_name:<50} [NOT FOUND]")

    # Summary
    print(f"\n{'='*70}")
    print(f"Validation Summary:")
    print(f"  Total checked:     {checked}")
    print(f"  Found locally:     {found_local}")
    if check_registry:
        print(f"  Found in registry: {found_registry}")
    print(f"  Missing:           {len(errors)}")
    print(f"{'='*70}\n")

    all_valid = len(errors) == 0
    return all_valid, errors


def prefetch_extensions(
    kit_file: Path,
    repo_root: Path,
    config: str = 'release'
) -> bool:
    """
    Pre-fetch (download) all extensions for a .kit file.

    This uses Kit SDK's built-in extension pulling mechanism.

    Args:
        kit_file: Path to .kit file
        repo_root: Repository root path
        config: Build config (release/debug)

    Returns:
        True if successful
    """
    print(f"\n{'='*70}")
    print(f"Pre-fetching extensions for {kit_file.name}")
    print(f"{'='*70}\n")

    # Use Kit SDK's pull_extensions command
    # This is the proper way to pre-download extensions
    try:
        import subprocess

        # Call repo_kit_pull_extensions (the proper tool for this)
        cmd = [
            sys.executable,
            str(repo_root / 'repo.sh'),
            'pull_extensions',
            'setup',
            '-c', config
        ]

        print(f"Running: {' '.join(cmd)}")
        print(f"This will download all extensions declared in .kit files...")
        print(f"(This may take several minutes on first run)\n")

        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=False
        )

        if result.returncode == 0:
            print(f"\n✓ Successfully pre-fetched extensions")
            return True
        else:
            print(f"\n✗ Failed to pre-fetch extensions (exit code: {result.returncode})")
            return False

    except Exception as e:
        logger.error(f"Failed to pre-fetch extensions: {e}")
        print(f"\n✗ Error: {e}")
        return False


def validate_all_kit_files(
    repo_root: Path,
    check_registry: bool = True,
    config: str = 'release',
    fail_fast: bool = False
) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Validate all .kit files in the repository.

    Args:
        repo_root: Repository root path
        check_registry: Whether to query online registries
        config: Build config (release/debug)
        fail_fast: Stop on first error

    Returns:
        Tuple of (all_valid, dict_of_errors_by_kit_file)
    """
    # Find all .kit files
    apps_dir = repo_root / 'source' / 'apps'
    if not apps_dir.exists():
        logger.warning(f"Apps directory not found: {apps_dir}")
        return True, {}

    kit_files = list(apps_dir.rglob('*.kit'))
    if not kit_files:
        logger.info("No .kit files found")
        return True, {}

    print(f"\nFound {len(kit_files)} .kit file(s) to validate")

    all_valid = True
    all_errors = {}

    for kit_file in kit_files:
        valid, errors = validate_kit_file(kit_file, repo_root, check_registry, config)

        if not valid:
            all_valid = False
            all_errors[str(kit_file)] = errors

            if fail_fast:
                break

    return all_valid, all_errors


def main():
    """CLI entry point for validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate Kit dependencies in .kit files'
    )
    parser.add_argument(
        '--kit-file',
        type=Path,
        help='Specific .kit file to validate (default: all .kit files)'
    )
    parser.add_argument(
        '--no-registry-check',
        action='store_true',
        help='Skip online registry queries (local only)'
    )
    parser.add_argument(
        '--prefetch',
        action='store_true',
        help='Pre-fetch (download) all extensions'
    )
    parser.add_argument(
        '--config',
        default='release',
        choices=['release', 'debug'],
        help='Build configuration'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help='Repository root path'
    )
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop on first validation error'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )

    # Prefetch mode
    if args.prefetch:
        if args.kit_file:
            success = prefetch_extensions(args.kit_file, args.repo_root, args.config)
        else:
            # Prefetch runs pull_extensions which gets all apps
            success = prefetch_extensions(
                args.repo_root / 'source' / 'apps' / 'dummy.kit',  # Not used
                args.repo_root,
                args.config
            )
        sys.exit(0 if success else 1)

    # Validation mode
    check_registry = not args.no_registry_check

    if args.kit_file:
        valid, errors = validate_kit_file(
            args.kit_file,
            args.repo_root,
            check_registry,
            args.config
        )

        if not valid:
            print(f"\n✗ Validation failed for {args.kit_file.name}:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print(f"\n✓ All dependencies validated successfully")
            sys.exit(0)
    else:
        # Validate all kit files
        all_valid, all_errors = validate_all_kit_files(
            args.repo_root,
            check_registry,
            args.config,
            args.fail_fast
        )

        if not all_valid:
            print(f"\n✗ Validation failed:")
            for kit_file, errors in all_errors.items():
                print(f"\n{kit_file}:")
                for error in errors:
                    print(f"  - {error}")
            sys.exit(1)
        else:
            print(f"\n✓ All .kit files validated successfully")
            sys.exit(0)


if __name__ == '__main__':
    main()
