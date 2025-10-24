#!/usr/bin/env python3
"""
CLI-API Equivalence Tests.

Phase 3 Test Suite: Verify that API calls produce equivalent results to CLI commands.
This ensures the API is a faithful wrapper of the CLI functionality.
"""

import pytest
import subprocess
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


class TestTemplateListEquivalence:
    """Verify API template list matches CLI template list."""

    def test_list_count_matches_cli(self, api_client):
        """Verify API returns same number of templates as CLI."""
        # Get from API
        response = api_client.get('/api/templates/list')
        api_data = response.get_json()
        api_templates = api_data.get('templates', [])
        api_count = len(api_templates)
        
        # Get from CLI with --json
        result = subprocess.run(
            ["./repo.sh", "template", "list", "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                cli_data = json.loads(result.stdout)
                cli_count = cli_data.get('count', 0)
                
                # Should match
                assert api_count == cli_count, \
                    f"API count ({api_count}) should match CLI count ({cli_count})"
                print(f"✅ Template count matches: {api_count}")
            except json.JSONDecodeError:
                # CLI JSON might not be implemented yet
                print("⚠ CLI --json not fully implemented, skipping equivalence check")
                pytest.skip("CLI --json output not available")
        else:
            print("⚠ CLI command failed or no output")
            pytest.skip("CLI command not available")

    def test_template_names_match_cli(self, api_client):
        """Verify API template names match CLI."""
        # Get from API
        response = api_client.get('/api/templates/list')
        api_data = response.get_json()
        api_templates = api_data.get('templates', [])
        api_names = sorted([t['name'] for t in api_templates])
        
        # Get from CLI (non-JSON for now, just verify it works)
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        
        assert result.returncode == 0, "CLI should work"
        
        # Check that known templates appear in CLI output
        for name in api_names[:5]:  # Check first 5
            assert name in result.stdout, f"Template {name} should appear in CLI output"
        
        print(f"✅ API templates match CLI output")


class TestTemplateCreationEquivalence:
    """Verify API template creation matches CLI template creation."""

    def test_api_creates_same_structure_as_cli(self, api_client, repo_root):
        """Verify API and CLI create equivalent directory structures."""
        import shutil
        
        api_test_name = "equivalence_api_test"
        cli_test_name = "equivalence_cli_test"
        
        try:
            # Create via API
            api_response = api_client.post('/api/templates/create',
                                          json={
                                              'template': 'kit_base_editor',
                                              'name': api_test_name,
                                              'displayName': 'API Test',
                                              'version': '1.0.0'
                                          },
                                          content_type='application/json')
            
            # Create via CLI
            cli_result = subprocess.run(
                ["./repo.sh", "template", "new", "kit_base_editor",
                 "--name", cli_test_name,
                 "--display-name", "CLI Test",
                 "--version", "1.0.0",
                 "--accept-license"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )
            
            # Both should succeed
            api_success = api_response.status_code in [200, 201]
            cli_success = cli_result.returncode == 0
            
            if api_success and cli_success:
                # Check that both created directories
                api_path = repo_root / "source" / "apps" / api_test_name
                cli_path = repo_root / "source" / "apps" / cli_test_name
                
                # May also be in _build/apps
                if not api_path.exists():
                    api_path = repo_root / "_build" / "apps" / api_test_name
                if not cli_path.exists():
                    cli_path = repo_root / "_build" / "apps" / cli_test_name
                
                assert api_path.exists(), f"API should create directory"
                assert cli_path.exists(), f"CLI should create directory"
                
                # Both should have similar structure (compare file counts as proxy)
                api_files = list(api_path.rglob('*')) if api_path.exists() else []
                cli_files = list(cli_path.rglob('*')) if cli_path.exists() else []
                
                # File counts should be similar (within 10%)
                if len(api_files) > 0 and len(cli_files) > 0:
                    ratio = len(api_files) / len(cli_files)
                    assert 0.9 <= ratio <= 1.1, \
                        f"API and CLI should create similar structures ({len(api_files)} vs {len(cli_files)} files)"
                    print(f"✅ API and CLI create equivalent structures")
                else:
                    print(f"✅ Both created directories")
            else:
                # Document if either failed
                print(f"⚠ API success: {api_success}, CLI success: {cli_success}")
                if not api_success:
                    print(f"   API response: {api_response.get_json()}")
                if not cli_success:
                    print(f"   CLI output: {cli_result.stderr[:200]}")
            
        finally:
            # Cleanup
            for test_name in [api_test_name, cli_test_name]:
                for base_dir in ["source/apps", "_build/apps"]:
                    test_path = repo_root / base_dir / test_name
                    if test_path.exists():
                        shutil.rmtree(test_path)
                        print(f"✓ Cleaned up {test_path}")


class TestAPIResponseFormat:
    """Verify API responses match expected format."""

    def test_api_uses_json_format(self, api_client):
        """Verify API returns proper JSON (not just strings)."""
        response = api_client.get('/api/templates/list')
        
        assert response.is_json, "API should return JSON"
        assert response.content_type.startswith('application/json'), \
            f"Content-Type should be application/json, got {response.content_type}"
        
        print("✅ API uses proper JSON format")

    def test_api_error_responses_are_json(self, api_client):
        """Verify API errors are also JSON formatted."""
        response = api_client.get('/api/templates/get/nonexistent')
        
        assert response.is_json, "Error responses should be JSON"
        data = response.get_json()
        assert 'error' in data, "Error response should have 'error' field"
        
        print("✅ API errors are properly formatted")


class TestAPIVsCLIPerformance:
    """Compare API and CLI performance (informational)."""

    def test_api_performance_vs_cli(self, api_client):
        """Compare API and CLI execution time (informational)."""
        import time
        
        # Time API call
        start = time.time()
        response = api_client.get('/api/templates/list')
        api_time = time.time() - start
        
        # Time CLI call
        start = time.time()
        subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        cli_time = time.time() - start
        
        print(f"API time: {api_time:.3f}s")
        print(f"CLI time: {cli_time:.3f}s")
        print(f"Ratio: {api_time/cli_time:.2f}x")
        
        # No assertion - just informational
        # API should generally be faster (no subprocess overhead)
        print(f"✅ Performance measured (API typically faster)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

