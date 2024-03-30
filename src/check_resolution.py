import argparse
import subprocess
import os

def check_video_properties(input_directory, output_file):
    extensions = ['mp4', 'mov', 'avi', 'mpg', '3gp', 'm4v']  # Updated extensions list
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(input_directory):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    file_path = os.path.join(root, file)
                    command = [
                        'ffprobe', 
                        '-v', 'error', 
                        '-select_streams', 'v:0', 
                        '-show_entries', 'stream=width,height', 
                        '-of', 'default=noprint_wrappers=1', 
                        file_path
                    ]
                    
                    try:
                        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
                        f.write(f'File: {file_path}\n{output}\n')
                    except subprocess.CalledProcessError as e:
                        f.write(f'Error processing file: {file_path}\n{e.output}\n')

def main():
    parser = argparse.ArgumentParser(description='Check video properties in a directory and sub-directories')
    parser.add_argument('input_directory', type=str, help='Path to the input directory')
    parser.add_argument('output_file', type=str, help='Path to the output file')

    args = parser.parse_args()

    check_video_properties(args.input_directory, args.output_file)
    print(f'Results written to {args.output_file}')

if __name__ == '__main__':
    main()
