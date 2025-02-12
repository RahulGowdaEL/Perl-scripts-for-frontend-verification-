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
print "Voltage transitions with power domains have been written to '$output_file'.\n";

instead of the voltages i want the State changes whih will be got by using 
[9458890003000 fs] [INFO] [LP_SS_STATE_CHANGE] Supply Set 'ddr_ss_synthetic_top_wrapper_dv/u_ddr_ss_synthetic_top_wrapper_dut_0/u_ddr_slice_hm_0/u_ddr_slice_center/u_dpcc/u_dpcc_plls/VDD_CX_SS' transitioned to state 'DEFAULT_NORMAL' with simstate 'NORMAL'.
[9458890003000 fs] [INFO] [LP_SS_STATE_CHANGE] Supply Set 'ddr_ss_synthetic_top_wrapper_dv/u_ddr_ss_synthetic_top_wrapper_dut_0/u_ddr_slice_hm_0/u_gen_slice_ddr_slice_ch/u_ddr_slice_ch/u_ddrss_ch02_hm/u_ddrss_ch2/u_mach9_hm/VDD_CX_SS' transitioned to state 'pmux_transition_coa' with simstate 'CORRUPT_ON_ACTIVITY'.
[7700504000 fs] [INFO] [LP_SS_STATE_CHANGE] Supply Set 'ddr_ss_synthetic_top_wrapper_dv/u_ddr_ss_synthetic_top_wrapper_dut_0/u_ddr_slice_hm_0/u_gen_slice_ddr_slice_ch/u_ddr_slice_ch/u_ddrss_ch02_hm/u_ddrss_ch2/u_mach9_hm/VDD_CX_SS' transitioned to state 'DEFAULT_NORMAL' with simstate 'NORMAL'.
[6674450000000 fs] [INFO] [LP_SS_STATE_CHANGE] Supply Set 'ddr_ss_synthetic_top_wrapper_dv/u_ddr_ss_synthetic_top_wrapper_dut_0/u_ddr_slice_hm_0/u_gen_slice_ddr_slice_ch/u_ddr_slice_ch/u_ddrss_ch02_hm/u_ddrss_ch2/u_mach9_hm/u_lpi_lb/VDD_CX_SS' transitioned to state 'off' with simstate 'CORRUPT'.

follow the above coding method and after only for the state change.
