#!/usr/bin/perl
use strict;
use warnings;

# Input files
my $log_file = "clock_log.txt";
my $csv_file = "clock_freqs.csv";
my $output_file = "violations_report.txt";

# Parse CSV to get allowed frequencies per clock
my %allowed_freqs;
open(my $csv_fh, '<', $csv_file) or die "Cannot open $csv_file: $!";
while (my $line = <$csv_fh>) {
    chomp $line;
    my @fields = split(',', $line);
    next if $fields[0] eq 'Name';  # Skip header
    
    my $clk_name = $fields[0];
    my @freqs;
    for my $i (5..12) {
        if ($fields[$i] =~ /^(\d+)(?:\.\d+)?$/) {  # Extract integer part
            push @freqs, $1 + 0;  # Convert to number (removes decimals)
        }
    }
    $allowed_freqs{$clk_name} = { map { $_ => 1 } @freqs };
}
close($csv_fh);

# Parse log file and check frequencies
open(my $log_fh, '<', $log_file) or die "Cannot open $log_file: $!";
my @violations;

while (my $line = <$log_fh>) {
    if ($line =~ /clk_name : (.+?) , at the time : (\d+\.\d+)ns/) {
        my $clk_name = $1;
        my $time_ns = $2;
        
        my $freq_line = <$log_fh>;
        if ($freq_line =~ /having frequency (\d+\.\d+)/) {
            my $freq = $1 + 0;  # Convert to number (e.g., 240.000000 → 240)
            
            next if $freq == 0;  # Skip 0 MHz
            
            if (exists $allowed_freqs{$clk_name}) {
                unless (exists $allowed_freqs{$clk_name}{$freq}) {
                    push @violations, {
                        clk_name => $clk_name,
                        time_ns  => $time_ns,
                        freq     => $freq,
                        allowed  => [ sort { $a <=> $b } keys %{ $allowed_freqs{$clk_name} } ]
                    };
                }
            }
        }
    }
}
close($log_fh);

# Write results to output file
open(my $out_fh, '>', $output_file) or die "Cannot open $output_file: $!";
if (@violations) {
    print $out_fh "❌ Found " . scalar(@violations) . " violations:\n";
    print $out_fh "-" x 50 . "\n";
    for my $i (0 .. $#violations) {
        my $v = $violations[$i];
        print $out_fh "🚩 Violation " . ($i + 1) . ":\n";
        print $out_fh "   Clock: $v->{clk_name}\n";
        print $out_fh "   Time: $v->{time_ns} ns\n";
        print $out_fh "   Measured: $v->{freq} MHz\n";
        print $out_fh "   Allowed: " . join(", ", @{ $v->{allowed} }) . " MHz\n";
        print $out_fh "-" x 50 . "\n";
    }
} else {
    print $out_fh "✅ All clock frequencies match allowed values!\n";
}
close($out_fh);

print "Report generated: $output_file\n";
