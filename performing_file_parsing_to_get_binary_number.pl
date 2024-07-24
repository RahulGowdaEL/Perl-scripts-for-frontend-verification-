#!/usr/bin/perl

use strict;
use warnings;

my $input_file = 'log.txt';
my $output_file = 'output_file.txt';
my $binary;

open my $input_fh, '<', $input_file or die "Cannot open input file: $!";
open my $output_fh, '>', $output_file or die "Cannot open output_file: $!";   #all
my $value;
while (<$input_fh>)  {

if ((/.*?Rd_data 1 for SCAN_REG=(\S+) /)) {
	$value = $1;
	$value =~ s/x/0/g;
	$value =~ s/X/0/g;
	#sprintf ("%b", ($value));
	my @binary;
	push @binary,$value;
	#print $output_fh "$value\n";
	
	#}
	my $bin = sprintf( "%b", hex($value));
#	my $bin = sprintf('%0*b', length($value)*4, $value);
	$bin =~ s/^0//g;
	print "$bin\n" if length($bin);
	print $output_fh "$value ====> $bin\n";
	}
	}
	
close $input_fh;
close $output_fh;
