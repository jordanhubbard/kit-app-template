#!/usr/bin/env python3
"""
Tests for Kit App Streaming Utilities

Tests detection, configuration, and management of Kit App Streaming
using the REAL streaming extensions (not hallucinated ones).
"""

import pytest
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'repoman'))

from streaming_utils import (
    is_streaming_app,
    get_streaming_type,
    get_streaming_url,
    get_streaming_config_path,
    STREAMING_EXTENSIONS
)


class TestStreamingExtensions:
    """Test streaming extension constants."""

    def test_streaming_extensions_correct(self):
        """Verify we're using the REAL streaming extensions."""
        # The REAL extensions that actually exist:
        assert 'default' in STREAMING_EXTENSIONS
        assert STREAMING_EXTENSIONS['default'] == 'omni.kit.livestream.app'
        
        assert 'nvcf' in STREAMING_EXTENSIONS
        assert STREAMING_EXTENSIONS['nvcf'] == 'omni.services.livestream.session'
        
        assert 'gdn' in STREAMING_EXTENSIONS
        assert STREAMING_EXTENSIONS['gdn'] == 'omni.kit.gfn'
        
        # Verify hallucinated extensions are NOT in our list
        for ext_type, ext_name in STREAMING_EXTENSIONS.items():
            assert 'omni.services.streaming.webrtc' != ext_name, \
                "Hallucinated extension detected!"
            assert 'omni.kit.streamhelper' != ext_name, \
                "Hallucinated extension detected!"


class TestStreamingDetection:
    """Test streaming app detection."""

    def test_detect_default_streaming(self, tmp_path):
        """Test detection of default streaming apps."""
        kit_file = tmp_path / "test.kit"
        kit_file.write_text("""
[package]
title = "Test App"

[dependencies]
"omni.kit.livestream.app" = {}
""")
        
        assert is_streaming_app(kit_file) is True
        assert get_streaming_type(kit_file) == 'default'

    def test_detect_nvcf_streaming(self, tmp_path):
        """Test detection of NVCF streaming apps."""
        kit_file = tmp_path / "test_nvcf.kit"
        kit_file.write_text("""
[package]
title = "Test NVCF App"

[dependencies]
"omni.services.livestream.session" = {}
"omni.ujitso.client" = {}
""")
        
        assert is_streaming_app(kit_file) is True
        assert get_streaming_type(kit_file) == 'nvcf'

    def test_detect_gdn_streaming(self, tmp_path):
        """Test detection of GDN streaming apps."""
        kit_file = tmp_path / "test_gdn.kit"
        kit_file.write_text("""
[package]
title = "Test GDN App"

[dependencies]
"omni.kit.gfn" = {}
""")
        
        assert is_streaming_app(kit_file) is True
        assert get_streaming_type(kit_file) == 'gdn'

    def test_detect_non_streaming(self, tmp_path):
        """Test detection of non-streaming apps."""
        kit_file = tmp_path / "test_regular.kit"
        kit_file.write_text("""
[package]
title = "Regular App"

[dependencies]
"omni.kit.window.viewport" = {}
""")
        
        assert is_streaming_app(kit_file) is False
        assert get_streaming_type(kit_file) is None

    def test_nonexistent_file(self, tmp_path):
        """Test handling of nonexistent files."""
        kit_file = tmp_path / "nonexistent.kit"
        
        assert is_streaming_app(kit_file) is False
        assert get_streaming_type(kit_file) is None


class TestStreamingURL:
    """Test streaming URL construction."""

    def test_default_url(self):
        """Test default URL construction."""
        url = get_streaming_url()
        assert url == 'http://localhost:47995/streaming/webrtc-client'

    def test_custom_url(self):
        """Test custom URL construction."""
        url = get_streaming_url(
            port=8080,
            hostname='example.com',
            protocol='https'
        )
        assert url == 'https://example.com:8080/streaming/webrtc-client'


class TestStreamingConfigPaths:
    """Test streaming configuration path utilities."""

    def test_default_config_path(self):
        """Test default streaming config path."""
        path = get_streaming_config_path('default')
        assert 'default_stream.kit' in path
        assert 'templates/apps/streaming_configs' in path

    def test_nvcf_config_path(self):
        """Test NVCF streaming config path."""
        path = get_streaming_config_path('nvcf')
        assert 'nvcf_stream.kit' in path

    def test_gdn_config_path(self):
        """Test GDN streaming config path."""
        path = get_streaming_config_path('gdn')
        assert 'gdn_stream.kit' in path


class TestHallucinationPrevention:
    """Tests to prevent hallucinated extensions from creeping back in."""

    def test_no_webrtc_hallucination(self):
        """Ensure omni.services.streaming.webrtc is not used."""
        # This extension DOES NOT EXIST
        hallucinated_ext = 'omni.services.streaming.webrtc'
        
        for ext_name in STREAMING_EXTENSIONS.values():
            assert ext_name != hallucinated_ext, \
                f"Hallucinated extension '{hallucinated_ext}' found in STREAMING_EXTENSIONS!"

    def test_no_streamhelper_hallucination(self):
        """Ensure omni.kit.streamhelper is not used."""
        # This extension DOES NOT EXIST
        hallucinated_ext = 'omni.kit.streamhelper'
        
        for ext_name in STREAMING_EXTENSIONS.values():
            assert ext_name != hallucinated_ext, \
                f"Hallucinated extension '{hallucinated_ext}' found in STREAMING_EXTENSIONS!"

    def test_only_real_extensions(self):
        """Verify we only use extensions that actually exist."""
        # The ONLY real streaming extensions are:
        real_extensions = {
            'omni.kit.livestream.app',           # Default
            'omni.services.livestream.session',  # NVCF
            'omni.kit.gfn',                      # GDN
        }
        
        for ext_name in STREAMING_EXTENSIONS.values():
            assert ext_name in real_extensions, \
                f"Extension '{ext_name}' is not a known real extension!"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
