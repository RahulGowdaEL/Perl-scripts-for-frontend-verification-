#!/usr/bin/perl
use strict;
use warnings;

# Input and output file
my $input_file  = "power_log.txt";   # Change as needed
my $output_file = "power_transitions.log";

# Hash to store state transitions for each power rail
my %power_transitions;

# Open input log file
open my $fh, '<', $input_file or die "Cannot open $input_file: $!";
while (<$fh>) {
    if (/LP_SS_STATE_CHANGE.*Supply Set '(.*?)' transitioned to state '(.*?)'/) {
        my ($rail, $state) = ($1, $2);

        # Normalize rail name to remove full hierarchy
        $rail =~ s{.*/}{};  # Keep only last part

        # Track state transitions
        push @{ $power_transitions{$rail} }, $state 
            if !@{ $power_transitions{$rail} } || $power_transitions{$rail}[-1] ne $state;
    }
}
close $fh;

# Write output file
open my $out, '>', $output_file or die "Cannot write to $output_file: $!";
foreach my $rail (sort keys %power_transitions) {
    print $out "$rail: " . join(" --> ", @{ $power_transitions{$rail} }) . "\n";
}
close $out;

print "Power transitions saved to $output_file\n";
