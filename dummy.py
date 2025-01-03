use strict;
use warnings;

# File paths
my $input_file     = 'input.v';       # Replace with your input file name
my $exclusion_file = 'exclusions.txt'; # Replace with your exclusion file name
my $output_file    = 'output.v';       # Replace with your desired output file name

# Load exclusions into a hash
open my $fh_exclusion, '<', $exclusion_file or die "Cannot open exclusion file: $!";
my %exclusions;
while (my $line = <$fh_exclusion>) {
    chomp($line);
    $line =~ s/^\s+|\s+$//g; # Trim whitespace
    $exclusions{$line} = 1 if $line; # Store valid signals
}
close $fh_exclusion;

# Process input file
open my $fh_in, '<', $input_file or die "Cannot open input file: $!";
open my $fh_out, '>', $output_file or die "Cannot open output file: $!";

while (my $line = <$fh_in>) {
    foreach my $signal (keys %exclusions) {
        # Match signals with optional array indices and remove backslash
        if ($line =~ /\b\\$signal(?:\[\d+\])?\b/) {
            $line =~ s/\\($signal(?:\[\d+\])?)/$1/g;
            last; # Stop further processing once a match is found
        }
    }
    print $fh_out $line; # Write the processed or unmodified line
}

close $fh_in;
close $fh_out;

print "Processing complete. Output written to $output_file.\n";
