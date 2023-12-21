import pandas as pd
import sys
import os

def process_csv(input_file_path, output_file_path):
    df = pd.read_csv(input_file_path)
    df['Directory'] = df['SourceFile'].apply(lambda x: '/'.join(x.split('/')[:-1]))
    df['Filename'] = df['SourceFile'].apply(lambda x: x.split('/')[-1])
    # df_output = df.drop('SourceFile', axis=1)
    df_reordered = df_output[['Directory', 'Filename', 'CreateDate', 'GPSLatitude', 'GPSLongitude']]
    df_reordered = df_output[['Directory', 'Filename', 'CreateDate']]

    df_reordered.to_csv(output_file_path, index=False)
    print(f"CSV file saved to {output_file_path}")

def main():
    # Check if the input file name is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    # Construct the output file name
    base_name, file_extension = os.path.splitext(input_file)
    output_file = base_name + 'output' + file_extension

    # Process the CSV file
    process_csv(input_file, output_file)

if __name__ == "__main__":
    main()
