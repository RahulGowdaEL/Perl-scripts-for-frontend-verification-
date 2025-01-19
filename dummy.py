use strict;
use warnings;

# Input files
my $log_file = 'input.log';
my $csv_file = 'input.csv';
my $output_file = 'output.txt';

# Open files
open my $log_fh, '<', $log_file or die "Could not open log file: $!";
open my $csv_fh, '<', $csv_file or die "Could not open CSV file: $!";
open my $out_fh, '>', $output_file or die "Could not open output file: $!";

# Parse CSV file
my %csv_data;
my @freq_names;

while (<$csv_fh>) {
    chomp;
    my @columns = split /,/;
    if ($. == 1) {
        @freq_names = @columns[5..$#columns]; # Extract frequency names from the first row
        next;
    }
    my $clk_name = $columns[0];
    for my $i (5..$#columns) {
        $csv_data{$clk_name}{$freq_names[$i - 5]} = $columns[$i];
    }
}
close $csv_fh;

# Parse log file
my %log_data;
while (<$log_fh>) {
    chomp;
    if (/shrm_rpmh_seq \[\] FREQ_SWITCH is = (\w+)/) {
        my $freq_name = $1;
        $log_data{'current_freq'} = $freq_name;
    }
    if (/Dhyan print for freq in MHz is = (\d+) of the (\w+)/) {
        my ($freq_number, $clk_name) = ($1, $2);
        push @{$log_data{$clk_name}}, { freq_name => $log_data{'current_freq'}, freq_number => $freq_number };
    }
}
close $log_fh;

# Compare data and write to output
print $out_fh "Comparison Results:\n";
foreach my $clk_name (keys %log_data) {
    next if $clk_name eq 'current_freq';
    foreach my $log_entry (@{$log_data{$clk_name}}) {
        my $freq_name = $log_entry->{freq_name};
        my $freq_number = $log_entry->{freq_number};

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
}
close $out_fh;

print "Comparison complete. Results saved in $output_file\n";
