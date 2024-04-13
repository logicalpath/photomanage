import os


def convert(value):
    directory, filename = os.path.split(value)
    parent_directory = os.path.basename(directory)
    shortened_path = os.path.join("." + os.sep + parent_directory, filename)
    return shortened_path

