# image_thumbnail_creator.py

from PIL import Image
from error_processing import get_file_info, log_error


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
        detailed_error_message = get_file_info(input_image_path, error_message)
        log_error(detailed_error_message)
        
