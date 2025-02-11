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



#!/usr/bin/perl
use strict;
use warnings;

my $input_file = 'vcs_lpmsg.log';   
my $output_file = 'voltage_log.txt';


my %voltage_data;
open(my $in_fh, '<', $input_file) or die "Could not open file '$input_file': $!";

while (my $line = <$in_fh>) {
    chomp($line);
    
    if ($line =~ /\[(\d+) fs\] \[INFO\] \[LP_PPN_VALUE_CHANGE\] Voltage of the primary power net '(.+?)' of power domain '(.+?)' changed from ([\d.]+ V) to ([\d.]+ V)/) {
        my $timestamp = $1;       
        my $net_name = $2;        
        my $power_domain = $3;    
        my $voltage_from = $4;    
        my $voltage_to = $5;              
        $voltage_data{$net_name}{$power_domain} //= [];
        
        my $transition = "$voltage_from --> $voltage_to";
        unless (grep { $_ eq $transition } @{$voltage_data{$net_name}{$power_domain}}) {
            push @{$voltage_data{$net_name}{$power_domain}}, $transition;
        }
    }
}

close($in_fh);

open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";
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
