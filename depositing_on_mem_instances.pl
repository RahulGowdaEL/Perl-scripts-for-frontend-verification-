#!/usr/bin/perl
use strict;
use warnings;

my $input_file = 'log.txt';  
my $output_file = 'mem_deposits.sv';

open my $in_fh, '<', $input_file or die "Could not open '$input_file' $!";
open my $out_fh, '>', $output_file or die "Could not open '$output_file' $!";

while (my $line = <$in_fh>) {
    chomp $line;

    if ($line =~ /^Memory instance\s+(.*)$/) {
        my $rest_of_line = $1;
	#print "$rest_of_line\n";
        $rest_of_line =~ s/created using QCmemmodel version 1\.6//g;
        $rest_of_line =~ s/^\s+|\s+$//g;

        # Generate the output format
        print $out_fh "always\@(posedge $rest_of_line.slp_ret_n)\n begin\n";
        print $out_fh "\t\$deposit($rest_of_line.dout,0);\n";
	print $out_fh "\t\$display(\"erahul::memory_init_and_load_gates:: %t $rest_of_line\",\$realtime);\n";
        print $out_fh "end\n\n";
    }
}

close $in_fh;
close $out_fh;
print "Processing completed. Output written to '$output_file'.\n";
