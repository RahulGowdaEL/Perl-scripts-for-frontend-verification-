use strict;
use warnings;

# Define file paths
my $input_file     = 'input_file.v';        # Input Verilog file
my $exclusion_file = 'exclusion_file.txt'; # File containing exclusion keywords
my $output_file    = 'output_file.v';      # Output processed file

# Read exclusions into a hash
open my $fh_excl, '<', $exclusion_file or die "Cannot open $exclusion_file: $!";
my %exclusions;
while (<$fh_excl>) {
    chomp;
    $exclusions{$_} = 1;
}
close $fh_excl;

# Process the input file
open my $fh_in,  '<', $input_file  or die "Cannot open $input_file: $!";
open my $fh_out, '>', $output_file or die "Cannot open $output_file: $!";

while (<$fh_in>) {
    my $line = $_;

    # Check if the line matches any exclusion keyword
    my $exclude_match = 0;
    foreach my $keyword (keys %exclusions) {
        if ($line =~ /\\$keyword/) { # Match lines with `\keyword`
            $exclude_match = 1;
            last;
        }
    }

    if ($exclude_match) {
        # Remove '\' for lines like Set 1
        if ($line =~ /\.\w+\s*\(\\/) {
            $line =~ s/\\//g; # Remove '\'
        }
        # Leave Set 2 lines intact (already matching exclusions)
    } else {
        # Remove '\' from other lines (general case)
        $line =~ s/\\//g;
    }

    print $fh_out $line; # Write processed line to output
}

close $fh_in;
close $fh_out;

print "Processing complete. Check $output_file for results.\n";
