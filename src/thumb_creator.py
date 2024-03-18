import sys
import os
import argparse
from raw_thumbnail_creator import create_raw_thumbnail
from thumbnail_creator import create_thumbnail

def non_raw_file(input_file, output_directory):
    create_thumbnail(input_file, output_directory)

def raw_file(input_file, output_directory):
    create_raw_thumbnail(input_file, output_directory)


def traverse_and_create_thumbnails(root_dir, extensions, thumbnail_dir, max_thumbnails=None):
    """Traverses directories from root_dir and creates thumbnails for images with specified extensions."""
    # Ensure the thumbnail directory exists
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if max_thumbnails is not None and count >= max_thumbnails:
                return  # Stop creating thumbnails once the limit is reached
            # if the filename starts with ._ then skip it
            if file.startswith('._'):
                continue
            file_extension = file.split('.')[-1].lower()
            if file_extension in extensions:
                input_path = os.path.join(root, file)
                # grab the first character of the file name
                first_char = file[0] 
                # output_path = os.path.join(thumbnail_dir + '/' + first_char, os.path.basename(file))
                output_path = os.path.join(thumbnail_dir + '/' + first_char, 'thumb-' + os.path.basename(file))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # if the extension is nef, call the raw_file function
                if file_extension == 'nef':
                    raw_file(input_path, output_path)
                else:
                    non_raw_file(input_path, output_path)
                count += 1  # Increment the counter for each thumbnail created



def main():
    parser = argparse.ArgumentParser(description="Create thumbnails for image files.")
    parser.add_argument("input_directory", help="The root directory to search for image files.")
    parser.add_argument("output_directory", help="The directory where thumbnails will be saved.")
    parser.add_argument("-n", "--number", type=int, default=None, help="Maximum number of thumbnails to create. Defaults to creating thumbnails for all images.")

    args = parser.parse_args()

    # Define the list of image file extensions (ensuring uniqueness)
    # image_extensions = list(set(['heic', 'jpg', 'nef', 'png', 'aae', 'jpeg', 'tif', 'tiff']))
    image_extensions = list(set(['heic', 'jpg', 'nef', 'png', 'aae', 'jpeg', 'tif', 'tiff']))


    # Call the function to start creating thumbnails using ImageMagick
    traverse_and_create_thumbnails(args.input_directory, image_extensions, args.output_directory, args.number)

    

if __name__ == "__main__":
    main()
