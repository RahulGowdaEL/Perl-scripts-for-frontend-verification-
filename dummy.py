use strict;
use warnings;

# Prompt for input file
print "Enter the input file name: ";
chomp(my $input_file = <STDIN>);
my $exclusion_file = "exclusions.v";
my $processed_file = "processed.v";

# Open files
open my $fh_in, '<', $input_file or die "Cannot open $input_file: $!";
open my $fh_excl, '>', $exclusion_file or die "Cannot open $exclusion_file: $!";
open my $fh_proc, '>', $processed_file or die "Cannot open $processed_file: $!";

# Step 1: Extract exclusion signals
my %exclusions;
while (my $line = <$fh_in>) {
    if ($line =~ /^\s*wire\s+\\(\S+);/) {  # Match lines like 'wire \signal_name;'
        my $signal = $1;                  # Extract the signal name
        $exclusions{"\\$signal"} = 1;    # Store in exclusions hash
        print $fh_excl $line;            # Write to exclusions file
    }
}

# Rewind the file to process it again
seek $fh_in, 0, 0;

# Step 2: Process lines
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
close $fh_excl;
close $fh_proc;

print "Processing complete.\n";
print "Excluded lines written to: $exclusion_file\n";
print "Processed lines written to: $processed_file\n";
