"""
Centralized path management for Kit Playground backend.
Ensures consistent path calculations across all routes and APIs.
"""
from pathlib import Path
from typing import Optional


class PathHelper:
    """Centralized path calculator for the Kit Playground backend."""

    def __init__(self):
        """Initialize with the repository root."""
        # Calculate repo root from this file's location
        # path_helper.py is in kit_playground/backend/
        # So parent.parent gives us the repo root
        self.repo_root = Path(__file__).parent.parent.parent.resolve()

    def get_repo_root(self) -> Path:
        """Get the absolute repository root path."""
        return self.repo_root

    def get_project_dir(self, project_name: str, standalone: bool = False) -> Path:
        """
        Get the directory where a project should be created/found.

        Args:
            project_name: Name of the project
            standalone: Whether this is a standalone project

        Returns:
            Absolute path to the project directory
        """
        if standalone:
            # Standalone projects go in kit_playground/backend/source/apps/
            return self.repo_root / "kit_playground" / "backend" / "source" / "apps" / project_name
        else:
            # Regular projects go in source/apps/
            return self.repo_root / "source" / "apps" / project_name

    def get_kit_file_path(self, project_name: str, standalone: bool = False) -> Path:
        """
        Get the absolute path to a project's .kit file.

        Args:
            project_name: Name of the project
            standalone: Whether this is a standalone project

        Returns:
            Absolute path to the .kit file
        """
        project_dir = self.get_project_dir(project_name, standalone)
        return project_dir / f"{project_name}.kit"

    def get_app_discovery_path(self, standalone: bool = False) -> Path:
        """
        Get the path where apps are discovered/created.

        Args:
            standalone: Whether this is for standalone projects

        Returns:
            Absolute path to the apps directory
        """
        if standalone:
            return self.repo_root / "kit_playground" / "backend" / "source" / "apps"
        else:
            return self.repo_root / "source" / "apps"


# Singleton instance
_path_helper = None


def get_path_helper() -> PathHelper:
    """Get the singleton PathHelper instance."""
    global _path_helper
    if _path_helper is None:
        _path_helper = PathHelper()
    return _path_helper
