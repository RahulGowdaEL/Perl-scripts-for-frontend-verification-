
set file1 "$file_name"

set F3 [open $file1 w]

puts $F3 "                                                                        ,,,TIE-OFF REPORT,   "

puts $F3 "Connection Name  , Source Block , Source , Destination Block  , Destination , Status      , Toggle        , COI              , Classification	 "

foreach inst $instance_list {
    check_conn -clear
    # check_conn -reverse -src {u_dsc_fsm 1'b1} -relative_depth 1 -complexity straightforward -load -semicolon_separated
    # check_conn -reverse -dest $inst -relative_depth 0 -complexity conditional -load -semicolon_separated
    check_conn -reverse -target {[get_design_info -instance $inst -list input output -include_hier_path]} -relative_depth 0 -complexity conditional -load -semicolon_separated
    puts $F3 "Connection Extraction done"

    catch {check_conn -generate_toggle_checks {}}
    catch {check_conn -validate}
    catch {check_conn -report -file Tie_off.csv -csv -force}
    
    catch {set result [exec grep "tied to" Tie_off.csv]} result

    puts $F3 "                                                                        ,,,Instance Name: $inst,   "
    puts $F3 "$result"
    set result ""
}

close $F3

set result [exec /view/erahul_nordschleife_ddr_ss_verif_2.0_13_jan_RTL_2_GLS/vobs/cores/infrastructure/ \
wildcat_ddr_ss/wildcat_ddr_ss_verif/sim/Formal/formal_fpv/sim/qvmr/erahul/Tie_off/mail.pl $file_name]






set file1 "$file_name"

set F3 [open $file1 w]

 puts $F3 "                                                                        ,,,TIE-OFF REPORT,																		 "

 puts $F3 "Connection Name  , Source Block , Source , Destination Block  , Destination , Status      , Toggle        , COI              , Classification	 "
 foreach inst $instance_list {
 check_conn -clear
#check_conn -reverse -src {u_dsc_fsm 1'b1} -relative_depth 1 -complexity straightforward -load -semicolon_separated
#check_conn -reverse -dest $inst -relative_depth 0 -complexity conditional -load -semicolon_separated
 check_conn -reverse -target [get_design_info -instance $inst -list input output -include_hier_path] -relative_depth 0 -complexity conditional -load -semicolon_separated
 puts $F3 "Connection Extraction done"
 catch {check_conn -generate_toggle_checks {}}
 catch {check_conn -validate}
 catch {check_conn -report -file Tie_off.csv -csv -force}
 catch {set result [exec grep "tied to" Tie_off.csv ]}
 puts $F3 "                                                                        ,,,Instance Name: $inst,																		 "
 puts $F3 "$result"
 set result ""

}

close $F3

set result [exec /view/erahul_nordschleife_ddr_ss_verif_2.0_13_jan_RTL_2_GLS/vobs/cores/infrastructure/wildcat_ddr_ss/wildcat_ddr_ss_verif/sim/Formal/formal_fpv/sim/qvmr/erahul/Tie_off/mail.pl $file_name]

