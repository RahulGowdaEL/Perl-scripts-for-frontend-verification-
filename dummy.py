use strict;
use warnings;

# Prompt for input and output file names
print "Enter the input file name: ";
chomp(my $input_file = <STDIN>);
my $output_file = "output.v";

# Open files
open my $fh_in, '<', $input_file or die "Cannot open $input_file: $!";
open my $fh_out, '>', $output_file or die "Cannot open $output_file: $!";

# Step 1: Extract exclusion references
my %exclusions;
while (my $line = <$fh_in>) {
    if ($line =~ /^\s*wire\s+\\(.+)/) {  # Match lines with 'wire \'
        my $signal = $1;
        $signal =~ s/\s+//g;             # Remove spaces
        $exclusions{"\\$signal"} = 1;   # Add to exclusions (prefix backslash)
    }
}

# Rewind the file for processing
seek $fh_in, 0, 0;

# Step 2: Process lines and handle exclusions
while (my $line = <$fh_in>) {
    chomp($line);

    # Check if the line contains (\ for modification
    if ($line =~ /\(/) {
        if ($line =~ /\\(\S+)/) {
            my $signal = $1;
            if (exists $exclusions{"\\$signal"}) {
                # Skip modification for excluded signals
                print $fh_out "$line\n";
                next;
            }
        }
        # Modify the line if not excluded
        $line =~ s/\\/\(/g;
    }

    # Write the (modified or unmodified) line to the output
    print $fh_out "$line\n";
}

# Close files
close $fh_in;
close $fh_out;

print "Processing complete. Output written to $output_file\n";
