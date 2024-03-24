import sys

def compare_files(file1, file2):
    # Open the first file and read its lines into a set for fast lookup
    with open(file1, 'r') as f1:
        file1_names = set(f1.read().splitlines())
    
    # Open the second file and read its lines
    with open(file2, 'r') as f2:
        file2_names = f2.read().splitlines()
    
    # Find the intersection of both sets
    common_files = file1_names.intersection(file2_names)
    
    # Report the results
    if common_files:
        print("Filenames found in both files:")
        for file in common_files:
            print(file)
    else:
        print("No common filenames found.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <file1> <file2>")
    else:
        file1, file2 = sys.argv[1], sys.argv[2]
        compare_files(file1, file2)
