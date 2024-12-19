#!/usr/bin/perl
use strict;
use warnings;
use Term::ANSIColor;

print color('green');
print "Please enter the input file name: ";
print color('reset');
my $input_file = <STDIN>;
chomp $input_file;

if (!-e $input_file) {
    die "Input file '$input_file' does not exist.\n";
}

my @user_strings = qw(async_rst upf_simstate async_in sync_out);
my $output_file = 'assertion_output.sv';

open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";
my @processed_lines;

# Parse the input file and process lines
open(my $fh, '<', $input_file) or die "Could not open file '$input_file': $!";
while (my $line = <$fh>) {
    chomp $line;

    if ($line =~ /demet_ares/) {
        $line =~ s/^([^ ]*).*/$1/;
        $line =~ s/\//./g;
        $line =~ s/(u_demet_ares).*/$1/;
        $line =~ s/u_demet_ares/u_demet_model.gen_model2.model2.demet_ares.u_demet_ares/g;
        $line = "ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.$line";

        foreach my $user_string (@user_strings) {
            push @processed_lines, "$line.$user_string";
        }
    }
}
close($fh);

# Generate assertions for SWITCH1
print $out_fh "`ifdef SWITCH1\n";
write_header_and_imports($out_fh, 'u_gen_slice_ddr_slice_ch');
generate_assertions($out_fh, \@processed_lines, 'u_gen_slice_ddr_slice_ch');
print $out_fh "`endif\n\n";

# Generate assertions for SWITCH2
print $out_fh "`ifdef SWITCH2\n";
write_header_and_imports($out_fh, 'u_ddr_slice_center');
generate_assertions($out_fh, \@processed_lines, 'u_ddr_slice_center');
print $out_fh "`endif\n";

close($out_fh);
print "Assertions have been written to $output_file\n";

# Subroutine to write header and import statements
sub write_header_and_imports {
    my ($fh, $condition) = @_;
    print $fh "import pwr_tb_pkg::*;\n";
    print $fh "import quvm_addons_pkg::*;\nimport UPF::*;\n\n";
    print $fh "logic demet_assertion_disable = 1'b0;\nlogic demet_assertion_triggered;\nupfHandleT snhandle;\nupfBooleanT mirrorstatus;\nupfSupplyObjT tb_upf;\nupfSupplyObjT tb_vdd_ddrss_mach9_int;\nupfBooleanT status;\n\n";
    print $fh "initial \nbegin\ndemet_assertion_disable = 1'b1;\n#110ns;\ndemet_assertion_disable = 1'b0;\nend\n\n";
    print $fh "initial\n  begin\nsnhandle = upf_get_handle_by_name(\"\/u_ddr_ss_synthetic_top_wrapper_dut_0\/u_ddr_slice_hm_0\/$condition\/u_ddr_slice_ch\/u_ddrss_ch02_hm\/u_ddrss_ch0\/u_mach9_hm\/vdd_ddrss_mach9_int\@upfSupplyNetT\");\n";
    print $fh "mirrorstatus = upf_create_object_mirror(upf_query_object_pathname(snhandle),\"tb_upf\");\n  if(mirrorstatus == 1)\n\t\$display(\"SV-API_demet: %s\", upf_query_object_pathname(snhandle));\n  end\n";
}

# Subroutine to generate assertions for a specific condition
sub generate_assertions {
    my ($fh, $lines_ref, $condition) = @_;
    my $assertion_count = 1;
    my $group_size = scalar @user_strings;

    for (my $i = 0; $i < scalar(@$lines_ref); $i++) {
        next unless $lines_ref->[$i] =~ /$condition/;

        print $fh "\nproperty demet_assertion$assertion_count;\n";
        print $fh "\@(posedge ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.i_glpi_cc_ddrss_lpinoc_bus_clk) disable iff (demet_assertion_disable)\n";
        print $fh "    ((\$past(tb_upf.current_value.state[0]) == 0) && ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.u_dpcc_cbc_glue.u_dpcc_shub_gdsc.gds_enr == 1 && \$fell($lines_ref->[$i])) |-> ($lines_ref->[$i].async_in == $lines_ref->[$i].sync_out);\n";
        print $fh "endproperty: demet_assertion$assertion_count\n\n";

        print $fh "assert_demet_assertion$assertion_count: assert property(demet_assertion$assertion_count)\n";
        print $fh "    else \$error(\"Assertion error: demet_assertion$assertion_count failed at %t\",\$time);\n\n";

        print $fh "\talways @(negedge $lines_ref->[$i].sync_out or posedge demet_assertion_disable) begin\n";
        print $fh "\t\tif (demet_assertion_disable) begin\n";
        print $fh "\t\t\tdemet_assertion_triggered <= 0;\n";
        print $fh "\t\tend else if (ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.u_dpcc_cbc_glue.u_dpcc_shub_gdsc.gds_enr) begin\n";
        print $fh "\t\t\t\$uvm_warning(\"Warning_demet_sync: Assertion condition for demet_assertion$assertion_count not met during simulation.\");\n";
        print $fh "\t\tend\n";
        print $fh "\tend\n";
        
        $assertion_count++;
    }
}
