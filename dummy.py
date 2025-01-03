use strict;
use warnings;

# Hardcoded file paths
my $input_file     = 'input.v';       # Replace with your input file name
my $exclusion_file = 'exclusions.txt'; # Replace with your exclusion file name
my $output_file    = 'output.v';       # Replace with your desired output file name

# Read exclusion file and build the exclusion hash
open my $fh_exclusion, '<', $exclusion_file or die "Cannot open exclusion file: $!";
my %exclusions;
while (my $line = <$fh_exclusion>) {
    chomp($line);
    $line =~ s/^\s+|\s+$//g;  # Trim whitespace
    $exclusions{$line} = 1 if $line;  # Store the signal names in a hash
}
close $fh_exclusion;

# Process the input file and write the output
open my $fh_in, '<', $input_file or die "Cannot open input file: $!";
open my $fh_out, '>', $output_file or die "Cannot open output file: $!";

while (my $line = <$fh_in>) {
    if ($line =~ /\\([\w\[\]\*]+)/) {  # Match lines with a backslash and potential signal name
        my $signal_name = $1;  # Extract the signal name
        if (exists $exclusions{$signal_name}) {
            # Exact match found in exclusions, remove backslash
            $line =~ s/\\($signal_name)/$1/g;
        }
    }
    print $fh_out $line;  # Write the (possibly modified) line to output
}

close $fh_in;
close $fh_out;

print "Processing completed. Output written to $output_file.\n";
