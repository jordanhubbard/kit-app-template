#!/usr/bin/env python3

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KIT_ICON_KEYS = {
    # Common keys used across .kit files
    "settings.app.window.iconPath": re.compile(r"iconPath\s*=\s*\"([^\"]+)\""),
    "menu.icon.file": re.compile(r"icon\.file\s*=\s*\"([^\"]+)\""),
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        # Best-effort read; the validator should not crash on unreadable files
        return ""


def token_resolve(path_str: str) -> str:
    # Resolve simple tokens used in templates/built apps
    # We can only verify local paths (data/..., assets/..., ${ext}/...)
    # Strip common tokens that resolve to app/extension roots at runtime
    # and map them to likely local folders for verification.
    s = path_str
    # Remove Jinja tokens if any
    s = s.replace("${% raw %}", "").replace("{% endraw %}", "")
    # Simplify ${app}/.. style which we cannot reliably resolve -> leave as-is
    return s


def validate_extension_icons() -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    for ext_cfg in ROOT.glob("source/extensions/**/config/extension.toml"):
        text = read_text(ext_cfg)
        # icon and preview_image are typically relative to extension root
        for key in ("icon", "preview_image"):
            m = re.search(
                rf"^\s*{key}\s*=\s*\"([^\"]+)\"",
                text,
                flags=re.MULTILINE,
            )
            if not m:
                continue
            rel = token_resolve(m.group(1))
            # extension root + rel
            candidate = ext_cfg.parent.parent / rel
            if not candidate.exists():
                problems.append((str(ext_cfg), f"Missing {key} -> {rel}"))
    return problems


def extract_values(pattern: re.Pattern, text: str) -> list[str]:
    return [m.group(1) for m in pattern.finditer(text)]


def validate_built_app_icons() -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    for kit_file in ROOT.glob("_build/apps/**/**/*.kit"):
        text = read_text(kit_file)
        for name, pattern in KIT_ICON_KEYS.items():
            for value in extract_values(pattern, text):
                value_resolved = token_resolve(value)
                # Only check relative local paths like data/, assets/
                if value_resolved.startswith(("data/", "assets/")):
                    # app folder parent + rel
                    candidate = kit_file.parent.parent / value_resolved
                    if not candidate.exists():
                        problems.append(
                            (
                                str(kit_file),
                                f"Missing {name} -> {value_resolved}",
                            )
                        )
    return problems


def main() -> int:
    problems = []
    problems += validate_extension_icons()
    problems += validate_built_app_icons()

    if problems:
        print("Icon validation found issues:\n")
        for file, msg in problems:
            print(f"- {file}: {msg}")
        print(f"\nTotal issues: {len(problems)}")
        return 1
    else:
        print("All icon paths validated successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
