import pandas as pd

def parse_log_file(log_file_path):
    """Parse the log file and extract clock frequency information"""
    clock_data = []
    with open(log_file_path, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        if "clk_name :" in lines[i] and "at the time :" in lines[i]:
            # Extract clock name and timestamp
            parts = lines[i].split(',')
            clk_name = parts[0].split(':')[1].strip()
            time_ns = float(parts[1].split(':')[1].strip().replace('ns', ''))
            
            # Check if next line has frequency
            if i+1 < len(lines) and "having frequency" in lines[i+1]:
                freq = float(lines[i+1].split(':')[2].strip())
                clock_data.append({
                    'clk_name': clk_name,
                    'time_ns': time_ns,
                    'frequency': freq
                })
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    return clock_data

def check_frequency_violations(clock_data, xls_file_path):
    """Check if any clock frequency violates the max frequency from Excel"""
    # Read Excel file
    df = pd.read_excel(xls_file_path)
    
    violations = []
    
    for entry in clock_data:
        clk_name = entry['clk_name']
        freq = entry['frequency']
        time_ns = entry['time_ns']
        
        # Skip 0 frequency (probably clock is off)
        if freq == 0:
            continue
            
        # Find clock in Excel
        clock_row = df[df['Name'] == clk_name]
        if not clock_row.empty:
            # Get the max frequency for all types
            max_freq_columns = [
                'Max LOWSVS', 'Max SVS', 'Max SVS_L1', 'Max NOM',
                'Max TURBO', 'Max TURBO_L1', 'Max TURBO_L3', 'Max TURBO_L4'
            ]
            
            # Get the maximum allowed frequency (max of all max frequencies)
            max_allowed = clock_row[max_freq_columns].max(axis=1).values[0]
            
            if freq > max_allowed:
                violations.append({
                    'clk_name': clk_name,
                    'time_ns': time_ns,
                    'measured_freq': freq,
                    'max_allowed': max_allowed
                })
    
    return violations

def main():
    log_file_path = 'clock_log.txt'  # Replace with your log file path
    xls_file_path = 'clock_frequencies.xlsx'  # Replace with your Excel file path
    
    # Parse log file
    clock_data = parse_log_file(log_file_path)
    
    # Check for violations
    violations = check_frequency_violations(clock_data, xls_file_path)
    
    # Print results
    if not violations:
        print("No clock frequency violations found!")
    else:
        print(f"Found {len(violations)} clock frequency violations:")
        print("-" * 80)
        for i, violation in enumerate(violations, 1):
            print(f"Violation {i}:")
            print(f"Clock: {violation['clk_name']}")
            print(f"Time: {violation['time_ns']} ns")
            print(f"Measured frequency: {violation['measured_freq']} MHz")
            print(f"Maximum allowed: {violation['max_allowed']} MHz")
            print("-" * 80)

if __name__ == "__main__":
    main()
