#!/usr/bin/perl
use strict;
use warnings;

# File paths
my $file1 = 'file1.txt';
my $file2 = 'file2.txt';
my $output_file = 'difference.txt';

# Read keywords from file1 into a hash
open(my $fh1, '<', $file1) or die "Cannot open $file1: $!";
my %file1_keywords;
while (my $line = <$fh1>) {
    chomp $line;
    $file1_keywords{$line} = 1;
}
close $fh1;

# Read file2 and check for keywords not in file1
open(my $fh2, '<', $file2) or die "Cannot open $file2: $!";
open(my $out_fh, '>', $output_file) or die "Cannot open $output_file: $!";

while (my $line = <$fh2>) {
    chomp $line;
    # Print keywords present in file2 but not in file1
    if (!exists $file1_keywords{$line}) {
        print $out_fh "$line\n";
    }
}
close $fh2;
close $out_fh;

print "Processing complete. Differences written to $output_file\n";
