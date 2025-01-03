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

    # Step 2.1: Match lines with the pattern '(\', but avoid lines with exclusion signals
    if ($line =~ /\(\s*\\([\w\[\]\*\_]+)\s*\)/) {  # Check for the pattern `(\` with a signal name
        my $signal_name = $1;

        # If the signal is not in the exclusion list, remove the backslash
        if (!exists $exclusions{$signal_name}) {
            $line =~ s/\\($signal_name)/$1/g;
        }
    }

    # Step 2.2: Print the (modified or unchanged) line to the output file
    print $fh_proc "$line\n";
}

# Close files
close $fh_in;
close $fh_excl;
close $fh_proc;

print "Processing complete. Output written to $processed_file.\n";
