#!/usr/bin/env python3
"""
Lightweight CLI for Kit dependency operations.

Commands:
  - validate: local-only validation of .kit dependencies (fast)
  - estimate: print estimated size/time
  - prefetch: delegate to validate_kit_deps.py --prefetch

This CLI intentionally shells to existing script(s) to minimize churn.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Local defaults (kept in sync with backend/config.py)
ESTIMATED_SIZE_BYTES: int = 12 * 1024 * 1024 * 1024
DEFAULT_BANDWIDTH_MBPS: float = 50.0


def estimate_cmd(args: argparse.Namespace) -> int:
    bw = float(args.bandwidth or DEFAULT_BANDWIDTH_MBPS)
    bytes_per_second = (bw * 1024 * 1024) / 8
    seconds = int(ESTIMATED_SIZE_BYTES / bytes_per_second)
    if args.json:
        print(
            json.dumps(
                {
                    "estimated_size_bytes": ESTIMATED_SIZE_BYTES,
                    "bandwidth_mbps": bw,
                    "estimated_seconds": seconds,
                }
            )
        )
    else:
        print(f"Estimated size: {ESTIMATED_SIZE_BYTES / (1024**3):.1f} GB")
        print(f"Bandwidth:      {bw:.0f} Mbps")
        mins = seconds // 60
        print(f"Estimated time: ~{mins} minutes")
    return 0


def validate_cmd(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "tools" / "repoman" / "validate_kit_deps.py"
    cmd = [sys.executable, str(script)]
    if args.check_registry:
        cmd.append("--check-registry")
    if args.verbose:
        cmd.append("-v")
    return subprocess.call(cmd, cwd=repo_root)


def prefetch_cmd(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "tools" / "repoman" / "validate_kit_deps.py"
    cmd = [
        sys.executable,
        str(script),
        "--prefetch",
    ]
    if args.config:
        cmd += ["--config", args.config]
    if args.verbose:
        cmd.append("-v")
    return subprocess.call(cmd, cwd=repo_root)


def main() -> int:
    ap = argparse.ArgumentParser(prog="kit-deps", description="Kit dependency tools")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("estimate", help="Estimate size/time for first-time dependencies")
    sp.add_argument("--bandwidth", type=float, default=DEFAULT_BANDWIDTH_MBPS)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=estimate_cmd)

    sp = sub.add_parser("validate", help="Validate .kit deps (local-only by default)")
    sp.add_argument("--check-registry", action="store_true")
    sp.add_argument("-v", "--verbose", action="store_true")
    sp.set_defaults(func=validate_cmd)

    sp = sub.add_parser("prefetch", help="Pre-fetch extensions using SDK")
    sp.add_argument("--config", default="release")
    sp.add_argument("-v", "--verbose", action="store_true")
    sp.set_defaults(func=prefetch_cmd)

    args = ap.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
