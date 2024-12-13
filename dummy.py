#!/usr/bin/perl
use strict;
use warnings;
use Term::ANSIColor;

# Prompt user for input file with green color
print color('green');
print "Please enter the input file name: ";
print color('reset');
my $input_file = <STDIN>;
chomp $input_file;

# Ensure the input file exists
if (!-e $input_file) {
    die "Input file '$input_file' does not exist.\n";
}

my @user_strings = qw(async_rst upf_simstate async_in sync_out);  # Signals in the hierarchy
my $output_file = 'assertion_output.sv';

open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";
my @processed_lines;

open(my $fh, '<', $input_file) or die "Could not open file '$input_file': $!";
while (my $line = <$fh>) {
    chomp $line;

    if ($line =~ /demet_ares/) {
        $line =~ s/^([^ ]*).*/$1/;  # Extract first word before space
        $line =~ s/\//./g;         # Replace '/' with '.'
        $line =~ s/(u_demet_ares).*/$1/; # Keep only 'u_demet_ares' keyword
        $line =~ s/u_demet_ares/u_demet_model.gen_model2.model2.demet_ares.u_demet_ares/g;
        $line = "ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.$line";

        foreach my $user_string (@user_strings) {
            push @processed_lines, "$line.$user_string";
        }
    }
}
close($fh);

# Assertions generation based on line characteristics
my $assertion_count = 1;
my $group_size = scalar @user_strings;

print $out_fh "import pwr_tb_pkg::*;\n";
print $out_fh "import quvm_addons_pkg::*;\nimport UPF::*;\n\n";
print $out_fh "logic demet_assertion_disable = 1'b0;\nlogic demet_assertion_triggered;\nupfHandleT snhandle;\nupfBooleanT mirrorstatus;\nupfSupplyObjT tb_upf;\nupfSupplyObjT tb_vdd_ddrss_mach9_int;\nupfBooleanT status;\n\n";
print $out_fh "initial \nbegin\ndemet_assertion_disable = 1'b1;\n#110ns;\ndemet_assertion_disable = 1'b0;\nend\n\n";
print $out_fh "initial\n  begin\nsnhandle = upf_get_handle_by_name(\"\/u_ddr_ss_synthetic_top_wrapper_dut_0\/u_ddr_slice_hm_0\/u_gen_slice_ddr_slice_ch\/u_ddr_slice_ch\/u_ddrss_ch02_hm\/u_ddrss_ch0\/u_mach9_hm\/vdd_ddrss_mach9_int\@upfSupplyNetT\");\n";
print $out_fh "mirrorstatus = upf_create_object_mirror(upf_query_object_pathname(snhandle),\"tb_upf\");\n  if(mirrorstatus == 1)\n\t\$display(\"SV-API_demet: %s\", upf_query_object_pathname(snhandle));\n  end\n";

foreach my $line (@processed_lines) {
    if ($line =~ /u_gen_slice_ddr_slice_ch/) {
        print_assertions($out_fh, $line, $assertion_count);
        $assertion_count++;
    } elsif ($line =~ /u_ddr_slice_center/) {
        print_assertions($out_fh, $line, $assertion_count);
        $assertion_count++;
    }
}

close($out_fh);
print "Assertions have been written to $output_file\n";

sub print_assertions {
    my ($fh, $line, $count) = @_;
    print $fh "\nproperty demet_assertion$count;\n";
    print $fh "\@(ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.dpcc_ddrss_top_xo_clk) disable iff (demet_assertion_disable)\n\n";
    print $fh "((\$past(tb_upf.current_value.state[0]) == 0) && ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.u_dpcc_cbc_glue.u_dpcc_shub_gdsc.gds_enr == 1 && \$fell($line)) |-> ($line == $line);\n";
    print $fh "endproperty: demet_assertion$count\n\n";
    print $fh "assert_demet_assertion$count: assert property(demet_assertion$count)\n";
    print $fh "    else \$error(\"Assertion error: demet_assertion$count failed at %t\",\$time);\n\n";
    print $fh "\t always @(posedge tb_upf.current_value.state or posedge demet_assertion_disable) begin\n";
    print $fh "\t\t if (demet_assertion_disable) begin\n";
    print $fh "\t\t\t demet_assertion_triggered <= 0;\n";
    print $fh "\t\t end\n\t\t else if ((ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.u_dpcc_cbc_glue.u_dpcc_shub_gdsc.gds_enr) && ($line) == 0) begin\n";
    print $fh "\t\t\t \$uvm_warning(\"Warning_demet_sync: demet_asertions.sv\", \$sformatf(\"demet_assertion$count condition was never met during the simulation.\"));\n\t end\nend\n\n";
}
