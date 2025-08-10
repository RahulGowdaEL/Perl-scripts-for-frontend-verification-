#!/usr/bin/perl
use strict;
use warnings;

# Input files
my $log_file = "clock_log.txt";     # Your log file
my $csv_file = "clock_freqs.csv";   # CSV with allowed freqs

# Parse CSV to get allowed frequencies per clock
my %allowed_freqs;
open(my $csv_fh, '<', $csv_file) or die "Cannot open $csv_file: $!";
while (my $line = <$csv_fh>) {
    chomp $line;
    my @fields = split(',', $line);
    next if $fields[0] eq 'Name';  # Skip header
    
    my $clk_name = $fields[0];
    # Extract allowed frequencies (columns 5-12: Max LOWSVS to Max TURBO_L4)
    my @freqs;
    for my $i (5..12) {
        push @freqs, $fields[$i] if $fields[$i] =~ /^\d+\.?\d*$/;  # Only numeric values
    }
    $allowed_freqs{$clk_name} = { map { $_ => 1 } @freqs };  # Store as hash for quick lookup
}
close($csv_fh);

# Parse log file and check frequencies
open(my $log_fh, '<', $log_file) or die "Cannot open $log_file: $!";
my @violations;

while (my $line = <$log_fh>) {
    if ($line =~ /clk_name : (.+?) , at the time : (\d+\.\d+)ns/) {
        my $clk_name = $1;
        my $time_ns = $2;
        
        # Read next line (frequency)
        my $freq_line = <$log_fh>;
        if ($freq_line =~ /having frequency (\d+\.\d+)/) {
            my $freq = $1;
            
            # Skip if clock is off (0 MHz)
            next if $freq == 0;
            
            # Check if frequency is allowed
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

# Print results
if (@violations) {
    print "❌ Found " . scalar(@violations) . " violations:\n";
    print "-" x 50 . "\n";
    for my $i (0 .. $#violations) {
        my $v = $violations[$i];
        print "🚩 Violation " . ($i + 1) . ":\n";
        print "   Clock: $v->{clk_name}\n";
        print "   Time: $v->{time_ns} ns\n";
        print "   Measured: $v->{freq} MHz\n";
        print "   Allowed: " . join(", ", @{ $v->{allowed} }) . " MHz\n";
        print "-" x 50 . "\n";
    }
} else {
    print "✅ All clock frequencies match allowed values!\n";
}
