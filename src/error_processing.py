# error_processing.py
import subprocess

def get_file_info(input_path, error_message):
    """
    Runs the 'file' command on the input path and appends its output to the error message.

    Args:
    - input_path: Path to the input file.
    - error_message: Basic error message to append detailed file info to.

    Returns:
    - A detailed error message including file type information.
    """
    try:
        result = subprocess.run(["file", input_path], capture_output=True, text=True)
        file_type_info = result.stdout.strip()
        return f"{error_message}\nFile type info: {file_type_info}"
    except subprocess.CalledProcessError as e:
        return f"{error_message}\nFailed to obtain file type info: {e}"

def log_error(message, log_file="thumb-errors.txt"):
    """
    Logs an error message to a specified log file.

    Args:
    - message: Error message to log.
    - log_file: Path to the log file.
    """
    with open(log_file, "a") as file:
        file.write(message + "\n")
