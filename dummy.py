import os
import gzip
import sys

def process_lib_files(libs_file_path, output_directory):
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Read the libs file containing paths to files
    with open(libs_file_path, "r") as libs_file:
        for lib_file_path in libs_file:
            lib_file_path = lib_file_path.strip()

            # Skip if the file does not exist
            if not os.path.exists(lib_file_path):
                print(f"Warning: File {lib_file_path} does not exist. Skipping...")
                continue

            # Extract the base name of the file for the output
            base_name = os.path.basename(lib_file_path)
            output_file_path = os.path.join(output_directory, base_name)

            # Open and process the file (handles both .gz and uncompressed files)
            try:
                if lib_file_path.endswith(".gz"):
                    open_file = gzip.open(lib_file_path, "rt")
                else:
                    open_file = open(lib_file_path, "r")

                with open_file as lib_file, open(output_file_path, "w") as output_file:
                    for line in lib_file:
                        if "cell(" in line:
                            output_file.write(line)

                print(f"Processed {lib_file_path} -> {output_file_path}")
            except Exception as e:
                print(f"Error processing {lib_file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <libs_file_path> <output_directory>")
        sys.exit(1)

    libs_file_path = sys.argv[1]
    output_directory = sys.argv[2]

    process_lib_files(libs_file_path, output_directory)def remove_duplicates(input_file, output_file):
    try:
        # Read the file and store unique lines
        with open(input_file, 'r') as infile:
            unique_lines = set(infile.readlines())
        
        # Write unique lines to the output file
        with open(output_file, 'w') as outfile:
            outfile.writelines(sorted(unique_lines))
        
        print(f"Duplicate removal complete. Output written to {output_file}.")
    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Define input and output file paths
input_file = "input.txt"  # Replace with your input file path
output_file = "output.txt"  # Replace with your desired output file path

# Call the function
remove_duplicates(input_file, output_file)
