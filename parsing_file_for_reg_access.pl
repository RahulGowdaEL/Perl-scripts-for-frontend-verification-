#!/usr/bin/perl

use strict;
use warnings;

my $input_file = 'input.log';
my $post_hpg_file = 'output.txt';

open my $input_fh, '<', $input_file or die "Cannot open input file: $!";
open my $hpg_fh, '>', $post_hpg_file or die "Cannot open output_file: $!";  


my %post_hpg_reg;

while (<$input_fh>)  {

#only for write registers
	if ((/HPG SEQUENCE END/) || (/.*?Done writing to the REGISTER=(\S+) reg_addr= (\S+) data (\S+)/)) {
		my $register_name = $1 ;
		my $reg_addr      = $2 ;
		my $actual_data   = $3 ;
		$post_hpg_reg{$register_name} = 1;
		#print $hpg_fh "Writing to the ", "REGISTER=$register_name reg_addr=$reg_addr data-->$actual_data\n";
		}
	}

foreach my $register (sort keys %post_hpg_reg) {
	print $hpg_fh "$register\n";
	}

close $input_fh;
close $hpg_fh;	
