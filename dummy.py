
my $file1 = $ARGV[0];
my $file2 = $ARGV[1];

open(file_1, $file1) or die "Couldn't open the file";

print "Opened file: $file1\n";

while (my $String = <file_1>) {
    print "Processing line: $String";
    
    if (($String =~ /internal_channel/ or $String =~ /internal2_channel/) and $String =~ /MASTER/) {
        print "Line matches 'internal_channel' or 'internal2_channel' and 'MASTER'\n";
        
        my @spl = split(' ', $String);
        print "Split line into array: @spl\n";
        
        @chain_name1 = split('_', $spl[1]);
        print "Split chain name: @chain_name1\n";
        
        @chain_value = split('/', $spl[9]);
        print "Split chain value: @chain_value\n";
        
        @chain_value1 = split('_sig', $chain_value[-2]);
        print "Split chain value 1: @chain_value1\n";
        
        @chain_value2 = split('_reg', $chain_value1[1]);
        print "Split chain value 2: @chain_value2\n";
        
        if ($spl[4] =~ /FFFF/) {
            print "Found 'FFFF' in spl[4], pushing $chain_value2[0] to \@signature_value\n";
            push(@signature_value, $chain_value2[0]);
        } else {
            print "Did not find 'FFFF' in spl[4], entering else block\n";
            $neg = int($spl[0]);
            print "Extracted integer value from spl[0]: $neg\n";
            
            if ($neg > 5) {
                print "Neg value ($neg) is greater than 5, applying not operation to $chain_value2[0]\n";
                $signature_value_neg_1 = not($chain_value2[0]);
            } else {
                print "Neg value ($neg) is not greater than 5, using original value $chain_value2[0]\n";
                $signature_value_neg_1 = $chain_value2[0];
            }
            
            print "Pushing $signature_value_neg_1 to \@signature_value\n";
            push(@signature_value, $signature_value_neg_1);
        }
        
        $subs = "chain";
        $a = index($chain_name1[-1], $subs);
        print "Index of 'chain' in $chain_name1[-1]: $a\n";
        
        if ($a == 0) {
            print "Found 'chain' at the beginning of $chain_name1[-1], splitting it\n";
            @chain_name = split('chain', $chain_name1[-1]);
            push(@chain_nu, $chain_name[-1]);
            print "Pushed $chain_name[-1] to \@chain_nu\n";
        } else {
            print "Did not find 'chain' at the beginning, pushing $chain_name1[-1] to \@chain_nu\n";
            push(@chain_nu, $chain_name1[-1]);
        }
        
        push(@chain_pos, $spl[0]);
        print "Pushed $spl[0] to \@chain_pos\n";
    }
}

$size = @signature_value;
$size1 = @chain_pos;
$size2 = @chain_nu;

print "Size of \@signature_value: $size\n";
print "Size of \@chain_pos: $size1\n";
print "Size of \@chain_nu: $size2\n";

if (($size == $size1) and ($size == $size2)) {
    print "All arrays have the same size, proceeding to print results\n";
    
    for ($i = 1; $i <= $size; $i++) {
        $a1 = shift(@chain_nu);
        $a2 = int($a1);
        $a = $a2 - 1;
        $c = pop(@chain_pos);
        $b = pop(@signature_value);
        printf("%s %s %0b\n", $a, $c, $b);
        print "Printed result: $a $c $b\n";
    }
} else {
    print "Array sizes do not match, printing error message\n";
    print("ijtag_txt file size is $size and scan cell report size is $size1, please check the scancell report and signature txt file not matching\n");
}

close file_1;
print "Closed file: $file1\n";



3      u_machx_hm_dft_controller_u_machx_hm_dft_controller_0_machx_hm_insert_mentor_ip_and_networks_tessent_edt_internal1_inst__chain_7  MASTER  (FF-LE)  TFFF  20485631  /ssn_bus_clock                                                                                                                                                                            F    r0hd_ln3_tsmc_n19_dfarsv1t01p00  /u_machx_hm_dft_controller/u_machx_hm_dft_controller_0/u_qdft_insert_mentor_ip_and_networks_tessent_internal1_channel_output_pipe_3_8_sig0_reg/u_dfarsv1t_SIZE_ONLY   seqinst0/mlc_dff    (d,q)           
 4      u_machx_hm_dft_controller_u_machx_hm_dft_controller_0_machx_hm_insert_mentor_ip_and_networks_tessent_edt_internal1_inst__chain_7  MASTER  (FF-LE)  TFFF  20485630  /ssn_bus_clock                                                                                                                                                                            F    r0hd_ln3_tsmc_n19_dfarsv1t01p00  /u_machx_hm_dft_controller/u_machx_hm_dft_controller_0/u_qdft_insert_mentor_ip_and_networks_tessent_internal1_channel_output_pipe_2_8_sig0_reg/u_dfarsv1t_SIZE_ONLY   seqinst0/mlc_dff    (d,q)           
 5      u_machx_hm_dft_controller_u_machx_hm_dft_controller_0_machx_hm_insert_mentor_ip_and_networks_tessent_edt_internal1_inst__chain_7  MASTER  (FF-LE)  TFFF  20485629  /ssn_bus_clock                                                                                                                                                                            F    r0hd_ln3_tsmc_n19_dfarsv1t01p00  /u_machx_hm_dft_controller/u_machx_hm_dft_controller_0/u_qdft_insert_mentor_ip_and_networks_tessent_internal1_channel_output_pipe_1_8_sig1_reg/u_dfarsv1t_SIZE_ONLY   seqinst0/mlc_dff    (d,q)

if (($String =~ /internal_channel/ or $String =~ /internal1_channel/ or $String =~ /internal2_channel/) and $String =~ /MASTER/) {
