use strict;
use warnings;
use Text::CSV;
use Spreadsheet::WriteExcel;

# Input and output file paths
my $input_csv  = "input.csv";  # Replace with your CSV file path
my $output_xls = "output.xls"; # Replace with your desired XLS file path

# Open the CSV file
open my $csv_fh, '<', $input_csv or die "Cannot open $input_csv: $!";

# Create a new Excel workbook
my $workbook  = Spreadsheet::WriteExcel->new($output_xls);
my $worksheet = $workbook->add_worksheet();

# Parse the CSV file
my $csv = Text::CSV->new({ binary => 1, auto_diag => 1 });
my $row_num = 0;

while (my $row = $csv->getline($csv_fh)) {
    my $col_num = 0;
    foreach my $cell (@$row) {
        $worksheet->write($row_num, $col_num++, $cell);
    }
    $row_num++;
}

# Apply autofilter to all columns
my $last_col = $worksheet->dim_colmax();  # Get the last column index
$worksheet->autofilter(0, 0, $row_num - 1, $last_col);

# Close the file handles
close $csv_fh;
$workbook->close();

print "Excel file with filters created: $output_xls\n";
