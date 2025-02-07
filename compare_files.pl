###This is used to parse two different files and get the comparision between the module instance names of DB cells ##

#!/usr/bin/perl
use strict;
use warnings;

my $file1 = 'undefined_db_cell.rpt';
my $file2 = 'undefined_db_cell_2.rpt';

my $output1 = 'output_file1.txt';
my $output2 = 'output_file2.txt';
my $final_output = 'final_output.txt';

sub process_file {
    my ($input_file, $output_file) = @_;
    open my $in, '<', $input_file or die "Could not open '$input_file': $!";
    open my $out, '>', $output_file or die "Could not open '$output_file': $!";
    
    while (my $line = <$in>) {
        if ($line =~ /^Model\s*----->\s*\S+\.(\S+)/) {
            my $my_string = $1; 
            $my_string =~ s/\s+//g;
            print $out "$my_string\n"; 
        }
    }

    close $in;
    close $out;
}

process_file($file1, $output1);
process_file($file2, $output2);

open my $out1, '<', $output1 or die "Could not open '$output1': $!";
open my $out2, '<', $output2 or die "Could not open '$output2': $!";
open my $final_out, '>', $final_output or die "Could not open '$final_output': $!";

my @file1_strings = <$out1>;
my @file2_strings = <$out2>;

chomp(@file1_strings);
chomp(@file2_strings);

my %file2_hash = map { $_ => 1 } @file2_strings;

foreach my $line (@file1_strings) {
    unless (exists $file2_hash{$line}) {
        print $final_out "file_1 has {$line} which is not present in another\n"; 
    }
}

close $out1;
close $out2;
close $final_out;
