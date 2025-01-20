use strict;
use warnings;

# Input and output files
my $log_file    = 'input.log';
my $csv_file    = 'input.csv';
my $output_file = 'output.txt';

# Open files
open my $log_fh, '<', $log_file or die "Cannot open log file: $!";
open my $csv_fh, '<', $csv_file or die "Cannot open CSV file: $!";
open my $out_fh, '>', $output_file or die "Cannot open output file: $!";

# Parse CSV file
my %csv_data;
my @freq_names;

while (<$csv_fh>) {
    chomp;
    my @columns = split /,/;

    # Skip header row
    if ($. == 1) {
        @freq_names = @columns[5..$#columns];
        next;
    }

    my $clk_name = $columns[0];
    for my $i (5..$#columns) {
        $csv_data{$clk_name}{ $freq_names[$i - 5] } = $columns[$i];
    }
}
close $csv_fh;

# Parse log file
my @log_entries;
my $current_freq_name = '';

while (<$log_fh>) {
    chomp;

    # Extract FREQ_SWITCH frequency name
    if (/FREQ_SWITCH is = (\w+)/) {
        $current_freq_name = $1;
    }

    # Extract clock information
    if (/Dhyan print for freq in MHz is = ([\d.]+) of (\w+)/) {
        my ($freq_number, $clk_name) = ($1, $2);
        push @log_entries, { clk_name => $clk_name, freq_name => $current_freq_name, freq_number => $freq_number };
    }
}
close $log_fh;

# Compare log data with CSV data and write to output
print $out_fh "Comparison Results:\n";

foreach my $entry (@log_entries) {
    my $clk_name    = $entry->{clk_name};
    my $freq_name   = $entry->{freq_name};
    my $freq_number = $entry->{freq_number};

    if (exists $csv_data{$clk_name}{$freq_name}) {
        my $csv_freq = $csv_data{$clk_name}{$freq_name};
        my $diff = abs($csv_freq - $freq_number);

        if ($diff <= 1) {
            print $out_fh "Match: clk $clk_name freq_name: $freq_name freq_number: $freq_number (CSV: $csv_freq)\n";
        } else {
            print $out_fh "Mismatch: clk $clk_name freq_name: $freq_name freq_number: $freq_number (CSV: $csv_freq)\n";
        }
    } else {
        print $out_fh "Mismatch: clk $clk_name freq_name: $freq_name not found in CSV\n";
    }
}

close $out_fh;
print "Comparison complete. Results saved in $output_file\n";



UVM_INFO @ 5963332138 ps: uvm_test_top [uvm_test_top]  Dhyan print for time_period in ps is = 826 ps of chk_shub_clk
UVM_INFO @ 5963332138 ps: uvm_test_top [uvm_test_top]  Dhyan print for freq in MHz is = 1210.000000 of chk_shub_clk 
UVM_INFO @ 5963343928 ps: uvm_test_top [uvm_test_top]  Dhyan print for time_period in ps is = 4168 ps of chk_pcie_clk
UVM_INFO @ 5963343928 ps: uvm_test_top [uvm_test_top]  Dhyan print for freq in MHz is = 239.000000 of chk_pcie_clk 
UVM_INFO @ 5963378154 ps: uvm_test_top [uvm_test_top]  Dhyan print for time_period in ps is = 13334 ps of chk_cnoc_clk
UVM_INFO @ 5963378154 ps: uvm_test_top [uvm_test_top]  Dhyan print for freq in MHz is = 74.000000 of chk_cnoc_clk 

UVM_INFO @ 0.000ps: reporter@@shrm_rpmh_sequence []  FREQ_SWITCH is = LOWSVS_547_GCC
from csv
Name,Type,Domain,Functional Group,Generator,Max LOWSVS_D1,Max LOWSVS,Max SVS,Max SVS_L1,Max NOM,Max TURBO,Max TURBO_L1,SW Configurations,Access
shub_clk,ext,ddrss_test_grp,ddrss_test,ext,250,250,333.333333,400,400,400,400,,
pcie_clk,ext,ddrss_test_grp,ddrss_test,ext,250,250,333.333333,400,400,400,400,,
cnoc_clk,cbc,ddrss_test_grp:div,ddrss_test_mux,sm_cbc,250,250,333.333333,400,400,400,400,,

for shub_clk : freq_name = lowsvs freq_number from csv -> 250 (so if it's +or - 1) in output it should be showed as matched with all those parameters.
