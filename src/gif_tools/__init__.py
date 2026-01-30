"""GIF creation tools for building animated GIFs from images."""

from .creator import GifCreator
from .exceptions import GifCreationError

__all__ = ['GifCreator', 'GifCreationError']
__version__ = '1.0.0'
