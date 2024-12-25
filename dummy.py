instance_pattern = re.compile(r"^\s+([a-zA-Z0-9_]+)\s+\w+\s*\(")
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.auto_filter import AutoFilter

# Input and output file paths
input_csv = "input.csv"  # Replace with your CSV file path
output_xls = "output.xls"  # Replace with your desired XLS file path

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(input_csv)

# Save the DataFrame to an Excel file (xlsx format temporarily for filters)
temp_xlsx = output_xls.replace('.xls', '.xlsx')
df.to_excel(temp_xlsx, index=False)

# Add filters to the Excel file
workbook = load_workbook(temp_xlsx)
sheet = workbook.active
sheet.auto_filter.ref = sheet.dimensions  # Apply filters to all columns

# Save as .xls format (optional, .xlsx is recommended for compatibility)
workbook.save(temp_xlsx)
workbook.close()
