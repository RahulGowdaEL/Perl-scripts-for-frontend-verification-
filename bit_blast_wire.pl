#!/usr/bin/perl
use strict;
use warnings;

# Input and output file paths
my $file1 = 'file1.v';       # File 1: Input file to modify
my $file2 = 'file2.txt';     # File 2: Reference file
my $output_file = 'output.v'; # Output file for modified contents

# Read signals from File 2 to determine exceptions
my %exception_signals;
open my $ref_fh, '<', $file2 or die "[Error] Cannot open $file2: $!";
while (my $line = <$ref_fh>) {
    chomp $line;
    if ($line =~ /\\(\S+\[\*\].*)/) {  # Match signal pattern \signal_name[*]_*
        $exception_signals{$1} = 1;
    }
}
close $ref_fh;

# Process File 1
open my $in_fh, '<', $file1 or die "[Error] Cannot open $file1: $!";
open my $out_fh, '>', $output_file or die "[Error] Cannot open $output_file: $!";
while (my $line = <$in_fh>) {
    chomp $line;

    # Skip comment lines or blank lines
    if ($line =~ /^\s*\/\// || $line =~ /^\s*$/) {
        print $out_fh "$line\n";
        next;
    }

    # Process line, checking for exceptions
    $line =~ s/\\(\S+)/exists $exception_signals{$1} ? "\\$1" : $1/ge;

    # Write modified line to the output file
    print $out_fh "$line\n";
}
close $in_fh;
close $out_fh;

print "Processing completed. Modified file saved as $output_file.\n";
