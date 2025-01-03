use strict;
use warnings;

# Prompt for input file
print "Enter the input file name: ";
chomp(my $input_file = <STDIN>);
my $processed_file = "processed.v";

# Hardcoded exclusion list (defined directly in the script)
my %exclusions = (
    '\\signal_ri[*]_s2' => 1,
    '\\signal_vi[*]_e2' => 1,
    '\\signal_q1[*]_r0' => 1,
    # Add more signal names as needed
);

# Open files
open my $fh_in, '<', $input_file or die "Cannot open $input_file: $!";
open my $fh_proc, '>', $processed_file or die "Cannot open $processed_file: $!";

# Step 2: Process lines from the input file
while (my $line = <$fh_in>) {
    chomp($line);

    # Skip processing for lines that include excluded signals
    my $is_excluded = 0;
    foreach my $signal (keys %exclusions) {
        if ($line =~ /\Q$signal\E/) {  # Check if the line contains the excluded signal
            $is_excluded = 1;
            last;
        }
    }

    if ($is_excluded) {
        print $fh_proc "$line\n";  # Write excluded lines unchanged to processed file
        next;
    }

    # Replace backslashes with parentheses for other lines
    $line =~ s/\\/\(/g;
    print $fh_proc "$line\n";  # Write processed lines to processed file
}

# Close files
close $fh_in;
close $fh_proc;

print "Processing complete.\n";
print "Processed lines written to: $processed_file\n";
