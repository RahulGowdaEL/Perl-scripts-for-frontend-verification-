#!/usr/bin/perl
use strict;
use warnings;

# Define input and output file paths
my $input_file = 'input.log';   # Replace with your actual input file
my $output_file = 'voltage_log.txt';

# Hash to store unique voltage transitions for each primary power net and power domain
my %voltage_data;

# Open the input file for reading
open(my $in_fh, '<', $input_file) or die "Could not open file '$input_file': $!";

# Process each line of the input file
while (my $line = <$in_fh>) {
    chomp($line);

    # Match lines containing "[LP_PPN_VALUE_CHANGE]"
    if ($line =~ /\[(\d+) fs\] \[INFO\] \[LP_PPN_VALUE_CHANGE\] Voltage of the primary power net '(.+?)' of power domain '(.+?)' changed from ([\d.]+ V) to ([\d.]+ V)/) {
        my $timestamp = $1;       # Extract the timestamp
        my $net_name = $2;        # Extract the primary power net name
        my $power_domain = $3;    # Extract the power domain
        my $voltage_from = $4;    # Extract the starting voltage
        my $voltage_to = $5;      # Extract the ending voltage

        # Initialize an entry if the net and power domain combination is new
        $voltage_data{$net_name}{$power_domain} //= [];

        # Append the voltage transition if it is unique
        my $transition = "$voltage_from --> $voltage_to";
        unless (grep { $_ eq $transition } @{$voltage_data{$net_name}{$power_domain}}) {
            push @{$voltage_data{$net_name}{$power_domain}}, $transition;
        }
    }
}

close($in_fh);

# Open the output file for writing
open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";

# Write the unique transitions to the output file
foreach my $net (sort keys %voltage_data) {
    foreach my $domain (sort keys %{$voltage_data{$net}}) {
        print $out_fh "Primary Power Net: $net\n";
        print $out_fh "Power Domain: $domain\n";
        print $out_fh "Transitions:\n";
        print $out_fh join(" --> ", map { (split / --> /)[0] } @{$voltage_data{$net}{$domain}}), "\n";
        print $out_fh join(" --> ", map { (split / --> /)[1] } @{$voltage_data{$net}{$domain}}), "\n\n";
    }
}

close($out_fh);

print "Voltage transitions with power domains have been written to '$output_file'.\n";
