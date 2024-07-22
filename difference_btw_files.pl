#!/usr/bin/perl

use strict;
use warnings;

# Input and output file names
my $output_file1 = 'file1';
my $output_file2 = 'file2';
my $unique_registers_dir = 'ret_registers_by_name';  # Directory for storing files by letters

# Ensure the directory exists or create it
unless (-d $unique_registers_dir) {
    mkdir $unique_registers_dir or die "Cannot create directory $unique_registers_dir: $!";
    }
	
# Open output files for reading
open my $output_fh1, '<', $output_file1 or die "Cannot open $output_file1: $!";
open my $output_fh2, '<', $output_file2 or die "Cannot open $output_file2: $!";

# Initialize hash to store unique registers
my %unique_registers;
# Function to extract registers from a file handle
sub extract_registers {
    my ($fh) = @_;  
	my %registers;
    while (<$fh>) {    
		if (/(\S+)/) {
            $registers{$1} = 1;      
			}
    } return %registers;
}

# Extract registers from both output files
%unique_registers = (%unique_registers, extract_registers($output_fh1));
%unique_registers = (%unique_registers, extract_registers($output_fh2));
# Close the files
close $output_fh1;
close $output_fh2;

# Sort registers alphabetically
my @sorted_registers = sort keys %unique_registers;
# Group registers by first letter and write to files
foreach my $register (@sorted_registers) {
    my $first_letter = uc(substr($register, 0, 3)); 
	my $output_file = "$unique_registers_dir/$first_letter.txt";
    # Open file handle for appending
    open my $fh, '>>', $output_file or die "Cannot open $output_file for appending: $!";
    
    # Write register name to the file
    print $fh "$register\n";
    # Close the file handle
    close $fh;
	}
print "Unique register names combined from $output_file1 and $output_file2 have been segregated into files by letters in directory $unique_registers_dir\n";
