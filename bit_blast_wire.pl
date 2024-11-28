#!/usr/bin/perl
use strict;
use warnings;

# Input file paths
my $file1 = 'file1.txt';  # File containing signal names to exclude
my $file2 = 'file2.v';    # File to parse and modify

# Output file path
my $output_file = 'output_file.v';

# Hash to store signal names from File1
my %exclude_signals;

# Read File1 and store signal names in a hash for quick lookup
open my $fh1, '<', $file1 or die "[Err] : Cannot open $file1: $!";
while (my $line = <$fh1>) {
    chomp $line;
    $exclude_signals{$line} = 1;  # Use signal name as a key
}
close $fh1;

# Process File2 and write to the output file
open my $fh2, '<', $file2 or die "[Err] : Cannot open $file2: $!";
open my $out, '>', $output_file or die "[Err] : Cannot open $output_file: $!";

while (my $line = <$fh2>) {
    chomp $line;

    # Check if the line matches any signal name in the exclusion list (File1)
    if ($line =~ /\b\\([\w\[\]\*\_]+)\b/) {
        my $signal_name = $1;

        # Skip processing if the signal name is in the exclusion list
        if (exists $exclude_signals{"\\$signal_name"}) {
            print $out "$line\n";  # Write the line as-is
            next;
        }
    }

    # Remove backslashes from the line (for non-excluded signals)
    $line =~ s/\\//g;

    # Write the modified line to the output file
    print $out "$line\n";
}

close $fh2;
close $out;

print "[Done] : Processed $file2 and created $output_file.\n";
