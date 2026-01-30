"""Core GIF creation functionality."""

from PIL import Image
import os
import yaml
import logging
from typing import Dict, List, Tuple, Optional

from .exceptions import GifCreationError

logger = logging.getLogger(__name__)


class GifCreator:
    """
    Creates animated GIFs from images based on YAML configuration.
    
    Attributes:
        config_path: Path to the YAML configuration file
        config: Loaded configuration dictionary
        config_dir: Directory containing the config file
        images_base_path: Resolved path to images directory
        image_dict: Dictionary of loaded PIL Image objects
    """
    
    def __init__(self, config_path: str):
        """
        Initialize GIF creator with configuration file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Raises:
            GifCreationError: If config file cannot be loaded
        """
        self.config_path = config_path
        self.config: Optional[dict] = None
        self.config_dir: str = ""
        self.images_base_path: str = ""
        self.image_dict: Dict[str, Image.Image] = {}
        
    def load_config(self) -> dict:
        """
        Load and validate YAML configuration file.
        
        Returns:
            Parsed configuration dictionary
            
        Raises:
            GifCreationError: If config file cannot be loaded or is invalid
        """
        logger.info(f"Loading configuration from: {self.config_path}")
        
        if not os.path.exists(self.config_path):
            raise GifCreationError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise GifCreationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise GifCreationError(f"Error reading config file: {e}")
        
        # Validate required keys
        if not config:
            raise GifCreationError("Configuration file is empty")
        
        if 'images' not in config:
            raise GifCreationError("Configuration missing required 'images' section")
        
        if 'schedule' not in config:
            raise GifCreationError("Configuration missing required 'schedule' section")
        
        if not config['images']:
            raise GifCreationError("No images defined in configuration")
        
        if not config['schedule']:
            raise GifCreationError("No frames scheduled in configuration")
        
        logger.info(f"Configuration loaded successfully: {len(config['images'])} images, {len(config['schedule'])} frames")
        self.config = config
        self.config_dir = os.path.dirname(os.path.abspath(self.config_path))
        return config
    
    def resolve_images_base_path(self) -> str:
        """
        Resolve the base path for images from configuration.
        
        Returns:
            Absolute path to images directory
            
        Raises:
            GifCreationError: If images directory doesn't exist
        """
        if not self.config:
            raise GifCreationError("Configuration not loaded. Call load_config() first.")
        
        images_base_path = self.config.get('images_base_path', './images/')
        
        # Make path absolute if it's relative
        if not os.path.isabs(images_base_path):
            images_base_path = os.path.join(self.config_dir, images_base_path)
        
        if not os.path.exists(images_base_path):
            raise GifCreationError(f"Images directory not found: {images_base_path}")
        
        logger.info(f"Using images base path: {images_base_path}")
        self.images_base_path = images_base_path
        return images_base_path
    
    def load_images(self) -> Dict[str, Image.Image]:
        """
        Load all images defined in configuration.
        
        Returns:
            Dictionary mapping image keys to PIL Image objects
            
        Raises:
            GifCreationError: If any image cannot be loaded
        """
        if not self.config:
            raise GifCreationError("Configuration not loaded. Call load_config() first.")
        
        if not self.images_base_path:
            raise GifCreationError("Images base path not resolved. Call resolve_images_base_path() first.")
        
        logger.info("Loading images...")
        image_dict = {}
        
        for idx, image_definition in enumerate(self.config['images']):
            if 'key' not in image_definition:
                raise GifCreationError(f"Image definition {idx} missing required 'key' field")
            
            if 'path' not in image_definition:
                raise GifCreationError(f"Image definition '{image_definition['key']}' missing required 'path' field")
            
            key = image_definition['key']
            image_path = os.path.join(self.images_base_path, image_definition['path'])
            
            if not os.path.exists(image_path):
                raise GifCreationError(f"Image file not found: {image_path}")
            
            try:
                logger.debug(f"Loading image '{key}' from {image_path}")
                image_dict[key] = Image.open(image_path)
            except Exception as e:
                raise GifCreationError(f"Error loading image '{key}' from {image_path}: {e}")
        
        logger.info(f"Successfully loaded {len(image_dict)} images")
        self.image_dict = image_dict
        return image_dict
    
    def build_frames(self) -> Tuple[List[Image.Image], List[int]]:
        """
        Build frame list and durations from schedule configuration.
        
        Returns:
            Tuple of (frames list, durations list)
            
        Raises:
            GifCreationError: If schedule references undefined images
        """
        if not self.config:
            raise GifCreationError("Configuration not loaded. Call load_config() first.")
        
        if not self.image_dict:
            raise GifCreationError("Images not loaded. Call load_images() first.")
        
        logger.info("Building frame schedule...")
        frames = []
        durations = []
        
        for idx, scheduled_frame in enumerate(self.config['schedule']):
            if 'image' not in scheduled_frame:
                raise GifCreationError(f"Schedule entry {idx} missing required 'image' field")
            
            key = scheduled_frame['image']
            
            if key not in self.image_dict:
                raise GifCreationError(
                    f"Schedule references undefined image key '{key}'. "
                    f"Available keys: {', '.join(self.image_dict.keys())}"
                )
            
            duration = scheduled_frame.get('time', 500)
            
            if not isinstance(duration, int) or duration <= 0:
                raise GifCreationError(f"Invalid duration for frame {idx}: {duration}. Must be a positive integer.")
            
            image = self.image_dict[key]
            frames.append(image)
            durations.append(duration)
        
        logger.info(f"Built {len(frames)} frames with total duration {sum(durations)}ms")
        return frames, durations
    
    def save_gif(self, frames: List[Image.Image], durations: List[int], output_path: str) -> None:
        """
        Create and save animated GIF from frames.
        
        Args:
            frames: List of PIL Image objects
            durations: List of frame durations in milliseconds
            output_path: Path where GIF should be saved
            
        Raises:
            GifCreationError: If GIF cannot be created
        """
        if not frames:
            raise GifCreationError("No frames to create GIF")
        
        logger.info(f"Creating GIF: {output_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            except Exception as e:
                raise GifCreationError(f"Error creating output directory: {e}")
        
        try:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,  # Loop forever
                disposal=2  # Replace each frame instead of stacking (fixes transparency issues)
            )
            logger.info(f"GIF created successfully: {output_path}")
        except Exception as e:
            raise GifCreationError(f"Error saving GIF: {e}")
    
    def cleanup(self) -> None:
        """Close all opened images to free resources."""
        logger.debug("Cleaning up image resources...")
        for key, image in self.image_dict.items():
            try:
                image.close()
            except Exception as e:
                logger.warning(f"Error closing image '{key}': {e}")
        self.image_dict.clear()
    
    def create(self, output_path: Optional[str] = None) -> str:
        """
        Complete workflow: load config, load images, and create GIF.
        
        Args:
            output_path: Optional output path override. If not provided,
                        uses path from config or defaults to 'example.gif'
                        
        Returns:
            Path to the created GIF file
            
        Raises:
            GifCreationError: If any step of the process fails
        """
        try:
            # Load and validate configuration
            self.load_config()
            
            # Resolve paths
            self.resolve_images_base_path()
            
            # Determine output path
            if output_path is None:
                output_path = self.config.get('output_gif_path', 'example.gif')
                if not os.path.isabs(output_path):
                    output_path = os.path.join(self.config_dir, output_path)
            
            # Load images
            self.load_images()
            
            # Build frame schedule
            frames, durations = self.build_frames()
            
            # Create GIF
            self.save_gif(frames, durations, output_path)
            
            return output_path
            
        finally:
            # Always cleanup resources
            self.cleanup()
