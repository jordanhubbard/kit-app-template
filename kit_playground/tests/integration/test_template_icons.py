"""
Integration tests for template icon files.

Tests that all template icons exist and are valid image files.
"""
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

# Add paths for imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "kit_playground"))

from tools.repoman.template_api import TemplateAPI


@pytest.fixture(scope="module")
def template_api():
    """Create a TemplateAPI instance for testing."""
    return TemplateAPI(str(repo_root))


def get_image_type(file_path: Path) -> str:
    """
    Detect image type by reading file magic bytes.

    Args:
        file_path: Path to image file

    Returns:
        Image type string ('PNG', 'JPEG', 'SVG', 'ICO', 'UNKNOWN')
    """
    if not file_path.exists() or not file_path.is_file():
        return 'MISSING'

    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)

        # Check for PNG (89 50 4E 47 0D 0A 1A 0A)
        if header[:8] == b'\x89PNG\r\n\x1a\n':
            return 'PNG'

        # Check for JPEG (FF D8 FF)
        if header[:3] == b'\xff\xd8\xff':
            return 'JPEG'

        # Check for SVG (XML starting with <svg or <?xml)
        if b'<svg' in header or b'<?xml' in header:
            return 'SVG'

        # Check for ICO (00 00 01 00)
        if header[:4] == b'\x00\x00\x01\x00':
            return 'ICO'

        # Check for GIF (47 49 46 38)
        if header[:4] == b'GIF8':
            return 'GIF'

        return 'UNKNOWN'

    except Exception as e:
        return f'ERROR: {e}'


def find_template_icons(template_dir: Path) -> List[Tuple[Path, str]]:
    """
    Find all icon files in a template directory.

    Args:
        template_dir: Path to template directory

    Returns:
        List of (icon_path, detected_type) tuples
    """
    icons = []

    # Common icon locations
    icon_patterns = [
        "assets/icon.*",
        "data/icon.*",
        "data/*.ico",
        "data/*.png",
        "*/icon.*",
    ]

    for pattern in icon_patterns:
        for icon_file in template_dir.glob(pattern):
            if icon_file.is_file():
                image_type = get_image_type(icon_file)
                icons.append((icon_file, image_type))

    return icons


class TestTemplateIcons:
    """Test template icon files."""

    def test_application_templates_have_icons(self):
        """Test that application templates have icon files."""
        templates_dir = repo_root / "templates" / "apps"

        if not templates_dir.exists():
            pytest.skip("Templates directory not found")

        app_templates = [d for d in templates_dir.iterdir() if d.is_dir()]

        assert len(app_templates) > 0, "No application templates found"

        print(f"\nChecking icons for {len(app_templates)} application templates:")

        templates_with_icons = 0
        for template_dir in app_templates:
            icons = find_template_icons(template_dir)

            if icons:
                templates_with_icons += 1
                print(f"\n  {template_dir.name}:")
                for icon_path, image_type in icons:
                    rel_path = icon_path.relative_to(template_dir)
                    print(f"    ✓ {rel_path} ({image_type})")
            else:
                print(f"\n  {template_dir.name}: ⚠ No icons found")

        # Most application templates should have icons
        assert templates_with_icons >= 3, \
            f"Expected at least 3 application templates with icons, found {templates_with_icons}"

    def test_all_icons_are_valid_images(self):
        """Test that all found icon files are valid images."""
        templates_dir = repo_root / "templates"

        if not templates_dir.exists():
            pytest.skip("Templates directory not found")

        all_icons = []

        # Search all template directories
        for template_path in templates_dir.rglob("*"):
            if template_path.is_dir():
                icons = find_template_icons(template_path)
                all_icons.extend(icons)

        assert len(all_icons) > 0, "No icon files found in any templates"

        print(f"\nValidating {len(all_icons)} icon files:")

        valid_types = {'PNG', 'JPEG', 'SVG', 'ICO', 'GIF'}
        invalid_icons = []

        for icon_path, image_type in all_icons:
            if image_type not in valid_types:
                invalid_icons.append((icon_path, image_type))
                print(f"  ✗ {icon_path}: {image_type}")
            else:
                print(f"  ✓ {icon_path}: {image_type}")

        assert len(invalid_icons) == 0, \
            f"Found {len(invalid_icons)} invalid icon files: {invalid_icons}"

    def test_specific_template_icons(self):
        """Test that specific known templates have valid icons."""
        expected_icons = [
            ("templates/apps/kit_base_editor/assets/icon.png", "PNG"),
            ("templates/apps/kit_service/assets/icon.png", "PNG"),
            ("templates/apps/usd_viewer/assets/icon.png", "PNG"),
        ]

        print("\nChecking specific template icons:")

        for rel_path, expected_type in expected_icons:
            icon_path = repo_root / rel_path

            if not icon_path.exists():
                print(f"  ⚠ {rel_path}: File not found (skipping)")
                continue

            actual_type = get_image_type(icon_path)

            assert actual_type == expected_type, \
                f"Icon {rel_path} has incorrect type: expected {expected_type}, got {actual_type}"

            print(f"  ✓ {rel_path}: {actual_type}")

    def test_icon_file_sizes_reasonable(self):
        """Test that icon files are reasonable sizes (not corrupted/empty)."""
        templates_dir = repo_root / "templates"

        if not templates_dir.exists():
            pytest.skip("Templates directory not found")

        all_icons = []
        for template_path in templates_dir.rglob("*"):
            if template_path.is_dir():
                icons = find_template_icons(template_path)
                all_icons.extend(icons)

        print(f"\nChecking file sizes for {len(all_icons)} icons:")

        too_small = []
        too_large = []

        for icon_path, image_type in all_icons:
            size = icon_path.stat().st_size

            # Icons should be at least 100 bytes (not empty/corrupted)
            if size < 100:
                too_small.append((icon_path, size))
                print(f"  ⚠ {icon_path.name}: {size} bytes (too small)")
            # Icons shouldn't be larger than 5MB (reasonable limit)
            elif size > 5 * 1024 * 1024:
                too_large.append((icon_path, size))
                print(f"  ⚠ {icon_path.name}: {size / 1024 / 1024:.1f} MB (too large)")
            else:
                print(f"  ✓ {icon_path.name}: {size / 1024:.1f} KB")

        assert len(too_small) == 0, \
            f"Found {len(too_small)} icons that are suspiciously small (< 100 bytes)"

        assert len(too_large) == 0, \
            f"Found {len(too_large)} icons that are too large (> 5MB)"

    def test_png_icons_readable_by_pil(self):
        """Test that PNG icons can be read by PIL/Pillow (if available)."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL/Pillow not installed")

        templates_dir = repo_root / "templates"
        if not templates_dir.exists():
            pytest.skip("Templates directory not found")

        all_icons = []
        for template_path in templates_dir.rglob("*"):
            if template_path.is_dir():
                icons = find_template_icons(template_path)
                all_icons.extend(icons)

        # Filter to PNG icons only
        png_icons = [(path, typ) for path, typ in all_icons if typ == 'PNG']

        if len(png_icons) == 0:
            pytest.skip("No PNG icons found")

        print(f"\nValidating {len(png_icons)} PNG icons with PIL:")

        corrupted = []

        for icon_path, _ in png_icons:
            try:
                with Image.open(icon_path) as img:
                    # Try to get basic info
                    width, height = img.size
                    mode = img.mode
                    print(f"  ✓ {icon_path.name}: {width}x{height} {mode}")
            except Exception as e:
                corrupted.append((icon_path, str(e)))
                print(f"  ✗ {icon_path.name}: {e}")

        assert len(corrupted) == 0, \
            f"Found {len(corrupted)} corrupted PNG icons: {corrupted}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
