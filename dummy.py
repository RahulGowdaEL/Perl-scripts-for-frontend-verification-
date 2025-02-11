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
