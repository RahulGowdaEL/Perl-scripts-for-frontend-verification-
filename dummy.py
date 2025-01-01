import gzip
import os
import re
import sys

def parse_netlist(netlist_path, output_instances_path):
    instance_pattern = re.compile(r"^\s{4}(\w+)\s+\w+\s*\(")
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
            if lib_path.endswith(".gz"):
                process_file(lib_path, is_gz=True)
            else:
                process_file(lib_path, is_gz=False)

    with open(output_matches_path, "w") as out_file:
        for instance, lib_path in matches:
            out_file.write(f"{instance} found in {lib_path}\n")
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
