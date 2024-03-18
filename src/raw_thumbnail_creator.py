# nef_thumbnail_creator.py

import rawpy
from PIL import Image, ImageOps
from pathlib import Path
from error_processing import get_file_info, log_error

def create_raw_thumbnail(input_file, output_file_path, thumbnail_size=256):
    try:
        
        # Process NEF file
        with rawpy.imread(input_file) as raw:
            rgb = raw.postprocess()
            
        # Convert the numpy array to a PIL Image object
        image = Image.fromarray(rgb)
        
        # Resize the image and crop it to a square
        image.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
        square_image = ImageOps.fit(image, (thumbnail_size, thumbnail_size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        
        # Save the square thumbnail
        square_image.save(output_file_path, "JPEG")
        # print(f"Raw thumbnail saved to {output_file_path}")

    except Exception as e:
        error_message = f"Error processing file {input_file}: {e}"
        detailed_error_message = get_file_info(input_file, error_message)
        log_error(detailed_error_message)
