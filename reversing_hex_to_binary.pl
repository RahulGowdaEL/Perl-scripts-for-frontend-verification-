#!/usr/bin/perl
use strict;
use warnings;

sub hex_to_32bit_binary {
    my ($hex) = @_;
    my $binary = sprintf("%032b", hex($hex));
    return $binary;
}

sub reverse_binary {
    my ($binary) = @_;
    my $reversed = reverse($binary);
    return $reversed;
}

my $input_file  = 'input.txt';
my $output_file = 'output.txt';

open my $input_fh, '<', $input_file or die "Cannot open input file: $!";
open my $output_fh, '>', $output_file or die "Cannot open output file: $!";
