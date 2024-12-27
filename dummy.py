def remove_duplicates(input_file, output_file):
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
