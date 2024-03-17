import os
import subprocess
import argparse

def log_file_type_and_error(input_path, error_message, error_log_path="error_log.txt"):
    """Logs the file type and ImageMagick conversion error."""
    try:
        # Running the 'file' command and capturing the output
        result = subprocess.run(["file", input_path], capture_output=True, text=True)
        file_type_info = result.stdout.strip()

        # Preparing the log entry
        log_entry = f"Conversion error for {input_path}:\nImageMagick error: {error_message}\nFile type: {file_type_info}\n\n"

        # Writing to the log file
        with open(error_log_path, "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        # If capturing file type fails, log the error
        with open(error_log_path, "a") as log_file:
            log_file.write(f"Failed to log file type for {input_path}. Error: {e}\n")

def create_thumbnail_with_imagemagick(input_path, output_path, size="128x128", error_log_path="error_log.txt"):
    """Creates a thumbnail of the image at input_path using ImageMagick."""
    try:
        subprocess.run(["convert", input_path, "-resize", size, output_path], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # Log both the ImageMagick error and the file type
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        log_file_type_and_error(input_path, error_message, error_log_path)

def traverse_and_create_thumbnails_with_imagemagick(root_dir, extensions, thumbnail_dir, max_thumbnails=None, error_log_path="error_log.txt"):
    """Traverses directories from root_dir and creates thumbnails for images with specified extensions using ImageMagick."""
    # Ensure the thumbnail directory exists
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if max_thumbnails is not None and count >= max_thumbnails:
                return  # Stop creating thumbnails once the limit is reached
            if file.split('.')[-1].lower() in extensions:
                input_path = os.path.join(root, file)
                # grab the first character of the file name
                first_char = file[0] 
                output_path = os.path.join(thumbnail_dir + '/' + first_char, os.path.basename(file))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                create_thumbnail_with_imagemagick(input_path, output_path, error_log_path=error_log_path)
                count += 1  # Increment the counter for each thumbnail created

def main():
    parser = argparse.ArgumentParser(description="Create thumbnails for image files using ImageMagick.")
    parser.add_argument("input_directory", help="The root directory to search for image files.")
    parser.add_argument("output_directory", help="The directory where thumbnails will be saved.")
    parser.add_argument("-n", "--number", type=int, default=None, help="Maximum number of thumbnails to create. Defaults to creating thumbnails for all images.")
    parser.add_argument("--error-log", default="error_log.txt", help="Path to the error log file.")

    args = parser.parse_args()

    # Define the list of image file extensions (ensuring uniqueness)
    # image_extensions = list(set(['heic', 'jpg', 'nef', 'png', 'aae', 'jpeg', 'tif', 'tiff']))
    image_extensions = list(set(['heic', 'jpg', 'png', 'aae', 'jpeg', 'tif', 'tiff']))


    # Call the function to start creating thumbnails using ImageMagick
    traverse_and_create_thumbnails_with_imagemagick(args.input_directory, image_extensions, args.output_directory, args.number, args.error_log)

if __name__ == "__main__":
    main()
