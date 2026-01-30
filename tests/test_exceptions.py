"""Tests for exception classes."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gif_tools import GifCreationError


class TestGifCreationError:
    """Tests for GifCreationError exception."""
    
    def test_exception_creation(self):
        """Test creating a GifCreationError."""
        error = GifCreationError("Test error message")
        assert str(error) == "Test error message"
    
    def test_exception_inheritance(self):
        """Test that GifCreationError inherits from Exception."""
        error = GifCreationError("Test")
        assert isinstance(error, Exception)
    
    def test_raise_and_catch(self):
        """Test raising and catching GifCreationError."""
        with pytest.raises(GifCreationError, match="Specific error"):
            raise GifCreationError("Specific error")
    
    def test_exception_with_empty_message(self):
        """Test creating error with empty message."""
        error = GifCreationError("")
        assert str(error) == ""
