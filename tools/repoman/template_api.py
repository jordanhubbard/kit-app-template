#!/usr/bin/env python3
"""
Unified API for template operations.
Provides a common interface for both CLI and GUI (REST API) usage.

This module ensures that CLI and GUI use the exact same backend code,
just with different binding mechanisms (in-process vs REST).
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from template_engine import TemplateEngine, TemplateDiscovery
from license_manager import LicenseManager, check_and_prompt_license


@dataclass
class TemplateGenerationRequest:
    """Request for generating a template."""
    template_name: str
    name: str
    display_name: str
    version: str = "0.1.0"
    config_file: Optional[str] = None
    output_dir: Optional[str] = None
    add_layers: bool = False
    layers: Optional[List[str]] = None
    accept_license: bool = False
    force_overwrite: bool = False  # Skip directory overwrite confirmation
    # Additional arbitrary parameters
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class TemplateGenerationResult:
    """Result of template generation."""
    success: bool
    playback_file: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    created_files: Optional[List[str]] = None


@dataclass
class TemplateInfo:
    """Template information."""
    name: str
    display_name: str
    type: str
    category: Optional[str]
    description: str
    version: str
    tags: List[str]
    documentation: Dict[str, Any]


@dataclass
class LicenseStatus:
    """License acceptance status."""
    accepted: bool
    timestamp: Optional[str] = None
    version: Optional[str] = None


class TemplateAPI:
    """
    Unified API for template operations.
    Used by both CLI (direct calls) and GUI (via REST endpoints).
    """

    def __init__(self, repo_root: Optional[str] = None):
        """
        Initialize template API.

        Args:
            repo_root: Repository root directory. Auto-detected if not provided.
        """
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            # Auto-detect repo root
            current = Path(__file__).parent
            while current.parent != current:
                if (current / "repo.toml").exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path(__file__).parent / ".." / ".."

        self.engine = TemplateEngine(str(self.repo_root))
        self.discovery = TemplateDiscovery(str(self.repo_root))
        self.license_manager = LicenseManager()

    # ============= License Operations =============

    def check_license(self) -> LicenseStatus:
        """
        Check license acceptance status.

        Returns:
            LicenseStatus object with acceptance information
        """
        info = self.license_manager.get_acceptance_info()
        if info:
            return LicenseStatus(
                accepted=info.get('accepted', False),
                timestamp=info.get('timestamp'),
                version=info.get('version')
            )
        return LicenseStatus(accepted=False)

    def accept_license(self) -> bool:
        """
        Accept license programmatically.

        Returns:
            True if acceptance stored successfully
        """
        return self.license_manager.accept_license()

    def get_license_text(self) -> str:
        """
        Get license text.

        Returns:
            License text string
        """
        from license_manager import LICENSE_TEXT
        return LICENSE_TEXT

    # ============= Template Discovery Operations =============

    def list_templates(self, template_type: Optional[str] = None,
                      category: Optional[str] = None) -> List[TemplateInfo]:
        """
        List available templates.

        Args:
            template_type: Filter by type (application, extension, microservice, component)
            category: Filter by category

        Returns:
            List of TemplateInfo objects
        """
        templates_dict = self.engine.list_templates(template_type, category)

        result = []
        for name, config in templates_dict.items():
            metadata = config.get('metadata', {})
            result.append(TemplateInfo(
                name=name,
                display_name=metadata.get('display_name', name),
                type=metadata.get('type', 'unknown'),
                category=metadata.get('category'),
                description=metadata.get('description', ''),
                version=metadata.get('version', '0.0.0'),
                tags=metadata.get('tags', {}).get('tags', []),
                documentation=config.get('documentation', {})
            ))

        return result

    def get_template(self, template_name: str) -> Optional[TemplateInfo]:
        """
        Get information about a specific template.

        Args:
            template_name: Name of the template

        Returns:
            TemplateInfo object or None if not found
        """
        templates = self.list_templates()
        for template in templates:
            if template.name == template_name:
                return template
        return None

    def get_template_docs(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get documentation for a template.

        Args:
            template_name: Name of the template

        Returns:
            Dictionary with template documentation or None if not found
        """
        return self.engine.get_template_documentation(template_name)

    # ============= Template Generation Operations =============

    def generate_template(self, request: Union[TemplateGenerationRequest, Dict]) -> TemplateGenerationResult:
        """
        Generate a template from a request.

        Args:
            request: TemplateGenerationRequest object or dict with same fields

        Returns:
            TemplateGenerationResult object
        """
        # Convert dict to TemplateGenerationRequest if needed
        if isinstance(request, dict):
            # Extract known fields
            req_dict = {k: v for k, v in request.items()
                       if k in TemplateGenerationRequest.__annotations__}
            request = TemplateGenerationRequest(**req_dict)

        # Check license
        if not self.license_manager.is_license_accepted():
            if request.accept_license:
                self.license_manager.accept_license()
            else:
                return TemplateGenerationResult(
                    success=False,
                    error="License terms have not been accepted. Set accept_license=True or accept manually."
                )

        try:
            # Build kwargs from request
            kwargs = {
                'name': request.name,
                'display_name': request.display_name,
                'version': request.version,
            }

            # Add layers if specified
            if request.add_layers:
                kwargs['add_layers'] = 'Yes'
                if request.layers:
                    kwargs['layers'] = request.layers

            # Add force_overwrite if specified
            if request.force_overwrite:
                kwargs['force_overwrite'] = True

            # Add extra params
            if request.extra_params:
                kwargs.update(request.extra_params)

            # Generate template
            playback = self.engine.generate_template(
                request.template_name,
                request.config_file,
                request.output_dir,
                **kwargs
            )

            # Save playback file
            playback_file = self.engine.save_playback_file(playback)

            return TemplateGenerationResult(
                success=True,
                playback_file=playback_file,
                message=f"Template '{request.template_name}' generated successfully"
            )

        except ValueError as e:
            return TemplateGenerationResult(
                success=False,
                error=str(e)
            )
        except Exception as e:
            return TemplateGenerationResult(
                success=False,
                error=f"Failed to generate template: {str(e)}"
            )

    def generate_template_simple(self, template_name: str, name: str,
                                 display_name: str, version: str = "0.1.0",
                                 accept_license: bool = False,
                                 add_layers: bool = False,
                                 layers: Optional[List[str]] = None,
                                 **kwargs) -> TemplateGenerationResult:
        """
        Generate a template with simple parameters (convenience method).

        Args:
            template_name: Name of template to use
            name: Application/extension name
            display_name: Display name
            version: Version string
            accept_license: Whether to accept license
            add_layers: Whether to add layers
            layers: List of layer templates
            **kwargs: Additional parameters

        Returns:
            TemplateGenerationResult object
        """
        request = TemplateGenerationRequest(
            template_name=template_name,
            name=name,
            display_name=display_name,
            version=version,
            accept_license=accept_license,
            add_layers=add_layers,
            layers=layers,
            extra_params=kwargs
        )
        return self.generate_template(request)


# ============= Convenience Functions =============

def get_api(repo_root: Optional[str] = None) -> TemplateAPI:
    """
    Get a TemplateAPI instance.

    Args:
        repo_root: Repository root directory

    Returns:
        TemplateAPI instance
    """
    return TemplateAPI(repo_root)


# Example usage for testing
if __name__ == "__main__":
    api = get_api()

    # Test license check
    print("License status:", api.check_license())

    # Test template listing
    print("\nAvailable templates:")
    templates = api.list_templates(template_type='application')
    for t in templates[:3]:
        print(f"  - {t.name}: {t.display_name}")

    # Test template generation (with accept_license=True for testing)
    print("\nGenerating test template...")
    result = api.generate_template_simple(
        template_name='kit_base_editor',
        name='test_company.test_app',
        display_name='Test App',
        version='1.0.0',
        accept_license=True
    )
    print(f"Result: success={result.success}, message={result.message}")
    if result.error:
        print(f"Error: {result.error}")
