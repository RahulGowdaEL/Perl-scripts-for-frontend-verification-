#!/usr/bin/perl
use strict;
use warnings;

my $input_file     = 'hm_dch_tile_top.v';       
my $exclusion_file = 'port_name_1'; 
my $output_file    = "processed_output.v";

# Load exclusion signals
open my $excl_fh, '<', $exclusion_file or die "Could not open exclusion file '$exclusion_file': $!\n";
my %exclusion_signals;
while (my $line = <$excl_fh>) {
    chomp $line;
    $exclusion_signals{$line} = 1;
}
close $excl_fh;

# Process the input file
open my $in_fh,  '<', $input_file  or die "Could not open input file '$input_file': $!\n";
open my $out_fh, '>', $output_file or die "Could not open output file '$output_file': $!\n";

while (my $line = <$in_fh>) {
    # Preserve lines with leading spaces and matching `.\\signal_name[*]`
    if ($line =~ /^\s*\.\\(\w+)\[\d+\]/) {
        my $signal = $1;
        if (exists $exclusion_signals{$signal}) {
            print $out_fh $line;
            next;
        }
    }

    # Remove backslash for exclusion signals in signal lists
    foreach my $signal (keys %exclusion_signals) {
        # Case 1: Match `.\\signal_name[*]`
        $line =~ s/\\($signal\[\d+\])/$1/g;
        
        # Case 2: Match `(\ \signal_name[*])` inside parentheses
        $line =~ s/\( \\\($signal\[\d+\]\)/\( $1\)/g;
    }

    print $out_fh $line;
}

close $in_fh;
close $out_fh;

print "Processing complete. Output written to '$output_file'.\n";

import gzip
import os
import re
import sys

def parse_netlist(file_path):
    """Parses a single netlist file to extract instances."""
    instance_pattern = re.compile(r"^\s{3}(\w+)\s+\w+\s*\(")
    in_module_block = False
    instances = set()

    with open(file_path, "r") as netlist_file:
        for line in netlist_file:
            if "// Module instantiation" in line:
                in_module_block = True
            elif "endmodule" in line:
                in_module_block = False
            elif in_module_block:
                match = instance_pattern.match(line)
                if match:
                    instances.add(match.group(1))

    return instances

def process_netlist_directory(input_dir, output_instances_path):
    """Processes all netlist files in a directory to extract instances."""
    all_instances = set()

    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                print(f"Processing netlist file: {file_path}")
                instances = parse_netlist(file_path)
                all_instances.update(instances)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    # Write all instances (with duplicates removed) to the output file
    with open(output_instances_path, "w") as out_file:
        out_file.write("\n".join(sorted(all_instances)))
    print(f"Extracted {len(all_instances)} unique instances to {output_instances_path}")
    return all_instances

def is_gzip_file(file_path):
    """Checks if the file is a valid gzip file."""
    try:
        with gzip.open(file_path, "rb") as f:
            f.read(1)
        return True
    except OSError:
        return False

def find_instances_in_libs(instances, libs_file_path, output_matches_path):
    """Finds instances in library files."""
    matches = []

    def process_file(file_path, is_gz=False):
        try:
            with (gzip.open(file_path, "rt") if is_gz else open(file_path, "r")) as file:
                for line in file:
                    for instance in instances:
                        if instance in line:
                            matches.append((instance, file_path))
                            break
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    with open(libs_file_path, "r") as libs_file:
        for lib_path in libs_file:
            lib_path = lib_path.strip()
            if os.path.exists(lib_path):
                if lib_path.endswith(".gz") and is_gzip_file(lib_path):
                    process_file(lib_path, is_gz=True)
                else:
                    process_file(lib_path, is_gz=False)
            else:
                print(f"File not found: {lib_path}")

    with open(output_matches_path, "w") as out_file:
        for instance, lib_path in matches:
            out_file.write(f"{instance} ----> {lib_path}\n")
    print(f"Found {len(matches)} matches. Results written to {output_matches_path}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py <netlist_dir> <libs_file_path> <output_dir>")
        sys.exit(1)

    netlist_dir = sys.argv[1]
    libs_file_path = sys.argv[2]
    output_dir = sys.argv[3]

    os.makedirs(output_dir, exist_ok=True)

    instances_output_path = os.path.join(output_dir, "instances.txt")
    unique_instances_output_path = os.path.join(output_dir, "instances_without_dup.txt")
    matches_output_path = os.path.join(output_dir, "matches.txt")

    # Process all files in the netlist directory
    all_instances = process_netlist_directory(netlist_dir, instances_output_path)

    # Remove duplicates and write to a separate file
    with open(unique_instances_output_path, "w") as out_file:
        out_file.write("\n".join(sorted(all_instances)))
    print(f"Removed duplicates. Unique instances written to {unique_instances_output_path}")

    # Use unique instances for library file search
    find_instances_in_libs(all_instances, libs_file_path, matches_output_path)

if __name__ == "__main__":
    main()




import gzip
import os
import re
import sys

def parse_netlist(netlist_path, output_instances_path):
    instance_pattern = re.compile(r"^\s{3}(\w+)\s+\w+\s*\(")
    in_module_block = False
    instances = set()

    with open(netlist_path, "r") as netlist_file:
        for line in netlist_file:
            if "// Module instantiation" in line:
                in_module_block = True
            elif "endmodule" in line:
                in_module_block = False
            elif in_module_block:
                match = instance_pattern.match(line)
                if match:
                    instances.add(match.group(1))

    with open(output_instances_path, "w") as out_file:
        out_file.write("\n".join(sorted(instances)))
    print(f"Extracted {len(instances)} instances to {output_instances_path}")
    return instances

def is_gzip_file(file_path):
    """Checks if the file is a valid gzip file."""
    try:
        with gzip.open(file_path, "rb") as f:
            f.read(1)
        return True
    except OSError:
        return False

def find_instances_in_libs(instances, libs_file_path, output_matches_path):
    matches = []

    def process_file(file_path, is_gz=False):
        try:
            with (gzip.open(file_path, "rt") if is_gz else open(file_path, "r")) as file:
                for line in file:
                    for instance in instances:
                        if instance in line:
                            matches.append((instance, file_path))
                            break
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    with open(libs_file_path, "r") as libs_file:
        for lib_path in libs_file:
            lib_path = lib_path.strip()
            if os.path.exists(lib_path):
                if lib_path.endswith(".gz") and is_gzip_file(lib_path):
                    process_file(lib_path, is_gz=True)
                else:
                    process_file(lib_path, is_gz=False)
            else:
                print(f"File not found: {lib_path}")

    with open(output_matches_path, "w") as out_file:
        for instance, lib_path in matches:
            out_file.write(f"{instance} ----> {lib_path}\n")
    print(f"Found {len(matches)} matches. Results written to {output_matches_path}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py <netlist_path> <libs_file_path> <output_dir>")
        sys.exit(1)

    netlist_path = sys.argv[1]
    libs_file_path = sys.argv[2]
    output_dir = sys.argv[3]

    os.makedirs(output_dir, exist_ok=True)

    instances_output_path = os.path.join(output_dir, "instances.txt")
    matches_output_path = os.path.join(output_dir, "matches.txt")

    instances = parse_netlist(netlist_path, instances_output_path)
    find_instances_in_libs(instances, libs_file_path, matches_output_path)

if __name__ == "__main__":
    main()
