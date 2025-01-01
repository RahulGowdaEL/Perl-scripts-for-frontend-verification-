if "cell(" in line:
    # Extract content inside parentheses using regex
    match = re.search(r"cell([^)]+)", line)
    if match:
        output_file.write(match.group(1) + "\n")
