#!/pkg/qct/software/perl/5.16.2/bin/perl
##!/pkg/qct/software/perl/q3_10/bin/perl

######################################################################
### Author      :: Robin Garg (robingar@qti.qualcomm.com)
### Description :: Reads regression and test databases to create
###				   detailes xls log, csv log and HTML log
### Usage		:: ./query_sql.pl
######################################################################

use lib '/prj/qct/verif/scripts/power/scripts/PA/';
use html_handler;
use Data::Dumper;
use Getopt::Long;
use constant;
use FileHandle;
use Env;
use Cwd;
use DBI;
use strict;
use Spreadsheet::WriteExcel;
use Spreadsheet::ParseExcel;
use Spreadsheet::ParseXLSX;

my $user; my $test; my $nativestatus; my $teststatus; my $failuresig; my $qsamarea; my $designbaseline; my $verifbaseline; my $logpath; my $pa_sim;
my $input_details;my $mail_all=0;my $assertion_fail=1;my $comparison=0;
GetOptions ("user=s"=>\$user,"test=s"=>\$test,"nativestatus=s"=>\$nativestatus,"teststatus=s"=>\$teststatus,"failuresig=s"=>\$failuresig,"qsamarea=s"=>\$qsamarea,"designbaseline=s"=>\$designbaseline,"verifbaseline=s"=>\$verifbaseline,"logpath=s"=>\$logpath,"pa_sim=s"=>\$pa_sim,"input_details=s"=> \$input_details,"mail_all=s"=> \$mail_all,"assertion_fail=s"=> \$assertion_fail,"comparison=s"=> \$comparison);

my @input_detail_array;
if(-e $input_details){
    open (INPUT_FILE,'<',$input_details) or die "Cannot Open $input_details for reading\n$!\n";
        @input_detail_array = <INPUT_FILE>;
    close INPUT_FILE;
} else {
    print "$input_details doesn't exist. Please give the correct path \n";
    exit;
}

my $project;my $type;my $central_area;my $database;my $owner_list;my $test_query_command;my $cc_list;my $search_query_command;my $message;
foreach (@input_detail_array){
    chomp($_);
    if($_ =~ /^PROJECT=/){
        $project = $_;
        $project =~ s/PROJECT=//g;
		chomp($project);
    } elsif ($_ =~ /^CATEGORY=/) {
    	$type = $_;
		$type =~ s/CATEGORY=//g;
		chomp($type);
	} elsif ($_ =~ /^HOSTING_PATH=/) {
    	$central_area = $_;
		$central_area =~ s/HOSTING_PATH=//g;
		chomp($central_area);
	} elsif ($_ =~ /^DATABASE=/) {
    	$database = $_;
		$database =~ s/DATABASE=//g;
		chomp($database);
	} elsif ($_ =~ /^OWNER_LIST=/) {
    	$owner_list = $_;
		$owner_list =~ s/OWNER_LIST=//g;
		chomp($owner_list);
	} elsif ($_ =~ /^TEST_QUERY_COMMAND=/) {
    	$test_query_command = $_;
		$test_query_command =~ s/TEST_QUERY_COMMAND=//g;
		chomp($test_query_command);
	} elsif ($_ =~ /^MAIL_CC_LIST=/) {
    	$cc_list = $_;
		$cc_list =~ s/MAIL_CC_LIST=//g;
		chomp($cc_list);
	} elsif ($_ =~ /^SEARCH_QUERY_COMMAND=/) {
    	$search_query_command = $_;
		$search_query_command =~ s/SEARCH_QUERY_COMMAND=//g;
		chomp($search_query_command);
	} elsif ($_ =~ /^MESSAGE=/) {
    	$message = $_;
		$message =~ s/MESSAGE=//g;
		chomp($message);
	}
}
my @search_query_commands = split(/,/,$search_query_command);
my @messages = split(/,/,$message);
my $msg = new html_handler() ;
if($pa_sim == 0){
	#$type = "Central";
	$type = "";
	$search_query_command = $search_query_commands[0];
	$message = $messages[0];
	$msg->add_header("$project: $type Regression Results");
	$msg->add_color_msg("b","green","These are latest results for $type testcases (Non-PA)");
	$msg->add_color_msg("b","green","$message");
} elsif ($pa_sim == 1) {
	$search_query_command = $search_query_commands[1];
	$message = $messages[1];
	$type = "PA_RTL";
	$msg->add_header("$project: $type Regression Results");
	$msg->add_color_msg("b","green","These are latest results for $type testcases on Power Aware UPF Model");
	$msg->add_color_msg("b","green","$message");
} elsif ($pa_sim == 2) {
	$search_query_command = $search_query_commands[2];
	$message = $messages[2];
	$type = "GLS";
	$msg->add_header("$project: $type Regression Results");
	$msg->add_color_msg("b","green","These are latest results for $type testcases (Non-PA)");
	$msg->add_color_msg("b","green","$message");
} elsif ($pa_sim == 3) {
	$search_query_command = $search_query_commands[3];
	$message = $messages[3];
	$type = "PA_GLS";
	$msg->add_header("$project: $type Regression Results");
	$msg->add_color_msg("b","green","These are latest results for $type testcases on Power Aware UPF Model");
	$msg->add_color_msg("b","green","$message");
} elsif ($pa_sim == 4) {
	$search_query_command = $search_query_commands[4];
	$message = $messages[4];
	$type = "RTL_ATE";
	$msg->add_header("$project: $type Regression Results");
	$msg->add_color_msg("b","green","These are latest results for $type testcases (Non-PA)");
	$msg->add_color_msg("b","green","$message");
} elsif ($pa_sim == 5) {
	$search_query_command = $search_query_commands[5];
	$message = $messages[5];
	$type = "PA_RTL_ATE";
	$msg->add_header("$project: $type Regression Results");
	$msg->add_color_msg("b","green","These are latest results for $type testcases on Power Aware UPF Model");
	$msg->add_color_msg("b","green","$message");
}
######################################################################
########################## Initializations ###########################
######################################################################
my $date		=`date +%F`; chomp($date);
my $time		=`date +%X`; chomp($time);
my $output		= $date."_".$time."_query_sql_out_".$type.".csv";
my $outputxls	= $date."_".$time."_query_sql_out_".$type.".xls";
my $outputhtml	= $date."_".$time."_query_sql_out_".$type.".html";
my $outputpath	= getcwd()."/".$outputxls; 
my $scripts 	= $central_area."/scripts/";
my $script_name = $scripts."run_area_record.pl";
my $input 		= $scripts.$owner_list;
my $link_xls	= "qctbdcweb.qualcomm.com".$central_area."/summary/".$outputxls;
my $link_html	= "qctbdcweb.qualcomm.com".$central_area."/summary/".$outputhtml;

my $driver   	= "SQLite"; 
$database 	    = $central_area."/sqlite3/".$database;
my $table   	= "record";
my $table_2 	= "test"; 
my $dsn 		= "DBI:$driver:dbname=$database";
my $userid 		= "";
my $password 	= "";
my $dbh 		= DBI->connect($dsn, $userid, $password, { RaiseError => 1 }) or die $DBI::errstr;
print "Database $database Access Successful\n";

my @records; my @entries; my @array; my @read;
my $stmt; my $sth; my $rv; my $to_list;

######################################################################
####################### Creating O/P files ###########################
######################################################################
open(OUTPUT_FILE,">$output") or die "Cannot Open $output for writing\n$!\n";
print OUTPUT_FILE "test,category,tag,user,test,nativestatus,teststatus,failuresig,teststart,testend,qsamarea,designbaseline,verifbaseline,logpath,pa_sim\n";

my $workbook = Spreadsheet::WriteExcel->new($outputxls) or die $!;
my $sheet1 = $workbook->addworksheet("Summary");
my $sheet2 = $workbook->addworksheet("Latest Results");
my $sheet3 = $workbook->addworksheet("Regression Database");
my $sheet4 = $workbook->addworksheet("Test Database");
$sheet1->set_column('A:Z',20);$sheet2->set_column('A:Z',20);$sheet3->set_column('A:Z',20);$sheet4->set_column('A:Z',60);
my $s1_row = 1;my $s2_row = 1;my $s3_row = 1;my $s4_row = 1;

my $format 		  = $workbook->add_format(valign=>'vcenter');$format->set_border(2);$format->set_font('Calibri');
my $format_head   = $workbook->add_format(align=>'center');$workbook->add_format(valign=>'vcenter');$format_head->set_color('black');$format_head->set_border(2);$format_head->set_border_color('black');$format_head->set_bg_color('cyan');$format_head->set_font('Calibri');$format_head->set_bold();
my $format_red	  = $workbook->add_format(align=>'center');$workbook->add_format(valign=>'vcenter');$format_red->set_color('black');$format_red->set_border(2);$format_red->set_border_color('black');$format_red->set_bg_color('orange');$format_red->set_font('Calibri');
my $format_yellow = $workbook->add_format(align=>'center');$workbook->add_format(valign=>'vcenter');$format_yellow->set_color('black');$format_yellow->set_border(2);$format_yellow->set_border_color('black');$format_yellow->set_bg_color('yellow');$format_yellow->set_font('Calibri');
my $format_green = $workbook->add_format(align=>'center');$workbook->add_format(valign=>'vcenter');$format_green->set_color('black');$format_green->set_border(2);$format_green->set_border_color('black');$format_green->set_bg_color('green');$format_green->set_font('Calibri');

if($assertion_fail){
	$sheet1->write(0,0,"Category",$format_head);$sheet1->write(0,1,"Owner",$format_head);$sheet1->write(0,2,"Total Tests",$format_head);$sheet1->write(0,3,"Passed",$format_head);$sheet1->write(0,4,"Failed",$format_head);$sheet1->write(0,5,"AssertionFail",$format_head);$sheet1->write(0,6,"Killed",$format_head);$sheet1->write(0,7,"No Run Record Found",$format_head);$sheet1->write(0,8,"Pass %",$format_head);
} else {
	$sheet1->write(0,0,"Category",$format_head);$sheet1->write(0,1,"Owner",$format_head);$sheet1->write(0,2,"Total Tests",$format_head);$sheet1->write(0,3,"Passed",$format_head);$sheet1->write(0,4,"Failed",$format_head);$sheet1->write(0,5,"Incomplete",$format_head);$sheet1->write(0,6,"Killed",$format_head);$sheet1->write(0,7,"No Run Record Found",$format_head);$sheet1->write(0,8,"Pass %",$format_head);
}
$sheet2->write(0,0,"Test",$format_head);$sheet2->write(0,1,"Category",$format_head);$sheet2->write(0,2,"Tag",$format_head);$sheet2->write(0,3,"User",$format_head);$sheet2->write(0,4,"Test",$format_head);$sheet2->write(0,5,"Native Status",$format_head);$sheet2->write(0,6,"Test Status",$format_head);$sheet2->write(0,7,"Failure Signature",$format_head);$sheet2->write(0,8,"Test Start",$format_head);$sheet2->write(0,9,"Test End",$format_head);$sheet2->write(0,10,"Qsam Area",$format_head);$sheet2->write(0,11,"Design baseline",$format_head);$sheet2->write(0,12,"Verif baseline",$format_head);$sheet2->write(0,13,"Logpath",$format_head);$sheet2->write(0,14,"ENABLE_PA_SIM",$format_head);
$sheet3->write(0,0,"User",$format_head);$sheet3->write(0,1,"Test",$format_head);$sheet3->write(0,2,"Native Status",$format_head);$sheet3->write(0,3,"Test Status",$format_head);$sheet3->write(0,4,"Failure Signature",$format_head);$sheet3->write(0,5,"Test Start",$format_head);$sheet3->write(0,6,"Test End",$format_head);$sheet3->write(0,7,"Qsam Area",$format_head);$sheet3->write(0,8,"Design baseline",$format_head);$sheet3->write(0,9,"Verif baseline",$format_head);$sheet3->write(0,10,"Logpath",$format_head);$sheet3->write(0,11,"ENABLE_PA_SIM",$format_head);
$sheet4->write(0,0,"Test",$format_head);$sheet4->write(0,1,"Category",$format_head);$sheet4->write(0,2,"Tag",$format_head);

my @email_mapping;
open (INPUT_FILE,'<',$input) or die "Cannot Open $input for reading\n\n";
	@email_mapping = <INPUT_FILE>;
close INPUT_FILE;

my $site = `/usr/local/sbin/gvquery -p site`;
$msg->add_link("Download detailed XLS from here","$link_xls");
$msg->add_msg("");
$msg->add_msg("");
$msg->add_link("Web based result summary here","$link_html");
$msg->add_msg("");
$msg->add_msg("");
$msg->start_list("bulleted");
$msg->add_to_list("Results collected on $date at $time ($site timezone)");
if($assertion_fail){
	$msg->add_to_list("Tests passing simulation but having assertion errors are treated as ASSERTION_FAIL");
} else {
	$msg->add_to_list("Tests passing simulation but having assertion errors are treated as SIMULATION_PASSED");
}
$msg->add_to_list("Please find category wise summary below");
$msg->add_to_list("In case you haven't run the script, please run following command to capture your results: $script_name -run_path RUN_AREA_TILL_TARGET_NAME");
$msg->add_to_list("Automatic generated email, please kindly don't reply.");
$msg->end_list();
$msg->start_table();
if($assertion_fail){
	$msg->add_first_row(qw(Category Owner TotalTests Passed Failed AssertionFail Killed NoRunRecordFound Pass%));
} else {
  $msg->add_first_row(qw(Category Owner TotalTests Passed Failed Incomplete Killed NoRunRecordFound Pass%));
}

######################################################################
####################### Populating regression db #####################
######################################################################
my $stmt_r = "SELECT * FROM $table;";
my $sth_r = $dbh->prepare($stmt_r);
my $rv_r = $sth_r->execute() or die $DBI::errstr;
while (my @row_r = $sth_r->fetchrow_array()) {
	$sheet3->write($s3_row,0,$row_r[0],$format);$sheet3->write($s3_row,1,$row_r[1],$format);$sheet3->write($s3_row,2,$row_r[2],$format);$sheet3->write($s3_row,3,$row_r[3],$format);$sheet3->write($s3_row,4,$row_r[4],$format);$sheet3->write($s3_row,5,$row_r[5],$format);$sheet3->write($s3_row,6,$row_r[6],$format);$sheet3->write($s3_row,7,$row_r[7],$format);$sheet3->write($s3_row,8,$row_r[8],$format);$sheet3->write($s3_row,9,$row_r[9],$format);$sheet3->write($s3_row,10,$row_r[10],$format);$sheet3->write($s3_row,11,$row_r[11],$format);$s3_row++;

}

######################################################################
####################### Querying relevant tests from test db #########
######################################################################
my $test_query_extension;
if($pa_sim == 0) {
	$test_query_extension="tag LIKE 'RTL_SIM/%'";
} elsif($pa_sim == 1) {
	$test_query_extension="tag LIKE 'PA_RTL_SIM/%'";
} elsif($pa_sim == 2) {
	$test_query_extension="tag LIKE 'GATE_SIM/%'";
} elsif($pa_sim == 3) {
	$test_query_extension="tag LIKE 'PA_GATE_SIM/%'";
} elsif($pa_sim == 4) {
	$test_query_extension="tag LIKE 'RTL_ATE/%'";
} elsif($pa_sim == 5) {
	$test_query_extension="tag LIKE 'PA_RTL_ATE/%'";
}
my $stmt_2 = "SELECT test,category,tag FROM $table_2 WHERE $test_query_extension $test_query_command;";
my $sth_2 = $dbh->prepare($stmt_2);
my $rv_2 = $sth_2->execute() or die $DBI::errstr;

######################################################################
# For each relevant test, finding record (latest) from regression db #
######################################################################
while (my @row_2 = $sth_2->fetchrow_array()) {
  	$sheet4->write($s4_row,0,$row_2[0],$format);$sheet4->write($s4_row,1,$row_2[1],$format);$sheet4->write($s4_row,2,$row_2[2],$format);$s4_row++;
  	my $query_command = "SELECT * FROM $table WHERE pa_sim = '$pa_sim' AND 
													( test LIKE '%$row_2[0]' OR 
													  test LIKE '%$row_2[0].PA' ) $search_query_command;";
	$stmt = $query_command;
	$sth = $dbh->prepare($stmt);
 	$rv = $sth->execute() or die $DBI::errstr;
	my $entry_count = 0; my $latest_index=0;
	my @md_array; my @md2_array;
	while (my @row = $sth->fetchrow_array()) {
		$md_array[$entry_count] = $row[6];
		$entry_count++;
	}
	if($entry_count>1){
		for(my $i=0; $i < $entry_count; $i++) {
			$md_array[$i] =~ s/  / 0/g; #For dates from 0-9, convert them to 00 - 09
			@md2_array = split(/ /,$md_array[$i]);
			$md_array[$i] = $md2_array[5].$md2_array[1].$md2_array[2].$md2_array[3];
			$md_array[$i] =~ s/://g;
			$md_array[$i] =~ s/Jan/01/g;$md_array[$i] =~ s/Feb/02/g;$md_array[$i] =~ s/Mar/03/g;$md_array[$i] =~ s/Apr/04/g;$md_array[$i] =~ s/May/05/g;$md_array[$i] =~ s/Jun/06/g;$md_array[$i] =~ s/Jul/07/g;$md_array[$i] =~ s/Aug/08/g;$md_array[$i] =~ s/Sep/09/g;$md_array[$i] =~ s/Oct/10/g;$md_array[$i] =~ s/Nov/11/g;$md_array[$i] =~ s/Dec/12/g;
			$md_array[$i] = int($md_array[$i]);
			if($i>0 && $md_array[$i]>$md_array[$i-1]) {
				$latest_index=$i;
			}
		}
		my $i=0;
		
		$stmt = $query_command;
		$sth = $dbh->prepare($stmt);
 		$rv = $sth->execute() or die $DBI::errstr;
		while (my @row = $sth->fetchrow_array()) {
			if($i == $latest_index) {
				my $result = "";
				foreach my $index (@row){
					chomp($index);
					$result = $result."$index".",";
				}
				$result = $row_2[0].",".$row_2[1].",".$row_2[2].",".$result;
				print OUTPUT_FILE "$result\n";
				push(@read,$result);
				my @row_xls = split(/,/,$result);
				$sheet2->write($s2_row,0,$row_xls[0],$format);$sheet2->write($s2_row,1,$row_xls[1],$format);$sheet2->write($s2_row,2,$row_xls[2],$format);$sheet2->write($s2_row,3,$row_xls[3],$format);$sheet2->write($s2_row,4,$row_xls[4],$format);$sheet2->write($s2_row,5,$row_xls[5],$format);$sheet2->write($s2_row,6,$row_xls[6],$format);$sheet2->write($s2_row,7,$row_xls[7],$format);$sheet2->write($s2_row,8,$row_xls[8],$format);$sheet2->write($s2_row,9,$row_xls[9],$format);$sheet2->write($s2_row,10,$row_xls[10],$format);$sheet2->write($s2_row,11,$row_xls[11],$format);$sheet2->write($s2_row,12,$row_xls[12],$format);$sheet2->write($s2_row,13,$row_xls[13],$format);$sheet2->write($s2_row,14,$row_xls[14],$format);$s2_row++;
			}
			$i++;
		}
	} elsif($entry_count==1) {
		$stmt = $query_command;
		$sth = $dbh->prepare($stmt);
 		$rv = $sth->execute() or die $DBI::errstr;
		while (my @row = $sth->fetchrow_array()) {
			my $result = "";
			foreach my $index (@row){
				chomp($index);
				$result = $result."$index".",";
			}
			$result = $row_2[0].",".$row_2[1].",".$row_2[2].",".$result;
			print OUTPUT_FILE "$result\n";
			push(@read,$result);
			my @row_xls = split(/,/,$result);
			$sheet2->write($s2_row,0,$row_xls[0],$format);$sheet2->write($s2_row,1,$row_xls[1],$format);$sheet2->write($s2_row,2,$row_xls[2],$format);$sheet2->write($s2_row,3,$row_xls[3],$format);$sheet2->write($s2_row,4,$row_xls[4],$format);$sheet2->write($s2_row,5,$row_xls[5],$format);$sheet2->write($s2_row,6,$row_xls[6],$format);$sheet2->write($s2_row,7,$row_xls[7],$format);$sheet2->write($s2_row,8,$row_xls[8],$format);$sheet2->write($s2_row,9,$row_xls[9],$format);$sheet2->write($s2_row,10,$row_xls[10],$format);$sheet2->write($s2_row,11,$row_xls[11],$format);$sheet2->write($s2_row,12,$row_xls[12],$format);$sheet2->write($s2_row,13,$row_xls[13],$format);$sheet2->write($s2_row,14,$row_xls[14],$format);$s2_row++;
		}
	} elsif($entry_count==0) {
		my $result = $row_2[0].",".$row_2[1].",".$row_2[2].",No Record Found";
		print OUTPUT_FILE "$result\n";
		push(@read,$result);
		my @row_xls = split(/,/,$result);
		$sheet2->write($s2_row,0,$row_xls[0],$format);$sheet2->write($s2_row,1,$row_xls[1],$format);$sheet2->write($s2_row,2,$row_xls[2],$format);$sheet2->write($s2_row,3,$row_xls[3],$format);$s2_row++;
	}
}

my @breakup; my @category; my @unique_category;
foreach my $line (@read){
	@breakup = split(/,/,$line);
	push(@category,$breakup[1]);
}
@unique_category= uniq(@category);

######################################################################
####################### Creating Summary #############################
######################################################################
my $overall_total = 0; my $overall_pass = 0; my $overall_fail = 0; my $overall_incomp = 0; my $overall_killed = 0; my $overall_nr =0;
print OUTPUT_FILE "\n\n\n";
if($assertion_fail){
	print OUTPUT_FILE "Category,Owner,Total,Passed,Failed,AssertionFail,Killed,NoRecordFound,Pass%\n";
} else {
	print OUTPUT_FILE "Category,Owner,Total,Passed,Failed,Incomplete,Killed,NoRecordFound,Pass%\n";
}
foreach my $category (@unique_category) {
	my $owner; my $owner_email;
	foreach my $mapping (@email_mapping){
  		my @owner_array = split(/,/,$mapping);
		chomp($owner_array[0]);chomp($owner_array[1]);chomp($owner_array[2]);
		if($category eq $owner_array[0]) {
			$owner=$owner_array[1];
			if($owner ne "N/A") {
			  	$owner_email="$owner_array[2]"."\@qti.qualcomm.com";
			  	$to_list = $owner_email.","."$to_list";
			}
		}
	}
	my $total = 0; my $pass = 0; my $fail = 0; my $incomp = 0; my $killed = 0; my $nr =0;
	foreach my $line (@read) {
		@breakup = split(/,/,$line);
		my $test_status = $breakup[6];
		my $no_record = $breakup[3];
		my $cat = $breakup[1];
		if($cat eq $category) {
			$total++;$overall_total++;
			if($assertion_fail){
				if($test_status eq "PASSED") { $pass++;$overall_pass++;}
				elsif($test_status eq "FAILED" or $test_status eq "INCOMPLETE") { $fail++;$overall_fail++;}
				elsif($test_status eq "ASSERTION_FAIL") { $incomp++;$overall_incomp++;}
				elsif($test_status eq "KILLED") { $killed++;$overall_killed++;}
				elsif($no_record =~ /No Record Found/) {$nr++;$overall_nr++;}
			} else {
				if($test_status eq "PASSED" or $test_status eq "ASSERTION_FAIL") { $pass++;$overall_pass++;}
				elsif($test_status eq "FAILED") { $fail++;$overall_fail++;}
				elsif($test_status eq "INCOMPLETE") { $incomp++;$overall_incomp++;}
				elsif($test_status eq "KILLED") { $killed++;$overall_killed++;}
				elsif($no_record =~ /No Record Found/) {$nr++;$overall_nr++;}
			}
		}
	}
	my $pass_p = int($pass*100/$total);
	print OUTPUT_FILE "$category,$owner,$total,$pass,$fail,$incomp,$killed,$nr,$pass_p\n";
	if($pass_p < 50) { $msg->add_color_row_without_font(("red",$category,$owner,$total,$pass,$fail,$incomp,$killed,$nr,$pass_p));$sheet1->write($s1_row,1,$owner,$format_red);$sheet1->write($s1_row,8,$pass_p,$format_red);}
	elsif($pass_p < 75) { $msg->add_color_row_without_font(("purple",$category,$owner,$total,$pass,$fail,$incomp,$killed,$nr,$pass_p));$sheet1->write($s1_row,1,$owner,$format_yellow);$sheet1->write($s1_row,8,$pass_p,$format_yellow);}
	elsif($pass_p < 90) { $msg->add_color_row_without_font(("blue",$category,$owner,$total,$pass,$fail,$incomp,$killed,$nr,$pass_p));$sheet1->write($s1_row,1,$owner,$format_yellow);$sheet1->write($s1_row,8,$pass_p,$format_yellow);}
	else {$msg->add_color_row_without_font(("green",$category,$owner,$total,$pass,$fail,$incomp,$killed,$nr,$pass_p));$sheet1->write($s1_row,1,$owner,$format_green);$sheet1->write($s1_row,8,$pass_p,$format_green);}
	$sheet1->write($s1_row,0,$category,$format);$sheet1->write($s1_row,2,$total,$format);$sheet1->write($s1_row,3,$pass,$format);$sheet1->write($s1_row,4,$fail,$format);$sheet1->write($s1_row,5,$incomp,$format);$sheet1->write($s1_row,6,$killed,$format);$sheet1->write($s1_row,7,$nr,$format);$s1_row++;
}
close OUTPUT_FILE;
my $overall_pass_p = int($overall_pass*100/$overall_total);
$sheet1->write($s1_row,0,"Total",$format_head);$sheet1->write($s1_row,1,"",$format_head);$sheet1->write($s1_row,2,$overall_total,$format_head);$sheet1->write($s1_row,3,$overall_pass,$format_head);$sheet1->write($s1_row,4,$overall_fail,$format_head);$sheet1->write($s1_row,5,$overall_incomp,$format_head);$sheet1->write($s1_row,6,$overall_killed,$format_head);$sheet1->write($s1_row,7,$overall_nr,$format_head);$sheet1->write($s1_row,8,$overall_pass_p,$format_head);$s1_row++;
$msg->add_first_row(("Total","",$overall_total,$overall_pass,$overall_fail,$overall_incomp,$overall_killed,$overall_nr,$overall_pass_p));
$msg->end_table();
$msg->add_break();

######################################################################
####################### Additional Queries ###########################
######################################################################
if($user ne ""){query_db("user",$user);}
if($test ne ""){query_db("test",$test);}
if($nativestatus ne ""){query_db("nativestatus",$nativestatus);}
if($teststatus ne ""){query_db("teststatus",$teststatus);}
if($failuresig ne ""){query_db("failuresig",$failuresig);}
if($qsamarea ne ""){query_db("qsamarea",$qsamarea);}
if($designbaseline ne ""){query_db("designbaseline",$designbaseline);}
if($verifbaseline ne ""){query_db("verifbaseline",$verifbaseline);}
if($logpath ne ""){query_db("logpath",$logpath);}

sub query_db {
	my $dump = "$_[1]"."_query_sql_out.csv";
	open(OUTPUT_FILE,">$dump") or die "Cannot Open $dump for writing\n$!\n";
	print OUTPUT_FILE "user,test,nativestatus,teststatus,failuresig,teststart,testend,qsamarea,designbaseline,verifbaseline,logpath,pa_sim\n";
	
	if($_[0] eq "test") {
		$stmt = "SELECT * FROM $table WHERE $_[0] like '%$_[1]' OR $_[0] like '%$_[1].PA';";
	} elsif($_[0] eq "failuresig") {
		$stmt = "SELECT * FROM $table WHERE $_[0] like '%$_[1]%';";
	} else {
	  	$stmt = "SELECT * FROM $table WHERE $_[0] = '$_[1]';";
	}
	$sth = $dbh->prepare($stmt);
 	$rv = $sth->execute() or die $DBI::errstr;
	
	while (my @row = $sth->fetchrow_array()) {
		my $result = "";
		foreach my $index (@row){
			chomp($index);
			$result = $result."$index".",";
		}
		$result =~ s/,$//g;
		print OUTPUT_FILE "$result\n";
	}
	close OUTPUT_FILE;
}

sub uniq {
    my %seen;
    grep !$seen{$_}++, @_;
}

$workbook->close();

if ($comparison==1) {
	my $date		= `date +%F`; chomp($date);
	my $date_old_1	= `perl -e 'use POSIX;print strftime "%Y-%m-%d",localtime time-86400;'`; chomp($date_old_1);
	my $date_old_2	= `perl -e 'use POSIX;print strftime "%Y-%m-%d",localtime time-172800;'`; chomp($date_old_2);
	my $date_old_3	= `perl -e 'use POSIX;print strftime "%Y-%m-%d",localtime time-259200;'`; chomp($date_old_3);
	my $flag = 0;
	
	my $existence_check = $outputxls;
	$existence_check =~ s/$date/$date_old_1/g;
	if(-e $existence_check){
		$flag=1;			
	} else {
		$existence_check = $outputxls;
		$existence_check =~ s/$date/$date_old_2/g;
		if(-e $existence_check){
			$flag=1;	
		} else {
			$existence_check = $outputxls;
			$existence_check =~ s/$date/$date_old_3/g;
			if(-e $existence_check){
				$flag=1;
			}
		}
	}
	if($flag == 1) {
		$msg->add_header("Comparing number of tests passed today to that of previous day.");
		$msg->start_table();
		$msg->add_first_row(("Category","Owner","Total Tests","Passed Previous Day","Passed Today","Delta Pass"));
		print "Processing $outputxls\n";
		my $excel   = Spreadsheet::ParseExcel->new();
		my $excel2  = $excel->parse($outputxls);
		foreach my $sheet (@{$excel2 -> {Worksheet}}) {
			my $sheetname = $sheet->{Name};
			if($sheetname eq "Summary") {
				my $rs_row_min_0 = $sheet -> {MinRow}; 
				my $rs_row_max_0 = $sheet -> {MaxRow};
				print "Processing $existence_check\n";
				my $excel1   = Spreadsheet::ParseExcel->new();
				my $excel21  = $excel1->parse($existence_check);
				foreach my $sheet1 (@{$excel21 -> {Worksheet}}) {
					my $sheetname1 = $sheet1->{Name};
					if($sheetname1 eq "Summary") {
						for(my $row_index = 1; $row_index < $rs_row_max_0; $row_index++){
							my $rs_cell_B = $sheet->{Cells}[$row_index][0];chomp($rs_cell_B); if($rs_cell_B != '' and $rs_cell_B !~ /#REF!/) {$rs_cell_B = $rs_cell_B->{Val};} else {$rs_cell_B = "";};chomp($rs_cell_B);
							my $rs_cell_C = $sheet->{Cells}[$row_index][1];chomp($rs_cell_C); if($rs_cell_C != '' and $rs_cell_C !~ /#REF!/) {$rs_cell_C = $rs_cell_C->{Val};} else {$rs_cell_C = "";};chomp($rs_cell_C);
							my $rs_cell_D = $sheet->{Cells}[$row_index][2];chomp($rs_cell_D); if($rs_cell_D != '' and $rs_cell_D !~ /#REF!/) {$rs_cell_D = $rs_cell_D->{Val};} else {$rs_cell_D = "";};chomp($rs_cell_D);
							my $rs_cell_E = $sheet->{Cells}[$row_index][3];chomp($rs_cell_E); if($rs_cell_E != '' and $rs_cell_E !~ /#REF!/) {$rs_cell_E = $rs_cell_E->{Val};} else {$rs_cell_E = "";};chomp($rs_cell_E);
							
							my $rs_cell_B1 = $sheet1->{Cells}[$row_index][0];chomp($rs_cell_B1); if($rs_cell_B1 != '' and $rs_cell_B1 !~ /#REF!/) {$rs_cell_B1 = $rs_cell_B1->{Val};} else {$rs_cell_B1 = "";};chomp($rs_cell_B1);
							my $rs_cell_E1 = $sheet1->{Cells}[$row_index][3];chomp($rs_cell_E1); if($rs_cell_E1 != '' and $rs_cell_E1 !~ /#REF!/) {$rs_cell_E1 = $rs_cell_E1->{Val};} else {$rs_cell_E1 = "";};chomp($rs_cell_E1);
							if($rs_cell_B eq $rs_cell_B1){
								my $delta = $rs_cell_E - $rs_cell_E1;
								if($delta >0) {$msg->add_color_row_without_font(("green",$rs_cell_B,$rs_cell_C,$rs_cell_D,$rs_cell_E1,$rs_cell_E,$delta));}
								if($delta ==0) {$msg->add_color_row_without_font(("black",$rs_cell_B,$rs_cell_C,$rs_cell_D,$rs_cell_E1,$rs_cell_E,$delta));}
								if($delta <0) {$msg->add_color_row_without_font(("red",$rs_cell_B,$rs_cell_C,$rs_cell_D,$rs_cell_E1,$rs_cell_E,$delta));}
							}
						}
					}
				}
			}
		}
		$msg->end_table();
		$msg->add_break();
	} else {
		$msg->add_msg("Comparison with last day's result not available.");
	}
}
$msg->add_msg("For reporting any issues in this script, please contact undersigned.");
$msg->add_email("Robin Garg","robingar\@qti.qualcomm.com");
open FH,">$outputhtml" || die "couldn't open $outputhtml for writing\n";
print FH $msg->get_full_message();
close FH;

######################################################################
####################### Sending e-mail ###############################
######################################################################
my $format = $msg->get_full_message();
open(MAIL, "|/usr/sbin/sendmail -t");
if($mail_all==1) {
	print MAIL "To: $to_list\n";
	print MAIL "Cc: $cc_list\n";
} else {
	print MAIL "To: robingar\@qti.qualcomm.com\n";
}
print MAIL "From: robingar\@qti.qualcomm.com\n";
print MAIL "Subject: Project Indicators: $date: $project $type Regress Results\n";
print MAIL "";
print MAIL "Content-Type: text/html\n";
print MAIL "<style> body {background-color:lightyellow;} table, th, td {border: 1px solid black;border-collapse: collapse;} </style>";
print MAIL "$format\n";
close(MAIL);
