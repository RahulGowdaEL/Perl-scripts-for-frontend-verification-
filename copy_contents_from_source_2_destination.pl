#!/usr/bin/perl

use strict;
use warnings;
use File::Copy;

die "Usage: $0 <output_filename>\n" unless @ARGV == 1;
my $output_file = $ARGV[0];

print "Enter the destination path for copying files: ";
my $destination_path = <STDIN>;
chomp($destination_path);

unless (-d $destination_path) {
	mkdir $destination_pathor die "Couldn't create directory: $!";
}

open my $input_fh, '<', 'input_file.txt' or die "Couldn't open input file.txt: $!";
open my $output_file, '>', 'output_file.txt' or die "Couldn't open output file.txt: $!";

while (my $line = <$input_fh>) {
	chomp($line);
	
	if ($line =~ m|^(.*/)([^/]+)$|)  {
		my $output_line = "ct co -nc $line";
		my $copy_from = "$file_path$filename";
		my $copy_to = "$destination_path$filename";
		
		print $output_fh "$output_line\n";
		if (copy($copy_from, $copy_to))  {
			print $output_fh "copied: $copy_from -> $copy_to\n";
		} else {
			print $output_fh "copy failed : $copy_from -> $copy_to\n";
		}
	}  else {
		print $output_fh "Invalid input format: $line\n";
	}
}
close $input_fh;
close $output_fh;
