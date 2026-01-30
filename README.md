<!-- Repository Name--->
# gif-tools

<!-- Short Repository Description--->
I got tired of having to use confusing tools to make or edit gifs so I have created this repository to store some Python scripts I write to manipulate gifs myself.



# Create GIFs from Images

Creates animated GIFs from PNG/JPG images using a YAML config file.

<p align="center">
  <figure align="center">
    <img src="example.gif" alt="Example GIF output" width="30%">
    <figcaption>Example GIF created from the example_config.yml</figcaption>
  </figure>
</p>

## Usage

```bash
python src/create_gif_from_images.py config.yml
```

Optional flags:
- `-o, --output` - Override output path from config
- `-v, --verbose` - Show detailed logging

## Config File Format

```yaml
# Base path for images (absolute or relative to config file)
images_base_path: ./images/

# Output GIF path (absolute or relative to config file)
output_gif_path: output.gif

# Define your images
images:
  - key: frame1
    path: image1.png
  - key: frame2
    path: image2.png

# Set the schedule (time in milliseconds)
schedule:
  - image: frame1
    time: 500
  - image: frame2
    time: 500
  - image: frame1  # You can reuse images
    time: 300
```

See [example_config.yml](example_config.yml) for a working example.


## Testing

### Installation

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=src --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_some_module.py
```

Run with verbose output:
```bash
pytest -v
```