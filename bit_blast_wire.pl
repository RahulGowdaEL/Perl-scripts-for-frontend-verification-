use strict;
use warnings;

# Input and output files
my $file1 = 'file1.txt';  # Contains excluded signal names
my $file2 = 'file2.v';    # Input Verilog file
my $output_file = 'output.v'; # Output Verilog file

# Read excluded signal names into a hash
open my $fh1, '<', $file1 or die "Cannot open $file1: $!";
my %exclude_signals;
while (<$fh1>) {
    chomp;
    s/^\s+|\s+$//g;    # Trim whitespace
    $exclude_signals{$_} = 1;  # Store signal names as hash keys
}
close $fh1;

# Process the Verilog file
open my $fh2, '<', $file2 or die "Cannot open $file2: $!";
open my $out, '>', $output_file or die "Cannot open $output_file: $!";

while (my $line = <$fh2>) {
    chomp($line);

    # Check if the line contains any excluded signal
    my $exclude_line = 0;
    foreach my $excluded_signal (keys %exclude_signals) {
        if ($line =~ /\Q$excluded_signal\E/) {  # Match exact signal name
            $exclude_line = 1;
            last;  # No need to check further, as this line should be excluded
        }
    }

    if ($exclude_line) {
        # Leave the line unchanged
        print $out "$line\n";
    } else {
        # Remove backslashes from all other lines
        $line =~ s/\\//g;
        print $out "$line\n";
    }
}

close $fh2;
close $out;

print "Processing complete. Output written to $output_file\n";
