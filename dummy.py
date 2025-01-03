use strict;
use warnings;

# File paths
my $input_file = "input_file.v";
my $exclusion_file = "exclusions.txt";
my $processed_file = "processed_output.v";

# Open files
open my $fh_in, '<', $input_file or die "Cannot open $input_file: $!";
open my $fh_excl, '<', $exclusion_file or die "Cannot open $exclusion_file: $!";
open my $fh_proc, '>', $processed_file or die "Cannot open $processed_file: $!";

# Step 1: Read exclusion signals from the exclusion file into a hash
my %exclusions;
while (my $line = <$fh_excl>) {
    chomp($line);
    $exclusions{$line} = 1;  # Store exclusion signals as keys in the hash
}

# Step 2: Process the input file
while (my $line = <$fh_in>) {
    chomp($line);

    # Step 2.1: Check if the line contains a signal name in the exclusion list
    foreach my $signal (keys %exclusions) {
        # Match lines that contain backslash before the signal name (but not part of .\)
        if ($line =~ /\\$signal(?!\w)/) {
            # Ensure it is not a .\structure, where the backslash should not be removed
            if ($line !~ /\\\./) {  # If there is no .\ before the backslash
                $line =~ s/\\$signal/$signal/g;  # Remove backslash before signal name
            }
            last;  # Stop further processing for this line
        }
    }

    # Step 3: Print the modified or unchanged line to the output file
    print $fh_proc "$line\n";
}

# Close files
close $fh_in;
close $fh_excl;
close $fh_proc;

print "Processing complete. Output written to $processed_file.\n";
