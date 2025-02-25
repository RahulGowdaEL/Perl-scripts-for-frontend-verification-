import os
import gzip
import sys

def process_lib_files(libs_file_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    with open(libs_file_path, "r") as libs_file:
        for lib_file_path in libs_file:
            lib_file_path = lib_file_path.strip()

            if not os.path.exists(lib_file_path):
                print(f"Warning: File {lib_file_path} does not exist. Skipping...")
                continue

            base_name = os.path.basename(lib_file_path)
            output_file_path = os.path.join(output_directory, base_name)

            try:
                if lib_file_path.endswith(".gz"):
                    open_file = gzip.open(lib_file_path, "rt")
                else:
                    open_file = open(lib_file_path, "r")

                with open_file as lib_file, open(output_file_path, "w") as output_file:
                    for line in lib_file:
                        if "cell(" in line:
                            output_file.write(line)

                print(f"Processed {lib_file_path} -> {output_file_path}")   #for post processing keep only output_file_path
            except Exception as e:
                print(f"Error processing {lib_file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <libs_file_path> <output_directory>")
        sys.exit(1)

    libs_file_path = sys.argv[1]
    output_directory = sys.argv[2]

    process_lib_files(libs_file_path, output_directory)
