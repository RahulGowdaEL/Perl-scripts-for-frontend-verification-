#!/usr/bin/perl
use strict;
use warnings;

# Define input, exclusion, and output file names
my $input_file = 'in';
my $exclusion_file = 'exc';
my $output_file = 'out';

# Read exclusion signals from exclusion file
open my $excl_fh, '<', $exclusion_file or die "Could not open exclusion file '$exclusion_file': $!\n";
my %exclusion_signals;
while (my $line = <$excl_fh>) {
    chomp $line;
    $exclusion_signals{$line} = 1;
}
close $excl_fh;

# Process the input file
open my $in_fh,  '<', $input_file  or die "Could not open input file '$input_file': $!\n";
open my $out_fh, '>', $output_file or die "Could not open output file '$output_file': $!\n";

while (my $line = <$in_fh>) {
    # Remove backslashes for exclusion signals only
    $line =~ s/\\(\w+\[\d+\])/$1/g if grep { $line =~ /$_/ } keys %exclusion_signals;
    print $out_fh $line;
}

close $in_fh;
close $out_fh;

print "Processing complete. Output written to '$output_file'.\n";
