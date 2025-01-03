use strict;
use warnings;

# Hardcoded file paths
my $input_file     = 'input.v';       # Replace with your input file name
my $exclusion_file = 'exclusions.txt'; # Replace with your exclusion file name
my $output_file    = 'output.v';       # Replace with your desired output file name

# Read the exclusion file and store exclusions in a hash
open my $fh_exclusion, '<', $exclusion_file or die "Cannot open exclusion file: $!";
my %exclusions;
while (my $line = <$fh_exclusion>) {
    chomp($line);
    $line =~ s/^\s+|\s+$//g;  # Trim leading/trailing whitespace
    $exclusions{$line} = 1 if $line;  # Store valid exclusion signals in the hash
}
close $fh_exclusion;

# Process the input file
open my $fh_in, '<', $input_file or die "Cannot open input file: $!";
open my $fh_out, '>', $output_file or die "Cannot open output file: $!";

while (my $line = <$fh_in>) {
    # Iterate over each exclusion signal
    foreach my $signal (keys %exclusions) {
        # Match the base signal name (ignoring array indices) and remove backslash
        if ($line =~ /\b\\$signal(?:\[\d+\])?\b/) {
            $line =~ s/\\($signal(?:\[\d+\])?)/$1/g;  # Remove backslash for the signal
            last;  # Stop processing further exclusions for this line
        }
    }
    print $fh_out $line; # Write the processed or unmodified line to the output
}

close $fh_in;
close $fh_out;

print "Processing complete. Output written to $output_file.\n";
