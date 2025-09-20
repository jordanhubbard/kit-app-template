#!/usr/bin/env python3
"""
Helper script to generate playback files for template creation.
This allows non-interactive template creation by template name.
"""

import os
import sys
import tempfile
from pathlib import Path

try:
    # Python 3.11+ has tomllib built-in
    import tomllib
    import tomli_w
    HAS_TOML = True
except ImportError:
    try:
        import toml
        HAS_TOML = True
    except ImportError:
        # Fall back to a simple TOML-like format using string formatting
        HAS_TOML = False

# Template mappings from templates.toml
APPLICATION_TEMPLATES = {
    "kit_base_editor": "Kit Base Editor",
    "omni_usd_composer": "USD Composer",
    "omni_usd_explorer": "USD Explorer",
    "omni_usd_viewer": "USD Viewer",
    "kit_service": "Kit Service"
}

EXTENSION_TEMPLATES = {
    "basic_python_extension": "Basic Python Extension",
    "basic_python_ui_extension": "Python UI Extension",
    "basic_cpp_extension": "Basic C++ Extension",
    "basic_python_binding": "Basic C++ w/ Python Binding Extension"
}

def generate_playback_file(template_name, app_name=None, display_name=None, version="0.1.0"):
    """Generate a playback file for the given template."""

    # Determine if this is an application or extension template
    if template_name in APPLICATION_TEMPLATES:
        template_type = "Application"
        template_display_name = APPLICATION_TEMPLATES[template_name]
    elif template_name in EXTENSION_TEMPLATES:
        template_type = "Extension"
        template_display_name = EXTENSION_TEMPLATES[template_name]
    else:
        print(f"Error: Unknown template '{template_name}'")
        print(f"Available application templates: {list(APPLICATION_TEMPLATES.keys())}")
        print(f"Available extension templates: {list(EXTENSION_TEMPLATES.keys())}")
        sys.exit(1)

    # Set default names if not provided
    if not app_name:
        if template_type == "Application":
            app_name = f"my_company.my_{template_name.replace('_', '')}"
        else:
            app_name = f"my_company.my_{template_name.replace('_', '')}"

    if not display_name:
        display_name = f"My {template_display_name}"

    # Create playback content using the template ID as the top-level key
    playback_content = {
        template_name: {
            f"{'application' if template_type == 'Application' else 'extension'}_name": app_name,
            f"{'application' if template_type == 'Application' else 'extension'}_display_name": display_name,
            "version": version
        }
    }

    # Add application-specific fields
    if template_type == "Application":
        playback_content[template_name]["add_layers"] = "No"

        # Add extension sections for templates that have them
        if template_name == "omni_usd_composer":
            playback_content[template_name]["extensions"] = {
                "omni_usd_composer_setup": {
                    "extension_name": f"{app_name}_setup",
                    "extension_display_name": f"{display_name} Setup",
                    "version": version
                }
            }
        elif template_name == "omni_usd_explorer":
            playback_content[template_name]["extensions"] = {
                "omni_usd_explorer_setup": {
                    "extension_name": f"{app_name}_setup",
                    "extension_display_name": f"{display_name} Setup",
                    "version": version
                }
            }
        elif template_name == "omni_usd_viewer":
            playback_content[template_name]["extensions"] = {
                "omni_usd_viewer_messaging": {
                    "extension_name": f"{app_name}_messaging",
                    "extension_display_name": f"{display_name} Messaging",
                    "version": version
                },
                "omni_usd_viewer_setup": {
                    "extension_name": f"{app_name}_setup",
                    "extension_display_name": f"{display_name} Setup",
                    "version": version
                }
            }
        elif template_name == "kit_service":
            playback_content[template_name]["extensions"] = {
                "kit_service_setup": {
                    "extension_name": f"{app_name}_setup",
                    "extension_display_name": f"{display_name} Setup",
                    "version": version
                }
            }

    return playback_content

def main():
    if len(sys.argv) < 2:
        print("Usage: template_helper.py <template_name> [app_name] [display_name] [version]")
        print(f"Available application templates: {list(APPLICATION_TEMPLATES.keys())}")
        print(f"Available extension templates: {list(EXTENSION_TEMPLATES.keys())}")
        sys.exit(1)

    template_name = sys.argv[1]
    app_name = sys.argv[2] if len(sys.argv) > 2 else None
    display_name = sys.argv[3] if len(sys.argv) > 3 else None
    version = sys.argv[4] if len(sys.argv) > 4 else "0.1.0"

    # Generate playback content
    playback_content = generate_playback_file(template_name, app_name, display_name, version)

    # Create temporary playback file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        if HAS_TOML:
            if 'tomli_w' in globals():
                tomli_w.dump(playback_content, f)
            else:
                toml.dump(playback_content, f)
        else:
            # Write TOML manually
            def write_dict(d, prefix=""):
                for key, value in d.items():
                    if isinstance(value, dict):
                        if prefix:
                            f.write(f"\n[{prefix}.{key}]\n")
                        else:
                            f.write(f"[{key}]\n")
                        write_dict(value, f"{prefix}.{key}" if prefix else key)
                    else:
                        f.write(f'{key} = "{value}"\n')

            write_dict(playback_content)

        playback_file = f.name

    print(playback_file)

if __name__ == "__main__":
    main()