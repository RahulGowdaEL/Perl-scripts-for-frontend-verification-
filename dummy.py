OpenAI GPT-4o mini



Hi 
I want a python script where it takes a CSV file and compare the contents with another file

I'll give one log from that the script should grep all the lines having
Dhyan print freq = 440.0000 for the clk dpcc_cbc

So the frequency number and clk can be anything 
It should store in such a way to compare with CSV inputs

In CSV there are freq nodes for particular clks
1st ele will be clk name
From 5th ele frequency range is there, which is defined in first line of the file
So the clk frequency from the log grepped should match anyone of those keeping+or - 1 difference 

avatar
Certainly! Below is a Python script that accomplishes your requirements. It takes a log file and a CSV file, extracts the relevant frequency data from the log, and compares it with frequency ranges defined in the CSV file.

python
Copy
import csv
import re

def read_csv(filename):
    """Read the CSV file and store the frequency ranges in a dictionary."""
    freq_data = {}
    
    with open(filename, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip header line
        
        # Assuming frequency columns start from the 5th element (index 4)
        for row in reader:
            clk_name = row[0]
            freq_ranges = [float(value) for value in row[4:] if value]  # Collect frequencies
            
            if clk_name not in freq_data:
                freq_data[clk_name] = []
            freq_data[clk_name].extend(freq_ranges)
    
    return freq_data

def extract_frequencies_from_log(log_filename):
    """Extract desired frequencies from the log file."""
    freq_pattern = re.compile(r'Dhyan print freq = ([\d.]+) for the clk (.+)')
    frequencies = []
    
    with open(log_filename, 'r') as log_file:
        for line in log_file:
            match = freq_pattern.search(line)
            if match:
                freq = float(match.group(1))
                clk = match.group(2).strip()
                frequencies.append((clk, freq))
    
    return frequencies

def compare_frequencies(frequencies, freq_data):
    """Compare extracted frequencies with those from the CSV."""
    for clk, freq in frequencies:
        if clk in freq_data:
            for range_freq in freq_data[clk]:
                if abs(freq - range_freq) <= 1.0:  # Allow a difference of +/-1
                    print(f"Match found: CLK '{clk}' with Frequency '{freq}' matches range '{range_freq}'.")

def main(log_file, csv_file):
    freq_data = read_csv(csv_file)
    frequencies = extract_frequencies_from_log(log_file)
    compare_frequencies(frequencies, freq_data)

# Example usage:
log_file_path = 'path/to/your/logfile.log'
csv_file_path = 'path/to/your/frequencies.csv'
main(log_file_path, csv_file_path)
