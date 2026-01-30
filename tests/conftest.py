"""Test fixtures for gif_tools tests."""

import os
import tempfile
import pytest
from PIL import Image
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_image():
    """Create a simple test image."""
    img = Image.new('RGB', (100, 100), color='red')
    return img


@pytest.fixture
def sample_images(temp_dir):
    """Create a set of sample images for testing."""
    images = {}
    colors = [('red', (255, 0, 0)), ('green', (0, 255, 0)), ('blue', (0, 0, 255))]
    
    for name, color in colors:
        img = Image.new('RGB', (100, 100), color=color)
        img_path = os.path.join(temp_dir, f'{name}.png')
        img.save(img_path)
        images[name] = img_path
    
    return images


@pytest.fixture
def valid_config(temp_dir, sample_images):
    """Create a valid configuration file."""
    config_data = {
        'images_base_path': temp_dir,
        'output_gif_path': os.path.join(temp_dir, 'output.gif'),
        'images': [
            {'key': 'img1', 'path': 'red.png'},
            {'key': 'img2', 'path': 'green.png'},
            {'key': 'img3', 'path': 'blue.png'},
        ],
        'schedule': [
            {'image': 'img1', 'time': 500},
            {'image': 'img2', 'time': 300},
            {'image': 'img3', 'time': 200},
        ]
    }
    
    config_path = os.path.join(temp_dir, 'config.yml')
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    return config_path


@pytest.fixture
def minimal_config(temp_dir, sample_images):
    """Create a minimal valid configuration file."""
    config_data = {
        'images_base_path': temp_dir,
        'images': [
            {'key': 'img1', 'path': 'red.png'},
        ],
        'schedule': [
            {'image': 'img1'},
        ]
    }
    
    config_path = os.path.join(temp_dir, 'minimal_config.yml')
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    return config_path


@pytest.fixture
def invalid_yaml_config(temp_dir):
    """Create an invalid YAML configuration file."""
    config_path = os.path.join(temp_dir, 'invalid.yml')
    with open(config_path, 'w') as f:
        f.write('images:\n  - key: img1\n    path: test.png\n  invalid yaml here:::[')
    
    return config_path


@pytest.fixture
def missing_images_config(temp_dir):
    """Create a config file missing the images section."""
    config_data = {
        'schedule': [
            {'image': 'img1', 'time': 500},
        ]
    }
    
    config_path = os.path.join(temp_dir, 'no_images.yml')
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    return config_path


@pytest.fixture
def missing_schedule_config(temp_dir):
    """Create a config file missing the schedule section."""
    config_data = {
        'images': [
            {'key': 'img1', 'path': 'test.png'},
        ]
    }
    
    config_path = os.path.join(temp_dir, 'no_schedule.yml')
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    return config_path
