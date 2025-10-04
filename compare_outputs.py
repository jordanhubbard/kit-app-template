#!/usr/bin/env python3
"""Compare CLI output with API output for template list."""

import sys
import json
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent / "tools" / "repoman"))

from template_api import TemplateAPI

def main():
    # Initialize API
    api = TemplateAPI(str(Path(__file__).parent))

    # Get templates via API (same as web endpoint would call)
    templates = api.list_templates()

    print("=" * 80)
    print("API OUTPUT (as returned by /api/v2/templates endpoint)")
    print("=" * 80)

    # Convert to dict format (as web_server.py does on line 301-311)
    api_result = []
    for t in templates:
        api_result.append({
            'id': t.name,
            'name': t.name,
            'displayName': t.display_name,
            'type': t.type,
            'category': t.category,
            'description': t.description,
            'version': t.version,
            'tags': t.tags,
            'documentation': t.documentation
        })

    print(json.dumps(api_result, indent=2))

    print("\n" + "=" * 80)
    print("CLI OUTPUT (as displayed by './repo.sh template list')")
    print("=" * 80)

    # Group by type (as CLI does on line 1110-1116)
    by_type = {}
    for t in templates:
        t_type = t.type
        if t_type not in by_type:
            by_type[t_type] = []
        by_type[t_type].append(t)

    for t_type in sorted(by_type.keys()):
        print(f"\n{t_type.upper()} Templates:")
        print("-" * 40)
        for t in sorted(by_type[t_type], key=lambda x: x.name):
            print(f"  {t.name:<25} - {t.display_name}")
            if t.description != t.display_name:
                desc = t.description[:60] + ('...' if len(t.description) > 60 else '')
                print(f"  {' ' * 27} {desc}")

    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"\nTotal templates found: {len(templates)}")
    print(f"Template types: {sorted(by_type.keys())}")
    print(f"\nCLI output: Human-readable text grouped by type")
    print(f"API output: JSON array with full metadata")
    print(f"\nBoth use the same underlying TemplateAPI.list_templates() method.")
    print(f"Difference is only in formatting:")
    print(f"  - CLI: Formatted text output")
    print(f"  - API: JSON with additional fields (version, tags, documentation)")

if __name__ == "__main__":
    main()
