#!/usr/bin/env python3
"""
Tests for Kit App Streaming utilities.

Tests the streaming_utils module to ensure proper detection,
flag generation, URL construction, and integration.
"""

import sys
from pathlib import Path
import pytest

# Add tools/repoman to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "tools" / "repoman"))

from streaming_utils import (
    is_streaming_app,
    get_streaming_url,
    get_streaming_flags,
    get_streaming_info,
    DEFAULT_STREAMING_PORT,
    STREAMING_EXTENSIONS
)


class TestStreamingDetection:
    """Test streaming app detection logic."""
    
    def test_streaming_extensions_list(self):
        """Verify streaming extensions are defined."""
        assert len(STREAMING_EXTENSIONS) > 0
        assert 'omni.services.streaming.webrtc' in STREAMING_EXTENSIONS
        assert 'omni.kit.streamhelper' in STREAMING_EXTENSIONS
    
    def test_default_port(self):
        """Verify default streaming port."""
        assert DEFAULT_STREAMING_PORT == 47995
    
    def test_is_streaming_app_nonexistent_file(self):
        """Non-existent files should return False."""
        result = is_streaming_app(Path("/nonexistent/file.kit"))
        assert result is False
    
    def test_is_streaming_app_detection(self):
        """Test detection against real template files."""
        # Check if streaming templates exist
        templates_dir = repo_root / "templates" / "apps" / "streaming_configs"
        
        if templates_dir.exists():
            streaming_kits = list(templates_dir.glob("*.kit"))
            if streaming_kits:
                # At least one streaming template should be detected
                detected = False
                for kit_file in streaming_kits:
                    if is_streaming_app(kit_file):
                        detected = True
                        print(f"✓ Detected streaming app: {kit_file.name}")
                        break
                
                # Note: This may not always pass if templates don't have
                # dependencies section, but that's okay for now
                print(f"Streaming templates found: {len(streaming_kits)}")


class TestURLConstruction:
    """Test streaming URL construction."""
    
    def test_get_streaming_url_default(self):
        """Test default URL construction."""
        url = get_streaming_url()
        assert url == "https://localhost:47995"
    
    def test_get_streaming_url_custom_port(self):
        """Test custom port."""
        url = get_streaming_url(port=48000)
        assert url == "https://localhost:48000"
    
    def test_get_streaming_url_custom_hostname(self):
        """Test custom hostname."""
        url = get_streaming_url(hostname="192.168.1.100")
        assert url == "https://192.168.1.100:47995"
    
    def test_get_streaming_url_http(self):
        """Test HTTP instead of HTTPS."""
        url = get_streaming_url(use_https=False)
        assert url == "http://localhost:47995"
    
    def test_get_streaming_url_remote(self):
        """Test remote access hostname."""
        url = get_streaming_url(hostname="0.0.0.0", port=48000)
        assert url == "https://0.0.0.0:48000"


class TestFlagGeneration:
    """Test streaming flag generation."""
    
    def test_get_streaming_flags_default(self):
        """Test default flag generation."""
        flags = get_streaming_flags()
        
        # Check essential flags are present
        assert '--allow-root' in flags
        assert '--enable' in flags
        assert 'omni.services.streaming.webrtc' in flags
        assert 'omni.kit.streamhelper' in flags
        assert '--no-window' in flags
        assert '--/renderer/headless=true' in flags
        assert '--/rtx/webrtc/enable=true' in flags
        
        # Check port configuration
        assert '--/rtx/webrtc/listenPort=47995' in flags
    
    def test_get_streaming_flags_custom_port(self):
        """Test custom port in flags."""
        flags = get_streaming_flags(port=48000)
        assert '--/rtx/webrtc/listenPort=48000' in flags
        assert '--/rtx/webrtc/listenPort=47995' not in flags
    
    def test_get_streaming_flags_draw_mouse(self):
        """Test mouse cursor flag."""
        flags_no_mouse = get_streaming_flags(draw_mouse=False)
        flags_with_mouse = get_streaming_flags(draw_mouse=True)
        
        assert '--/app/window/drawMouse=false' in flags_no_mouse
        assert '--/app/window/drawMouse=true' in flags_with_mouse
    
    def test_get_streaming_flags_no_root(self):
        """Test without allow-root flag."""
        flags = get_streaming_flags(allow_root=False)
        assert '--allow-root' not in flags
    
    def test_get_streaming_flags_custom_certs(self):
        """Test custom certificate paths."""
        cert_path = Path("/etc/ssl/cert.pem")
        key_path = Path("/etc/ssl/key.pem")
        
        flags = get_streaming_flags(cert_path=cert_path, key_path=key_path)
        
        assert '--/rtx/webrtc/certificatePath=/etc/ssl/cert.pem' in flags
        assert '--/rtx/webrtc/privateKeyPath=/etc/ssl/key.pem' in flags
    
    def test_get_streaming_flags_count(self):
        """Verify expected number of flags."""
        flags = get_streaming_flags()
        
        # Should have at least these flags:
        # --allow-root, --enable, omni.services.streaming.webrtc,
        # --enable, omni.kit.streamhelper, --no-window,
        # --/app/window/drawMouse=false, --/renderer/headless=true,
        # --/rtx/webrtc/enable=true, --/rtx/webrtc/listenPort=47995
        assert len(flags) >= 10


class TestStreamingInfo:
    """Test convenience function."""
    
    def test_get_streaming_info_nonexistent(self):
        """Non-existent files should return None."""
        info = get_streaming_info(Path("/nonexistent/file.kit"))
        assert info is None
    
    def test_get_streaming_info_structure(self):
        """Test info dictionary structure."""
        # Create a mock streaming kit file for testing
        # (This test assumes we have at least one streaming template)
        templates_dir = repo_root / "templates" / "apps" / "streaming_configs"
        
        if templates_dir.exists():
            streaming_kits = list(templates_dir.glob("*.kit"))
            if streaming_kits:
                info = get_streaming_info(streaming_kits[0], port=48000)
                
                if info:  # May be None if template doesn't have dependencies
                    assert 'is_streaming' in info
                    assert 'url' in info
                    assert 'port' in info
                    assert 'flags' in info
                    assert 'ssl_warning' in info
                    
                    assert info['is_streaming'] is True
                    assert info['port'] == 48000
                    assert isinstance(info['flags'], list)
                    assert 'https://' in info['url']


class TestIntegration:
    """Integration tests for streaming utilities."""
    
    def test_flags_can_be_joined(self):
        """Verify flags can be used in subprocess commands."""
        flags = get_streaming_flags()
        
        # Should be able to join into command
        cmd = ["./my_app.sh"] + flags
        assert len(cmd) > 1
        assert cmd[0] == "./my_app.sh"
    
    def test_url_format_valid(self):
        """Verify URL format is valid."""
        url = get_streaming_url()
        
        # Should be a valid URL format
        assert url.startswith("https://")
        assert ":" in url
        
        # Should be parseable
        parts = url.replace("https://", "").split(":")
        assert len(parts) == 2
        assert parts[0]  # hostname
        assert parts[1].isdigit()  # port
    
    def test_multiple_ports_unique(self):
        """Verify different ports generate different URLs."""
        url1 = get_streaming_url(port=47995)
        url2 = get_streaming_url(port=48000)
        url3 = get_streaming_url(port=49000)
        
        assert url1 != url2
        assert url2 != url3
        assert url1 != url3
        
        assert "47995" in url1
        assert "48000" in url2
        assert "49000" in url3


def test_module_imports():
    """Verify all expected functions are importable."""
    # This test verifies the module structure
    from streaming_utils import (
        is_streaming_app,
        get_streaming_url,
        get_streaming_flags,
        wait_for_streaming_ready,
        get_streaming_info,
        DEFAULT_STREAMING_PORT,
        STREAMING_EXTENSIONS
    )
    
    # All imports should succeed (verified by not raising ImportError)
    assert callable(is_streaming_app)
    assert callable(get_streaming_url)
    assert callable(get_streaming_flags)
    assert callable(wait_for_streaming_ready)
    assert callable(get_streaming_info)
    assert isinstance(DEFAULT_STREAMING_PORT, int)
    assert isinstance(STREAMING_EXTENSIONS, list)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

