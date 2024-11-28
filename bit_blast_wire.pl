use strict;
use warnings;

# Input and output files
my $file1 = 'file1.txt';
my $file2 = 'file2.v';
my $output_file = 'output.v';

# Read excluded signal names from file1 into a hash
open my $fh1, '<', $file1 or die "Cannot open $file1: $!";
my %exclude_signals;
while (<$fh1>) {
    chomp;
    s/^\s+|\s+$//g;    # Trim leading/trailing whitespace
    $exclude_signals{$_} = 1;  # Store as keys in hash
}
close $fh1;

# Process file2
open my $fh2, '<', $file2 or die "Cannot open $file2: $!";
open my $out, '>', $output_file or die "Cannot open $output_file: $!";

while (my $line = <$fh2>) {
    chomp($line);

    # Check for signals in the line
    if ($line =~ /\\([\w\[\]\*\_]+)/) {  # Match backslash-prefixed signals
        my $signal_name = "\\$1";  # Reconstruct signal name with backslash

        if (exists $exclude_signals{$signal_name}) {
            # Do not modify this line
            print $out "$line\n";
            next;
        }
    }

    # Remove backslashes from all other lines
    $line =~ s/\\//g;
    print $out "$line\n";
}

close $fh2;
close $out;

print "Processing complete. Output written to $output_file\n";
