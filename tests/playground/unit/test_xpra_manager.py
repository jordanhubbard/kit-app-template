import os
import pytest

# Skip Xpra-dependent tests by default; enable with XPRA_TESTS=1
if os.environ.get("XPRA_TESTS") != "1":
    pytest.skip("Skipping Xpra-dependent tests by default", allow_module_level=True)
"""
Unit tests for XpraManager
"""
import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "kit_playground"))

from kit_playground.backend.xpra_manager import XpraSession, XpraManager


class TestXpraSession:
    """Test XpraSession class."""

    def test_session_initialization(self):
        """Test that XpraSession initializes correctly."""
        session = XpraSession(display_number=100, port=10000)
        assert session.display_number == 100
        assert session.port == 10000
        assert session.process is None
        assert session.app_process is None
        assert session.started is False

    def test_session_no_shell_injection(self):
        """Test that launch_app uses shell=False (security)."""
        import inspect
        source = inspect.getsource(XpraSession.launch_app)
        assert "shell=False" in source, \
            "launch_app should use shell=False for security"
        assert "shlex" in source or "shell=False" in source, \
            "Should use safe argument parsing"


class TestXpraManager:
    """Test XpraManager class."""

    def test_manager_initialization(self):
        """Test that XpraManager initializes correctly."""
        manager = XpraManager()
        assert hasattr(manager, 'sessions')
        assert isinstance(manager.sessions, dict)
        assert hasattr(manager, 'next_display')
        assert hasattr(manager, 'base_port')

    def test_create_session(self):
        """Test session creation."""
        manager = XpraManager()
        session = manager.create_session("test_session")

        assert session is not None
        assert session.display_number > 0
        assert session.port > 0
        assert "test_session" in manager.sessions

    def test_get_session_url_with_custom_host(self):
        """Test get_session_url with custom host."""
        manager = XpraManager()
        session = manager.create_session("test_session")
        session.started = True

        # Test with custom host
        url = manager.get_session_url("test_session", host="192.168.1.100")
        assert url is not None
        assert "192.168.1.100" in url
        assert str(session.port) in url

    def test_get_session_url_default_localhost(self):
        """Test get_session_url defaults to localhost."""
        manager = XpraManager()
        session = manager.create_session("test_session")
        session.started = True

        # Test without host (should default to localhost)
        url = manager.get_session_url("test_session")
        assert url is not None
        assert "localhost" in url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
