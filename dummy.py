#!/usr/bin/perl
use strict;
use warnings;

my $input_file = 'center_hm_with_demet.txt';
my @user_strings = qw(async_rst upf_simstate async_in sync_out);  #no of signals in the heirarchy

my $output_file = 'assertion_output.sv';
open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file': $!";
my @processed_lines;

open(my $fh, '<', $input_file) or die "Could not open file '$input_file': $!";while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^([^ ]*).*/$1/;  #first white space
    $line =~ s/\//./g;

   if ($line =~ /u_demet_ares/) {
        $line =~ s/(u_demet_ares).*/$1/; #keeping the desired keyword will remove the remaining 
	}

  #  $line = "ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_gen_slice_ddr_slice_ch.u_ddr_slice_ch.u_ddrss_ch02_hm.u_ddrss_ch0.u_mach9_hm.$line";
    $line = "ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.$line";     #glymur-r2
    $line =~ s/u_demet_ares/u_demet_model.gen_model2.model2.demet_ares.u_demet_ares/g;

    foreach my $user_string (@user_strings) {
        push @processed_lines, "$line.$user_string"; 
	}
}

close($fh);

foreach my $line (@processed_lines) {  
#print $out_fh "$line\n";
	}

my $assertion_count = 1;
my $group_size = scalar @user_strings;  

    print $out_fh "import pwr_tb_pkg::*;\n";
    print $out_fh "import quvm_addons_pkg::*;\nimport UPF::*;\n\n";
    print $out_fh "logic demet_assertion_disable = 1'b0;\nlogic demet_assertion_triggered;\nupfHandleT snhandle;\nupfBooleanT mirrorstatus;\nupfSupplyObjT tb_upf;\nupfSupplyObjT tb_vdd_ddrss_mach9_int;\nupfBooleanT status;\n";
    print $out_fh "logic demet_assertion_disable = 1'b0;\n\n";
    print $out_fh "initial \nbegin\ndemet_assertion_disable = 1'b1;\n#110ns;\ndemet_assertion_disable = 1'b0;\nend\n\n";
    print $out_fh "initial\n  begin\nsnhandle = upf_get_handle_by_name(\"\/u_ddr_ss_synthetic_top_wrapper_dut_0\/u_ddr_slice_hm_0\/u_gen_slice_ddr_slice_ch\/u_ddr_slice_ch\/u_ddrss_ch02_hm\/u_ddrss_ch0\/u_mach9_hm\/vdd_ddrss_mach9_int\@upfSupplyNetT\");\n";
    print $out_fh "mirrorstatus = upf_create_object_mirror(upf_query_object_pathname(snhandle),\"tb_upf\");\n  if(mirrorstatus == 1)\n\t\$display(\"SV-API_demet: %s\", upf_query_object_pathname(snhandle));\n  end\n";


#assertions creation
for (my $i = 0; $i < scalar(@processed_lines);$i += $group_size) {

    print $out_fh "\nproperty demet_assertion$assertion_count;\n"; 
    print $out_fh "\@(ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.dpcc_ddrss_top_xo_clk) disable iff (demet_assertion_disable)\n\n";
    print $out_fh "((\$past(tb_upf.current_value.state[0]) == 0) && ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.u_dpcc_cbc_glue.u_dpcc_shub_gdsc.gds_enr == 1 && \$fell($processed_lines[$i])) |-> ($processed_lines[$i+2] == $processed_lines[$i+3]);\n"; 
    print $out_fh "endproperty: demet_assertion$assertion_count\n\n";
    print $out_fh "assert_demet_assertion$assertion_count: assert property(demet_assertion$assertion_count)\n"; 
    print $out_fh "    else \$error(\"Assertion error: demet_assertion$assertion_count failed at %t\",\$time);\n\n";
    print $out_fh "\t always @(posedge tb_upf.current_value.state or posedge demet_assertion_disable) begin\n";
    print $out_fh "\t\t if (demet_assertion_disable) begin\n";
    print $out_fh "\t\t\t demet_assertion_triggered <= 0;\n";
    print $out_fh "\t\t end\n\t\t else if ((ddr_ss_synthetic_top_wrapper_dv.u_ddr_ss_synthetic_top_wrapper_dut_0.u_ddr_slice_hm_0.u_ddr_slice_center.u_dpcc.u_dpcc_cbc_glue.u_dpcc_shub_gdsc.gds_enr) && ($processed_lines[$i]) == 0) begin\n";
    print $out_fh "\t\t\t \$uvm_warning(\"Warning_demet_sync: demet_asertions.sv\", \$sformatf(\"demet_assertion$assertion_count condition was never met during the simulation.\"));\n\t end\nend\n\n";
    $assertion_count++;
    }

close($out_fh);
print "Assertions have been written to $output_file\n";
