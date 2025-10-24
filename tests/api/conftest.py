"""
Shared pytest fixtures for API tests.
"""

import pytest
import sys
from pathlib import Path

# Add kit_playground to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "kit_playground"))
sys.path.insert(0, str(REPO_ROOT))

@pytest.fixture(scope="session")
def api_client():
    """Create a Flask test client for API testing (session-scoped to avoid blueprint re-registration)."""
    from kit_playground.backend.web_server import PlaygroundWebServer
    from kit_playground.core.playground_app import PlaygroundApp
    from kit_playground.core.config import PlaygroundConfig

    # Create test configuration
    config = PlaygroundConfig()
    app = PlaygroundApp(config)

    # Create web server
    server = PlaygroundWebServer(app, config)
    server.app.config['TESTING'] = True

    # Return test client (session-scoped, reused across all tests)
    return server.app.test_client()

@pytest.fixture
def repo_root():
    """Provide repository root path."""
    return REPO_ROOT
