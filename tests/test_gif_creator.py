"""Tests for GifCreator class."""

import os
import pytest
from PIL import Image
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gif_tools import GifCreator, GifCreationError


class TestGifCreatorInit:
    """Tests for GifCreator initialization."""
    
    def test_init_with_valid_path(self, valid_config):
        """Test initialization with a valid config path."""
        creator = GifCreator(valid_config)
        assert creator.config_path == valid_config
        assert creator.config is None
        assert creator.config_dir == ""
        assert creator.images_base_path == ""
        assert creator.image_dict == {}
    
    def test_init_with_nonexistent_path(self):
        """Test initialization with nonexistent path (doesn't fail until load)."""
        creator = GifCreator('/nonexistent/path/config.yml')
        assert creator.config_path == '/nonexistent/path/config.yml'


class TestLoadConfig:
    """Tests for configuration loading."""
    
    def test_load_valid_config(self, valid_config):
        """Test loading a valid configuration file."""
        creator = GifCreator(valid_config)
        config = creator.load_config()
        
        assert config is not None
        assert 'images' in config
        assert 'schedule' in config
        assert len(config['images']) == 3
        assert len(config['schedule']) == 3
        assert creator.config == config
        assert creator.config_dir == os.path.dirname(valid_config)
    
    def test_load_nonexistent_config(self):
        """Test loading a nonexistent configuration file."""
        creator = GifCreator('/nonexistent/config.yml')
        
        with pytest.raises(GifCreationError, match="Configuration file not found"):
            creator.load_config()
    
    def test_load_invalid_yaml(self, invalid_yaml_config):
        """Test loading an invalid YAML file."""
        creator = GifCreator(invalid_yaml_config)
        
        with pytest.raises(GifCreationError, match="Invalid YAML"):
            creator.load_config()
    
    def test_load_empty_config(self, temp_dir):
        """Test loading an empty configuration file."""
        config_path = os.path.join(temp_dir, 'empty.yml')
        with open(config_path, 'w') as f:
            f.write('')
        
        creator = GifCreator(config_path)
        
        with pytest.raises(GifCreationError, match="Configuration file is empty"):
            creator.load_config()
    
    def test_load_config_missing_images(self, missing_images_config):
        """Test loading config without images section."""
        creator = GifCreator(missing_images_config)
        
        with pytest.raises(GifCreationError, match="missing required 'images' section"):
            creator.load_config()
    
    def test_load_config_missing_schedule(self, missing_schedule_config):
        """Test loading config without schedule section."""
        creator = GifCreator(missing_schedule_config)
        
        with pytest.raises(GifCreationError, match="missing required 'schedule' section"):
            creator.load_config()
    
    def test_load_config_empty_images(self, temp_dir):
        """Test loading config with empty images list."""
        config_path = os.path.join(temp_dir, 'empty_images.yml')
        with open(config_path, 'w') as f:
            f.write('images: []\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        
        with pytest.raises(GifCreationError, match="No images defined"):
            creator.load_config()
    
    def test_load_config_empty_schedule(self, temp_dir):
        """Test loading config with empty schedule list."""
        config_path = os.path.join(temp_dir, 'empty_schedule.yml')
        with open(config_path, 'w') as f:
            f.write('images:\n  - key: img1\n    path: test.png\nschedule: []\n')
        
        creator = GifCreator(config_path)
        
        with pytest.raises(GifCreationError, match="No frames scheduled"):
            creator.load_config()


class TestResolveImagesBasePath:
    """Tests for resolving images base path."""
    
    def test_resolve_absolute_path(self, temp_dir, sample_images):
        """Test resolving an absolute path."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: red.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        path = creator.resolve_images_base_path()
        
        assert path == temp_dir
        assert creator.images_base_path == temp_dir
    
    def test_resolve_relative_path(self, temp_dir, sample_images):
        """Test resolving a relative path."""
        # Create subdirectory structure
        config_dir = os.path.join(temp_dir, 'configs')
        os.makedirs(config_dir)
        
        config_path = os.path.join(config_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write('images_base_path: ../\nimages:\n  - key: img1\n    path: red.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        path = creator.resolve_images_base_path()
        
        # Should resolve to temp_dir
        assert os.path.abspath(path) == os.path.abspath(temp_dir)
    
    def test_resolve_default_path(self, temp_dir):
        """Test default images path when not specified."""
        # Create ./images/ directory
        images_dir = os.path.join(temp_dir, 'images')
        os.makedirs(images_dir)
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(os.path.join(images_dir, 'test.png'))
        
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write('images:\n  - key: img1\n    path: test.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        path = creator.resolve_images_base_path()
        
        # Normalize paths for comparison
        assert os.path.normpath(path) == os.path.normpath(images_dir)
    
    def test_resolve_nonexistent_path(self, temp_dir):
        """Test resolving a path that doesn't exist."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write('images_base_path: /nonexistent/path/\nimages:\n  - key: img1\n    path: test.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        
        with pytest.raises(GifCreationError, match="Images directory not found"):
            creator.resolve_images_base_path()
    
    def test_resolve_without_loading_config(self):
        """Test resolving path before loading config."""
        creator = GifCreator('dummy.yml')
        
        with pytest.raises(GifCreationError, match="Configuration not loaded"):
            creator.resolve_images_base_path()


class TestLoadImages:
    """Tests for loading images."""
    
    def test_load_valid_images(self, valid_config):
        """Test loading valid images."""
        creator = GifCreator(valid_config)
        creator.load_config()
        creator.resolve_images_base_path()
        images = creator.load_images()
        
        assert len(images) == 3
        assert 'img1' in images
        assert 'img2' in images
        assert 'img3' in images
        assert isinstance(images['img1'], Image.Image)
        assert images['img1'].size == (100, 100)
    
    def test_load_images_missing_key(self, temp_dir, sample_images):
        """Test loading images when key field is missing."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - path: red.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        
        with pytest.raises(GifCreationError, match="missing required 'key' field"):
            creator.load_images()
    
    def test_load_images_missing_path(self, temp_dir, sample_images):
        """Test loading images when path field is missing."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        
        with pytest.raises(GifCreationError, match="missing required 'path' field"):
            creator.load_images()
    
    def test_load_nonexistent_image(self, temp_dir):
        """Test loading an image that doesn't exist."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: nonexistent.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        
        with pytest.raises(GifCreationError, match="Image file not found"):
            creator.load_images()
    
    def test_load_invalid_image_file(self, temp_dir):
        """Test loading a file that isn't a valid image."""
        # Create a text file instead of an image
        bad_file = os.path.join(temp_dir, 'not_an_image.png')
        with open(bad_file, 'w') as f:
            f.write('This is not an image')
        
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: not_an_image.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        
        with pytest.raises(GifCreationError, match="Error loading image"):
            creator.load_images()
    
    def test_load_images_without_config(self):
        """Test loading images before loading config."""
        creator = GifCreator('dummy.yml')
        
        with pytest.raises(GifCreationError, match="Configuration not loaded"):
            creator.load_images()
    
    def test_load_images_without_base_path(self, valid_config):
        """Test loading images before resolving base path."""
        creator = GifCreator(valid_config)
        creator.load_config()
        
        with pytest.raises(GifCreationError, match="Images base path not resolved"):
            creator.load_images()


class TestBuildFrames:
    """Tests for building frame schedule."""
    
    def test_build_valid_frames(self, valid_config):
        """Test building frames from valid schedule."""
        creator = GifCreator(valid_config)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        frames, durations = creator.build_frames()
        
        assert len(frames) == 3
        assert len(durations) == 3
        assert durations == [500, 300, 200]
        assert all(isinstance(f, Image.Image) for f in frames)
    
    def test_build_frames_default_duration(self, temp_dir, sample_images):
        """Test building frames with default duration."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: red.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        frames, durations = creator.build_frames()
        
        assert len(frames) == 1
        assert durations == [500]  # Default duration
    
    def test_build_frames_missing_image_key(self, temp_dir, sample_images):
        """Test building frames when schedule entry missing image key."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: red.png\nschedule:\n  - time: 500\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        
        with pytest.raises(GifCreationError, match="missing required 'image' field"):
            creator.build_frames()
    
    def test_build_frames_undefined_image(self, temp_dir, sample_images):
        """Test building frames with undefined image reference."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: red.png\nschedule:\n  - image: img2\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        
        with pytest.raises(GifCreationError, match="undefined image key 'img2'"):
            creator.build_frames()
    
    def test_build_frames_invalid_duration(self, temp_dir, sample_images):
        """Test building frames with invalid duration."""
        config_path = os.path.join(temp_dir, 'config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: red.png\nschedule:\n  - image: img1\n    time: -100\n')
        
        creator = GifCreator(config_path)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        
        with pytest.raises(GifCreationError, match="Invalid duration"):
            creator.build_frames()
    
    def test_build_frames_without_images(self, valid_config):
        """Test building frames before loading images."""
        creator = GifCreator(valid_config)
        creator.load_config()
        creator.resolve_images_base_path()
        
        with pytest.raises(GifCreationError, match="Images not loaded"):
            creator.build_frames()


class TestSaveGif:
    """Tests for saving GIF files."""
    
    def test_save_valid_gif(self, temp_dir, valid_config):
        """Test saving a valid GIF."""
        creator = GifCreator(valid_config)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        frames, durations = creator.build_frames()
        
        output_path = os.path.join(temp_dir, 'test_output.gif')
        creator.save_gif(frames, durations, output_path)
        
        assert os.path.exists(output_path)
        # Verify it's a valid GIF
        with Image.open(output_path) as img:
            assert img.format == 'GIF'
            assert img.n_frames == 3
    
    def test_save_gif_creates_directory(self, temp_dir, valid_config):
        """Test that save_gif creates output directory if needed."""
        creator = GifCreator(valid_config)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        frames, durations = creator.build_frames()
        
        output_dir = os.path.join(temp_dir, 'new_dir', 'sub_dir')
        output_path = os.path.join(output_dir, 'output.gif')
        creator.save_gif(frames, durations, output_path)
        
        assert os.path.exists(output_path)
        assert os.path.isdir(output_dir)
    
    def test_save_empty_frames(self, temp_dir):
        """Test saving with empty frames list."""
        creator = GifCreator('dummy.yml')
        output_path = os.path.join(temp_dir, 'output.gif')
        
        with pytest.raises(GifCreationError, match="No frames to create GIF"):
            creator.save_gif([], [], output_path)


class TestCleanup:
    """Tests for resource cleanup."""
    
    def test_cleanup_closes_images(self, valid_config):
        """Test that cleanup closes all images."""
        creator = GifCreator(valid_config)
        creator.load_config()
        creator.resolve_images_base_path()
        creator.load_images()
        
        # Get references to images
        images = list(creator.image_dict.values())
        
        creator.cleanup()
        
        # Images should be closed - check the closed attribute
        for img in images:
            assert img.fp is None or img.fp.closed
        
        # Dictionary should be cleared
        assert len(creator.image_dict) == 0
    
    def test_cleanup_empty_dict(self):
        """Test cleanup with no images loaded."""
        creator = GifCreator('dummy.yml')
        creator.cleanup()  # Should not raise


class TestCreateWorkflow:
    """Tests for the complete create() workflow."""
    
    def test_create_success(self, valid_config, temp_dir):
        """Test successful complete workflow."""
        creator = GifCreator(valid_config)
        output_path = creator.create()
        
        assert os.path.exists(output_path)
        with Image.open(output_path) as img:
            assert img.format == 'GIF'
            assert img.n_frames == 3
    
    def test_create_with_custom_output(self, valid_config, temp_dir):
        """Test create with custom output path."""
        custom_output = os.path.join(temp_dir, 'custom.gif')
        creator = GifCreator(valid_config)
        output_path = creator.create(output_path=custom_output)
        
        assert output_path == custom_output
        assert os.path.exists(custom_output)
    
    def test_create_minimal_config(self, minimal_config):
        """Test create with minimal configuration."""
        creator = GifCreator(minimal_config)
        output_path = creator.create()
        
        assert os.path.exists(output_path)
    
    def test_create_cleanup_on_error(self, temp_dir):
        """Test that cleanup happens even on error."""
        # Create config with nonexistent image
        config_path = os.path.join(temp_dir, 'bad_config.yml')
        with open(config_path, 'w') as f:
            f.write(f'images_base_path: {temp_dir}\nimages:\n  - key: img1\n    path: nonexistent.png\nschedule:\n  - image: img1\n')
        
        creator = GifCreator(config_path)
        
        with pytest.raises(GifCreationError):
            creator.create()
        
        # Cleanup should have been called
        assert len(creator.image_dict) == 0
    
    def test_create_multiple_times(self, valid_config, temp_dir):
        """Test that creator can be reused (though not recommended)."""
        creator = GifCreator(valid_config)
        
        output1 = os.path.join(temp_dir, 'output1.gif')
        result1 = creator.create(output_path=output1)
        assert os.path.exists(result1)
        
        # Second creation (after cleanup from first)
        output2 = os.path.join(temp_dir, 'output2.gif')
        result2 = creator.create(output_path=output2)
        assert os.path.exists(result2)
