import os

def convert(value):
    # Get the directory name and file name from the file path
    directory, filename = os.path.split(value)
    
    # Check if the file name starts with 'thumb-'
    if filename.startswith('thumb-'):
        # Remove 'thumb-' from the file name
        new_filename = filename[6:]
        
        # Construct the new file path
        new_value = os.path.join(directory, new_filename)
        
        return new_value
    
    # If the file name doesn't start with 'thumb-', return the original file path
    return value

