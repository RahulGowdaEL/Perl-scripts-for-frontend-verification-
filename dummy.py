use strict;
use warnings;

# Hardcoded file paths
my $input_file     = 'input.v';       # Replace with your input file name
my $exclusion_keyword = 'TraceTargetNIU_Data';  # Keyword to match for exclusion
my $output_file    = 'output.v';       # Replace with your desired output file name

# Open the input and output files
open my $fh_in, '<', $input_file or die "Cannot open input file: $!";
open my $fh_out, '>', $output_file or die "Cannot open output file: $!";

while (my $line = <$fh_in>) {
    # Process Set 1: Remove '\' for signal assignments
    if ($line =~ /\.z\s*\(\s*\\$exclusion_keyword\[\d+\]\s*\)/) {
        $line =~ s/\\($exclusion_keyword\[\d+\])/$1/g;  # Remove backslash
    }
    # Leave Set 2 unchanged (associative lines)
    elsif ($line =~ /\.\\$exclusion_keyword\[\d+\]/) {
        # No modification needed for associative lines
    }
    print $fh_out $line;  # Write the line to output
}

close $fh_in;
close $fh_out;

print "Processing completed. Output written to $output_file.\n";
