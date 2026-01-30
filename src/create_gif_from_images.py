"""CLI script for creating animated GIFs from images based on YAML configuration."""

import argparse
import sys
import logging

from gif_tools import GifCreator, GifCreationError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main entry point for GIF creation CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Create an animated GIF from images based on a YAML config file'
    )
    parser.add_argument('config_path', help='Path to the YAML configuration file')
    parser.add_argument(
        '-o', '--output',
        dest='output_path',
        help='Output path for the GIF (overrides config file setting)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger('gif_tools').setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    try:
        # Create GIF using the library
        creator = GifCreator(args.config_path)
        output_path = creator.create(output_path=args.output_path)
        
        logger.info(f"GIF creation completed successfully")
        logger.info(f"Output: {output_path}")
        return 0
        
    except GifCreationError as e:
        logger.error(f"✗ GIF creation failed: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
