"""Integration tests for end-to-end workflows."""

import os
import pytest
from PIL import Image
import yaml
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gif_tools import GifCreator, GifCreationError


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Integration tests for complete workflows."""
    
    def test_complete_workflow_with_transparency(self, temp_dir):
        """Test complete workflow with transparent images."""
        # Create transparent images
        img1 = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        img2 = Image.new('RGBA', (100, 100), (0, 255, 0, 128))
        
        img1.save(os.path.join(temp_dir, 'trans1.png'))
        img2.save(os.path.join(temp_dir, 'trans2.png'))
        
        # Create config
        config_path = os.path.join(temp_dir, 'config.yml')
        config_data = {
            'images_base_path': temp_dir,
            'output_gif_path': os.path.join(temp_dir, 'transparent.gif'),
            'images': [
                {'key': 'img1', 'path': 'trans1.png'},
                {'key': 'img2', 'path': 'trans2.png'},
            ],
            'schedule': [
                {'image': 'img1', 'time': 300},
                {'image': 'img2', 'time': 300},
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Create GIF
        creator = GifCreator(config_path)
        output = creator.create()
        
        assert os.path.exists(output)
        with Image.open(output) as gif:
            assert gif.format == 'GIF'
            assert gif.n_frames == 2
    
    def test_workflow_with_different_sized_images(self, temp_dir):
        """Test workflow with images of different sizes."""
        # Create images of different sizes
        img1 = Image.new('RGB', (100, 100), 'red')
        img2 = Image.new('RGB', (200, 150), 'green')
        img3 = Image.new('RGB', (50, 200), 'blue')
        
        img1.save(os.path.join(temp_dir, 'small.png'))
        img2.save(os.path.join(temp_dir, 'medium.png'))
        img3.save(os.path.join(temp_dir, 'tall.png'))
        
        # Create config
        config_path = os.path.join(temp_dir, 'config.yml')
        config_data = {
            'images_base_path': temp_dir,
            'output_gif_path': os.path.join(temp_dir, 'mixed_sizes.gif'),
            'images': [
                {'key': 'small', 'path': 'small.png'},
                {'key': 'medium', 'path': 'medium.png'},
                {'key': 'tall', 'path': 'tall.png'},
            ],
            'schedule': [
                {'image': 'small', 'time': 200},
                {'image': 'medium', 'time': 200},
                {'image': 'tall', 'time': 200},
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Create GIF
        creator = GifCreator(config_path)
        output = creator.create()
        
        assert os.path.exists(output)
        with Image.open(output) as gif:
            assert gif.format == 'GIF'
    
    def test_workflow_with_repeated_frames(self, temp_dir):
        """Test workflow with same image repeated in schedule."""
        # Create one image
        img = Image.new('RGB', (100, 100), 'purple')
        img.save(os.path.join(temp_dir, 'single.png'))
        
        # Create config with repeated schedule
        config_path = os.path.join(temp_dir, 'config.yml')
        config_data = {
            'images_base_path': temp_dir,
            'output_gif_path': os.path.join(temp_dir, 'repeated.gif'),
            'images': [
                {'key': 'img', 'path': 'single.png'},
            ],
            'schedule': [
                {'image': 'img', 'time': 100},
                {'image': 'img', 'time': 200},
                {'image': 'img', 'time': 300},
                {'image': 'img', 'time': 400},
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Create GIF
        creator = GifCreator(config_path)
        output = creator.create()
        
        assert os.path.exists(output)
        with Image.open(output) as gif:
            assert gif.format == 'GIF'
            # Note: PIL may optimize identical consecutive frames, so we just verify
            # the GIF was created successfully rather than checking frame count
            assert gif.n_frames >= 1
    
    def test_workflow_with_nested_directories(self, temp_dir):
        """Test workflow with images in nested directories."""
        # Create nested directory structure
        img_dir = os.path.join(temp_dir, 'assets', 'images')
        os.makedirs(img_dir)
        
        # Create image
        img = Image.new('RGB', (100, 100), 'orange')
        img.save(os.path.join(img_dir, 'nested.png'))
        
        # Create config in different location
        config_dir = os.path.join(temp_dir, 'configs')
        os.makedirs(config_dir)
        
        config_path = os.path.join(config_dir, 'config.yml')
        config_data = {
            'images_base_path': img_dir,
            'output_gif_path': os.path.join(temp_dir, 'output', 'nested.gif'),
            'images': [
                {'key': 'img', 'path': 'nested.png'},
            ],
            'schedule': [
                {'image': 'img', 'time': 500},
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Create GIF
        creator = GifCreator(config_path)
        output = creator.create()
        
        assert os.path.exists(output)
        assert os.path.exists(os.path.join(temp_dir, 'output'))
    
    def test_workflow_large_number_of_frames(self, temp_dir):
        """Test workflow with many frames."""
        # Create several images
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan']
        
        for i, color in enumerate(colors):
            img = Image.new('RGB', (50, 50), color)
            img.save(os.path.join(temp_dir, f'img{i}.png'))
        
        # Create config with many schedule entries
        config_path = os.path.join(temp_dir, 'config.yml')
        images_list = [{'key': f'img{i}', 'path': f'img{i}.png'} for i in range(len(colors))]
        schedule = [{'image': f'img{i % len(colors)}', 'time': 100} for i in range(50)]
        
        config_data = {
            'images_base_path': temp_dir,
            'output_gif_path': os.path.join(temp_dir, 'large.gif'),
            'images': images_list,
            'schedule': schedule
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Create GIF
        creator = GifCreator(config_path)
        output = creator.create()
        
        assert os.path.exists(output)
        with Image.open(output) as gif:
            assert gif.format == 'GIF'
            assert gif.n_frames == 50
    
    def test_workflow_with_relative_paths(self, temp_dir):
        """Test workflow using relative paths throughout."""
        # Create images directory
        images_dir = os.path.join(temp_dir, 'images')
        os.makedirs(images_dir)
        
        # Create image
        img = Image.new('RGB', (100, 100), 'teal')
        img.save(os.path.join(images_dir, 'relative.png'))
        
        # Create config with relative paths
        config_path = os.path.join(temp_dir, 'config.yml')
        config_data = {
            'images_base_path': './images/',
            'output_gif_path': './output_relative.gif',
            'images': [
                {'key': 'img', 'path': 'relative.png'},
            ],
            'schedule': [
                {'image': 'img', 'time': 500},
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Create GIF
        creator = GifCreator(config_path)
        output = creator.create()
        
        assert os.path.exists(output)
        # Output should be relative to config directory
        assert output.startswith(temp_dir)
