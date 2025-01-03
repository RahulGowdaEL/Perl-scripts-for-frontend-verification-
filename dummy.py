#!/usr/bin/perl
use strict;
use warnings;

# File definitions
my $input_file     = 'hm_dch_tile_top.v';       
my $exclusion_file = 'port_name_1'; 
my $output_file    = "processed_output.v";

# Load exclusion signals
open my $excl_fh, '<', $exclusion_file or die "Could not open exclusion file '$exclusion_file': $!\n";
my %exclusion_signals;
while (my $line = <$excl_fh>) {
    chomp $line;
    $exclusion_signals{$line} = 1;
}
close $excl_fh;

# Process input file
open my $in_fh,  '<', $input_file  or die "Could not open input file '$input_file': $!\n";
open my $out_fh, '>', $output_file or die "Could not open output file '$output_file': $!\n";

while (my $line = <$in_fh>) {
    foreach my $signal (keys %exclusion_signals) {
        # Handle standard case: Remove backslash for exclusion signals
        $line =~ s/\\($signal\[\d+\])/$1/g;
        
        # Handle the special case: Don't modify backslashes within complex parentheses
        $line =~ s/(\\\.$signal\[\d+\]\s*\(\s*.*?\\$signal\[\d+\].*?\))/$1/g;
    }
    print $out_fh $line;
}

close $in_fh;
close $out_fh;

print "Processing complete. Output written to '$output_file'.\n";
