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
    if ($line =~ /^\s*wire\s+\\(.+);/) {  # Match lines like 'wire \signal_name;'
        my $signal = $1;
        $signal =~ s/\s+//g;             # Remove spaces
        $exclusions{"\\$signal"} = 1;   # Store in exclusions hash
    }
}

# Rewind the file to process it again
seek $fh_in, 0, 0;

# Step 2: Process lines
while (my $line = <$fh_in>) {
    chomp($line);

    # Check if line contains signals and is excluded
    if ($line =~ /\\(\S+)/) {  # Match any line containing '\signal_name'
        my $signal = $1;       # Extract signal name
        if (exists $exclusions{"\\$signal"}) {
            # If signal is excluded, write to exclusions file
            print $fh_excl "$line\n";
            next;
        }
    }

    # Replace backslashes with parentheses for non-excluded lines
    $line =~ s/\\/\(/g;

    # Write the processed line to the processed file
    print $fh_proc "$line\n";
}

# Close files
close $fh_in;
close $fh_excl;
close $fh_proc;

print "Processing complete.\n";
print "Excluded lines written to: $exclusion_file\n";
print "Processed lines written to: $processed_file\n";
