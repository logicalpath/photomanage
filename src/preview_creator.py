import os
import subprocess
import sys
from error_processing import log_error


import os
import subprocess

def create_preview(input_file, output_file, file_extension):
    """
    Creates a video preview using ffmpeg, with error handling.
    Ensures no 0-length files are left.
    """
    # command = [
    #     'ffmpeg', '-i', input_file, '-ss', '00:00:05', '-t', '00:00:10',
    #     '-vf', 'scale=320:-1', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '28', output_file
    # ]

    command = [
    'ffmpeg', '-i', input_file, '-ss', '00:00:05', '-t', '00:00:10',
    '-vf', 'scale=320:-2', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '28', output_file
    ]

    command3gp = [
    'ffmpeg', '-i', input_file, '-ss', '00:00:05', '-t', '00:00:10',
    '-vf', 'scale=320:-2', '-c:v', 'libx264', '-preset', 'veryfast',
    '-crf', '28', '-c:a', 'aac', '-b:a', '128k', output_file
    ]




    try:
        if file_extension == '3gp':
            result = subprocess.run(command3gp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # Check if the file was created and its size is not zero
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"Preview created for {input_file}")
        else:
            # If the file is 0 bytes, log the error and remove the file
            error_message = f"Preview creation resulted in a 0-length file for {input_file}"
            log_error(error_message, "preview-errors.txt")
            os.remove(output_file)
            return False
    except subprocess.CalledProcessError as e:
        error_message = f"Error creating preview for {input_file}: {e.stderr.decode()}"
        log_error(error_message, "preview-errors.txt")
        if os.path.exists(output_file):
            os.remove(output_file)
        return False
    return True

                
def traverse_and_create_previews(root_dir, extensions, thumbnail_dir, max_thumbnails=None):
    """Traverses directories from root_dir and creates thumbnails for images with specified extensions."""
    # Ensure the thumbnail directory exists
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    count = 0
    successes = 0
    errors = 0

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
                output_path = os.path.join(thumbnail_dir + '/' + first_char, 'preview-' + os.path.basename(file))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                if create_preview(input_path, output_path, file_extension):
                    successes += 1
                else:
                    errors += 1    
             
                count += 1  # Increment the counter for each thumbnail created

    print(f"Total successful conversions: {successes}\n")
    print(f"Total errors: {errors}\n")



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_dir> <output_dir> [max_previews]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    max_previews = int(sys.argv[3]) if len(sys.argv) > 3 else None

    extensions = ['mp4', 'mov', 'avi', 'mpg', '3gp', 'm4v']
    # find_and_process_videos(input_dir, output_dir, extensions, max_previews)

    traverse_and_create_previews(input_dir, extensions, output_dir, max_previews)

