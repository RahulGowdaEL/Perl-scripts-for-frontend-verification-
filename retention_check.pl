#!/usr/bin/perl

use strict;
use warnings;

my $directory = '$prj/impl/power_intent/rtl1/vcs/upf/'; 
my $output_file = '/Scripts/XRCA_perl/signal_list'; # Replace with the desired output file name

my @keywords = ('u_mc5_wrap/','u_llcc_wrap','cpu_tile_hm'); #provide any matching word from *design.upf file for which retention cells will be collected

opendir(my $dh, $directory) or die "Failed to open directory: $!";
my @files = grep { /design\.upf$/ } readdir($dh); #collect all the cells from design.upf files
closedir($dh);

open(my $output_fh, '>', $output_file) or die "Failed to open output file: $!";

foreach my $file (@files) {
open(my $fh, '<', "$directory/$file") or die "Failed to open file $file: $!";


while (my $line = <$fh>) {
chomp $line;


#for the specific subsystems retention addition of keywords can be made
if(($line =~ /^u_llcc|  u_mc5_wrap/) | ($line =~ /^u_mc5_wrap|  u_llcc/))   {
$line =~ s/\\/ /g; # Replace backslashes with spaces
$line =~ s/\s+//g; # Remove extra spaces
$line =~ s/\//\./g; # Replace forward slashes with dots
$line.= '#3268220566000fs';  #this is the timestamp which should be provided for xrca

if ($line =~ /^u_llcc/) {
$line = "ddrss_tb_top.u_dut.u_ddrss_center_hm.u_llcc0_hm.$line"; # Insert u_dut at the beginning
	} elsif ($line =~ /^u_mc5_wrap/) {
		$line = "ddrss_tb_top.u_dut.u_ddrss_chgrp_hm.u_ddrss_ch02_hm.u_ddrss_ch0.u_mc5_hm.$line"; # Insert u_dut at the beginning
	}

		print $output_fh "$line\n"; # Write processed line to output file
		}
	}
}

print "Process is completed"
