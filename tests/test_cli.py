"""Tests for the CLI script."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import the main function
from create_gif_from_images import main


class TestCLI:
    """Tests for command-line interface."""
    
    def test_main_with_valid_config(self, valid_config):
        """Test main function with valid configuration."""
        with patch.object(sys, 'argv', ['script.py', valid_config]):
            exit_code = main()
        
        assert exit_code == 0
    
    def test_main_with_nonexistent_config(self):
        """Test main function with nonexistent config file."""
        with patch.object(sys, 'argv', ['script.py', '/nonexistent/config.yml']):
            exit_code = main()
        
        assert exit_code == 1
    
    def test_main_with_custom_output(self, valid_config, temp_dir):
        """Test main function with custom output path."""
        import os
        custom_output = os.path.join(temp_dir, 'cli_output.gif')
        
        with patch.object(sys, 'argv', ['script.py', valid_config, '-o', custom_output]):
            exit_code = main()
        
        assert exit_code == 0
        assert os.path.exists(custom_output)
    
    def test_main_with_verbose_flag(self, valid_config):
        """Test main function with verbose flag."""
        with patch.object(sys, 'argv', ['script.py', valid_config, '-v']):
            exit_code = main()
        
        assert exit_code == 0
    
    def test_main_verbose_long_flag(self, valid_config):
        """Test main function with --verbose flag."""
        with patch.object(sys, 'argv', ['script.py', valid_config, '--verbose']):
            exit_code = main()
        
        assert exit_code == 0
    
    def test_main_with_all_flags(self, valid_config, temp_dir):
        """Test main function with all flags."""
        import os
        custom_output = os.path.join(temp_dir, 'all_flags.gif')
        
        with patch.object(sys, 'argv', ['script.py', valid_config, '-o', custom_output, '-v']):
            exit_code = main()
        
        assert exit_code == 0
        assert os.path.exists(custom_output)
    
    def test_main_keyboard_interrupt(self, valid_config):
        """Test main function handles KeyboardInterrupt."""
        with patch('gif_tools.creator.GifCreator.load_config', side_effect=KeyboardInterrupt):
            with patch.object(sys, 'argv', ['script.py', valid_config]):
                exit_code = main()
        
        assert exit_code == 1
    
    def test_main_unexpected_exception(self, valid_config):
        """Test main function handles unexpected exceptions."""
        with patch('gif_tools.creator.GifCreator.load_config', side_effect=RuntimeError("Unexpected")):
            with patch.object(sys, 'argv', ['script.py', valid_config]):
                exit_code = main()
        
        assert exit_code == 1
    
    def test_main_missing_required_argument(self):
        """Test main function with missing required argument."""
        with patch.object(sys, 'argv', ['script.py']):
            with pytest.raises(SystemExit):
                main()
    
    def test_main_help_flag(self):
        """Test main function with help flag."""
        with patch.object(sys, 'argv', ['script.py', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Help exits with code 0
        assert exc_info.value.code == 0
