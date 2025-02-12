#!/usr/bin/perl
use strict;
use warnings;

# Input file names
my $file1 = 'file1.txt';   # Source file
my $file2 = 'file2.txt';   # Comparison file
my $output_file = 'difference.txt';  # Output file

# Hash to store words from file2
my %words_in_file2;

# Read file2 and store words in a hash
open(my $fh2, '<', $file2) or die "Could not open '$file2': $!";
while (my $line = <$fh2>) {
    chomp($line);
    $words_in_file2{$line} = 1;  # Store as hash keys for quick lookup
}
close($fh2);

# Open output file for writing
open(my $out_fh, '>', $output_file) or die "Could not open '$output_file': $!";

# Read file1 and check for missing words
open(my $fh1, '<', $file1) or die "Could not open '$file1': $!";
while (my $line = <$fh1>) {
    chomp($line);
    # If the word is not in file2, write to output
    print $out_fh "$line\n" unless exists $words_in_file2{$line};
}
close($fh1);
close($out_fh);

print "Words present in '$file1' but not in '$file2' have been written to '$output_file'.\n";





#!/usr/bin/perl
use strict;
use warnings;

# Input and output file names
my $input_file  = 'vcs_lpmsg.log';
my $output_file = 'state_changes_log.txt';

# Hash to store state transition data
my %state_data;

# Open the log file for reading
open(my $in_fh, '<', $input_file) or die "Could not open file '$input_file': $!";

while (my $line = <$in_fh>) {
    chomp($line);
    
    # Match state change log format
    if ($line =~ /\[(\d+) fs\] \[INFO\] \[LP_SS_STATE_CHANGE\] Supply Set '(.+?)' transitioned to state '(.+?)' with simstate '(.+?)'/) {
        my $timestamp  = $1;
        my $supply_set = $2;
        my $state      = $3;
        my $simstate   = $4;
        
        # Store state changes per supply set
        $state_data{$supply_set} //= [];
        my $transition = "$state [$simstate]";
        
        # Avoid duplicate transitions
        unless (grep { $_ eq $transition } @{$state_data{$supply_set}}) {
            push @{$state_data{$supply_set}}, $transition;
        }
    }
}

close($in_fh);

# Open output file for writing
open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";

# Print collected state transitions
foreach my $supply_set (sort keys %state_data) {
    print $out_fh "Supply Set: $supply_set\n";
    print $out_fh "State Transitions:\n";
    
    # Separate transitions into "From" and "To" lists for readability
    my @from_states = map { (split / \[/)[0] } @{$state_data{$supply_set}};
    my @to_states   = map { (split / \[/)[1] } @{$state_data{$supply_set}};

    print $out_fh join(" --> ", @from_states), "\n";
    print $out_fh join(" --> ", @to_states), "\n\n";
}

close($out_fh);
print "State transitions have been written to '$output_file'.\n";








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
