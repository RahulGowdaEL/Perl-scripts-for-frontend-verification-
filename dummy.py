#!/usr/bin/perl
use strict;
use warnings;

use Term::ANSIColor;

# Prompt user for input file
print colored("Enter the input file name: ", 'green');
my $input_file = <STDIN>;
chomp $input_file;

# Check if file exists
if (!-e $input_file) {
    die "File '$input_file' does not exist.\n";
}

my $output_file = 'assertion_output.sv';
open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";

my @user_strings = qw(async_rst upf_simstate async_in sync_out);
my @processed_lines;

open(my $fh, '<', $input_file) or die "Could not open file '$input_file': $!";
while (my $line = <$fh>) {
    chomp $line;

    # Extract relevant lines
    if ($line =~ /u_demet_ares/) {
        $line =~ s/^([^ ]*).*/$1/;  # Extract first part before whitespace
        $line =~ s/\//./g;         # Replace '/' with '.'
        $line =~ s/(u_demet_ares).*/$1/;  # Keep only "u_demet_ares"
        $line = "ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.$line";
        $line =~ s/u_demet_ares/u_demet_model.gen_model2.model2.demet_ares.u_demet_ares/g;
        push @processed_lines, "$line.$_" for @user_strings;
    }
}
close($fh);

my $assertion_count = 1;
my $group_size = scalar @user_strings;

# Write header to output file
print $out_fh "import pwr_tb_pkg::*;\n";
print $out_fh "import quvm_addons_pkg::*;\nimport UPF::*;\n\n";
print $out_fh "logic demet_assertion_disable = 1'b0;\nlogic demet_assertion_triggered;\n";
print $out_fh "upfHandleT snhandle;\nupfBooleanT mirrorstatus;\nupfSupplyObjT tb_upf;\nupfSupplyObjT tb_vdd_ddrss_mach9_int;\nupfBooleanT status;\n";
print $out_fh "initial \nbegin\ndemet_assertion_disable = 1'b1;\n#110ns;\ndemet_assertion_disable = 1'b0;\nend\n\n";

# Assertions creation
for (my $i = 0; $i < scalar(@processed_lines); $i += $group_size) {
    print $out_fh "\nproperty demet_assertion$assertion_count;\n";
    print $out_fh "\@(...clock signal...) disable iff (demet_assertion_disable)\n";
    print $out_fh "((...condition...) && \$fell($processed_lines[$i])) |-> ($processed_lines[$i+2] == $processed_lines[$i+3]);\n";
    print $out_fh "endproperty: demet_assertion$assertion_count\n\n";
    print $out_fh "assert_demet_assertion$assertion_count: assert property(demet_assertion$assertion_count)\n";
    print $out_fh "    else \$error(\"Assertion error: demet_assertion$assertion_count failed at %t\",\$time);\n\n";
    $assertion_count++;
}

close($out_fh);
print "Assertions have been written to $output_file\n";
