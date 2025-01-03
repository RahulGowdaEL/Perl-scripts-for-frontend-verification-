#!/bin/bash

# Define file paths
input_file="input_file.v"
exclusion_file="exclusions.txt"
output_file="processed_output.v"

# Create a temporary file to hold processed lines
temp_file=$(mktemp)

# Read exclusion file and store the signal names in an array
declare -a exclusion_signals
while IFS= read -r signal; do
    exclusion_signals+=("$signal")
done < "$exclusion_file"

# Process the input file
while IFS= read -r line; do
    # Check if the line contains any of the exclusion signals
    modified_line="$line"
    for signal in "${exclusion_signals[@]}"; do
        # Check if the line contains the signal and is not prefixed with .\
        if [[ "$line" =~ \\$signal && ! "$line" =~ \\.\$signal ]]; then
            # Remove the backslash from the signal if it's found
            modified_line=$(echo "$modified_line" | sed "s/\\$signal/$signal/g")
        fi
    done
    # Write the modified or original line to the temp file
    echo "$modified_line" >> "$temp_file"
done < "$input_file"

# Move the processed temp file to the final output file
mv "$temp_file" "$output_file"

echo "Processing complete. Output written to $output_file."
