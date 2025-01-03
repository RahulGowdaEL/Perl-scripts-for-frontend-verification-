use strict;
use warnings;

# Hardcoded file paths
my $input_file     = 'input.v';       # Replace with your input file name
my $exclusion_file = 'exclusions.txt'; # Replace with your exclusion file name
my $output_file    = 'output.v';       # Replace with your desired output file name

# Read exclusion file and build the exclusion list
open my $fh_exclusion, '<', $exclusion_file or die "Cannot open exclusion file: $!";
my @exclusion_keywords = map { chomp; $_ } <$fh_exclusion>;
close $fh_exclusion;

# Process the input file
open my $fh_in, '<', $input_file or die "Cannot open input file: $!";
open my $fh_out, '>', $output_file or die "Cannot open output file: $!";

while (my $line = <$fh_in>) {
    my $modified = $line;

    foreach my $keyword (@exclusion_keywords) {
        # Match and process set 1: Remove '\' for `.z (\keyword[...] )`
        if ($modified =~ /\.z\s*\(\\$keyword\[(\d+)\]/) {
            $modified =~ s/\.z\s*\(\\($keyword\[\d+\])/\( $1/g;
        }

        # Do not modify set 2: Lines containing `.\keyword[...]`
        elsif ($modified =~ /\\$keyword_/) {
            next; # Skip any modifications for set 2
        }
    }

    print $fh_out $modified;
}

close $fh_in;
close $fh_out;

print "Processing completed. Output written to $output_file.\n";
