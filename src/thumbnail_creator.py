# image_thumbnail_creator.py

from PIL import Image

def log_error(message, log_file="non-raw-errors.txt"):
    """
    Logs an error message to a specified log file.

    Args:
    - message: Error message to log.
    - log_file: Path to the log file.
    """
    with open(log_file, "a") as file:
        file.write(message + "\n")

def create_thumbnail(input_image_path, output_image_path, size=(256, 256)):
    """
    Creates a thumbnail of an image with error handling.

    Args:
    - input_image_path: Path to the input image file.
    - output_image_path: Path where the thumbnail will be saved.
    - size: A tuple of (width, height) for the thumbnail size.
    """
    try:
        with Image.open(input_image_path) as img:
            img.thumbnail(size)
            img.save(output_image_path)
        # print(f"Thumbnail saved to {output_image_path}")
    except Exception as e:
        error_message = f"Error creating thumbnail for {input_image_path}: {e}"
        log_error(error_message)
        # print(error_message)
