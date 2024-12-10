#!/usr/bin/perl
use strict;
use warnings;

# Define input and output file paths
my $input_file = 'input.log';   # Replace with your actual input file
my $output_file = 'voltage_log.txt';

# Hash to store unique voltage transitions for each primary power net
my %voltage_data;

# Open the input file for reading
open(my $in_fh, '<', $input_file) or die "Could not open file '$input_file': $!";

# Process each line of the input file
while (my $line = <$in_fh>) {
    chomp($line);

    # Match lines containing "[LP_PPN_VALUE_CHANGE]"
    if ($line =~ /\[(\d+) fs\] \[INFO\] \[LP_PPN_VALUE_CHANGE\] Voltage of the primary power net '(.+?)' .*? changed from ([\d.]+ V) to ([\d.]+ V)/) {
        my $timestamp = $1;       # Extract the timestamp
        my $net_name = $2;        # Extract the primary power net name
        my $voltage_from = $3;    # Extract the starting voltage
        my $voltage_to = $4;      # Extract the ending voltage

        # Initialize an entry if the net is new
        $voltage_data{$net_name} //= [];

        # Append the voltage transition if it is unique
        my $transition = "$voltage_from --> $voltage_to";
        unless (grep { $_ eq $transition } @{$voltage_data{$net_name}}) {
            push @{$voltage_data{$net_name}}, $transition;
        }
    }
}

close($in_fh);

# Open the output file for writing
open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";

# Write the unique transitions to the output file
foreach my $net (sort keys %voltage_data) {
    print $out_fh "Primary Power Net: $net\n";
    print $out_fh "Transitions:\n";
    print $out_fh join(" --> ", map { (split / --> /)[0] } @{$voltage_data{$net}}), "\n";
    print $out_fh join(" --> ", map { (split / --> /)[1] } @{$voltage_data{$net}}), "\n\n";
}

close($out_fh);

print "Voltage transitions have been written to '$output_file'.\n";
