#!/usr/bin/env python3
"""
License acceptance manager for Kit App Template.
Prompts user to accept terms on first run and stores acceptance.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# License text
LICENSE_TEXT = """
By downloading or using the software and materials provided, you agree to the governing terms:

The software and materials are governed by the NVIDIA Software License Agreement and the Product-Specific Terms for NVIDIA Omniverse.

NVIDIA Software License Agreement: https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement/
Product-Specific Terms for NVIDIA Omniverse: https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-omniverse/
"""

class LicenseManager:
    """Manages license acceptance for Kit App Template."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize license manager.

        Args:
            config_dir: Optional custom config directory. Defaults to ~/.omni/kit-app-template/
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".omni" / "kit-app-template"

        self.license_file = self.config_dir / "license_accepted.json"

    def is_license_accepted(self) -> bool:
        """Check if license has been accepted."""
        if not self.license_file.exists():
            return False

        try:
            with open(self.license_file, 'r') as f:
                data = json.load(f)
                return data.get('accepted', False)
        except Exception:
            return False

    def get_acceptance_info(self) -> Optional[Dict]:
        """Get license acceptance information."""
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def store_acceptance(self, accepted: bool = True) -> bool:
        """
        Store license acceptance.

        Args:
            accepted: Whether license was accepted

        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Store acceptance with timestamp
            data = {
                'accepted': accepted,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',  # License version for future tracking
            }

            with open(self.license_file, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Warning: Failed to store license acceptance: {e}", file=sys.stderr)
            return False

    def prompt_for_acceptance(self, force: bool = False) -> bool:
        """
        Prompt user to accept license terms.

        Args:
            force: If True, prompt even if already accepted

        Returns:
            True if accepted, False if declined
        """
        # Check if already accepted
        if not force and self.is_license_accepted():
            return True

        # Print license text
        print(LICENSE_TEXT)

        # Prompt for acceptance
        while True:
            try:
                response = input("Do you accept the governing terms? (Yes/No): ").strip().lower()

                if response in ['yes', 'y']:
                    self.store_acceptance(True)
                    return True
                elif response in ['no', 'n']:
                    print("\nLicense terms not accepted. Cannot proceed.", file=sys.stderr)
                    return False
                else:
                    print("Please answer 'Yes' or 'No'")
            except (EOFError, KeyboardInterrupt):
                print("\n\nLicense terms not accepted. Cannot proceed.", file=sys.stderr)
                return False

def check_and_prompt_license(force: bool = False, config_dir: Optional[Path] = None) -> bool:
    """
    Check license acceptance and prompt if necessary.

    Args:
        force: If True, prompt even if already accepted
        config_dir: Optional custom config directory

    Returns:
        True if license is accepted, False otherwise
    """
    manager = LicenseManager(config_dir)

    if not force and manager.is_license_accepted():
        return True

    return manager.prompt_for_acceptance(force)

def main():
    """Command-line interface for license management."""
    import argparse

    parser = argparse.ArgumentParser(
        description="License acceptance manager for Kit App Template"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help="Check if license is accepted (exit 0 if yes, 1 if no)"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Force re-acceptance of license"
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help="Show license acceptance information"
    )
    parser.add_argument(
        '--config-dir',
        type=Path,
        help="Custom config directory"
    )

    args = parser.parse_args()

    manager = LicenseManager(args.config_dir)

    if args.check:
        # Check mode - silent exit code
        sys.exit(0 if manager.is_license_accepted() else 1)

    if args.info:
        # Show acceptance info
        info = manager.get_acceptance_info()
        if info:
            print("License Acceptance Information:")
            print(f"  Status: Accepted")
            print(f"  Date: {info.get('timestamp', 'Unknown')}")
            print(f"  Version: {info.get('version', 'Unknown')}")
            print(f"  Config: {manager.license_file}")
        else:
            print("License has not been accepted yet.")
        sys.exit(0)

    # Default: prompt for acceptance
    if check_and_prompt_license(force=args.force, config_dir=args.config_dir):
        print("\n✓ License terms accepted.")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
