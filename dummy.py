#!/usr/bin/perl

######################################################################
### Author      :: Robin Garg (robingar@qti.qualcomm.com)
### Description :: Script to capture test status for testcases 
### Usage		:: script -run_path <regress_area>
######################################################################

use Getopt::Long;
use constant;
use FileHandle;
use Env;
use Cwd;
use DBI;
use strict;

my $run_path; my $input_details;
GetOptions ("input_details=s"=> \$input_details, "run_path=s"=> \$run_path);

my @input_detail_array;
if(-e $input_details){
    open (INPUT_FILE,'<',$input_details) or die "Cannot Open $input_details for reading\n$!\n";
        @input_detail_array = <INPUT_FILE>;
    close INPUT_FILE;
} else {
    print "$input_details doesn't exist. Please give the correct path \n";
    exit;
}

my $project;my $type;my $central_area;my $database;my $owner_list;my $test_query_command;my $cc_list;
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
	}
}

my $central_area =  $central_area."/outputs/";

######################################################################
################## Basic Information Extraction ######################
######################################################################
my $user = `whoami | cut -d " " -f1`; chomp ($user);
my $date=`date +%F`; chomp($date);
my $time=`date +%X`; chomp($time);
my $output_details = $central_area.$user."_".$date."_".$time.".csv";

######################################################################
######################### Basic Checks ###############################
######################################################################
if($run_path eq '') {
    print "Error: Enter regression run_path (-run_path). Exiting .....\n";
    exit; 
}
if(!-d $run_path) {
	print "Error: $run_path is not a valid run directory. Exiting .....\n";
	exit;
}

######################################################################
######################### Capturing Tests ############################
######################################################################
my $temp = "run_area_record_temp.out";
my @testlist;

system("ls $run_path > $temp");
if(-e $temp){
    open (INPUT_FILE,'<',$temp) or die "Cannot Open $temp for reading\n\n";
        @testlist = <INPUT_FILE>;
    close INPUT_FILE;
} else {
    print "$temp file doesn't exist. Please check write permissions in PWD. Exiting .....\n";
    exit;
}
system("rm -f $temp");

#DB format: username,testname,nativestatus,teststatus,failuresig,teststart,testend,qsamarea,designbaseline,verifbaseline,logpath,pa_sim
open(OUTPUT_FILE,">$output_details") or die "Cannot Open $output_details for writing\n$!\n";
print OUTPUT_FILE "user,test,nativestatus,teststatus,failuresig,teststart,testend,qsamarea,designbaseline,verifbaseline,logpath,pa_sim\n";
print "\nScript execution in progress ..... \n";

######################################################################
####################### Bucketizing testcases ########################
######################################################################
foreach my $test (@testlist){
	chomp($test);
	my $test_dir = $run_path."/".$test;
	if (-d $test_dir) {
		if($test ne "tb" && $test ne "th" && $test ne "options"){
			my @file_read;
			my $test_run_area = $test_dir."/"."latest/";
			my $session_log = $test_run_area."session.log";my $session_log_gz = $test_run_area."session.log.gz";
			my $nativestatus; my $teststatus; my $failuresig; my $teststart; my $testend; my $qsamarea; my $designbaseline; my $verifbaseline; my $logpath; my $pa_sim=0;
			my $assertion_fail=0;
			my $pa_rtl=0; my $gls=0;
			my $vector=0;
			my $check0=0; my $check1=0; my $check2=0; my $check3=0; my $check4=0; my $check5=0; my $check6=0; my $check7=0;
			if(-e $session_log or -e $session_log_gz){
				if(-e $session_log_gz) {
					open (INPUT_FILE,"gunzip -c $session_log_gz |") or die "Cannot Open $session_log_gz for reading\n$!\n";
						@file_read = <INPUT_FILE>;
					close INPUT_FILE;
				} elsif(-e $session_log) {
					open (INPUT_FILE,'<',$session_log) or die "Cannot Open $session_log for reading\n$!\n";
						@file_read = <INPUT_FILE>;
					close INPUT_FILE;
				}

				foreach my $line (@file_read){
					if($check0==0 && $line =~ / \* Session started: (.*)/){
						$teststart=$1;
						$check0=1;
					} elsif($qsamarea=="" && $line =~ /^.* Info: Executing \"qbar.* (QSAM_TESTDIR='[^ ]+) .*/) {	
						$qsamarea=$1;
						$qsamarea=~s/'//g;$qsamarea=~s/QSAM_TESTDIR=//g;
					} 
					if($logpath=="" && $line =~ /^.* Info: Executing \"qbar.* (RUNDIR='[^ ]+) /) {	
						$logpath=$1;
						$logpath=~s/'//g;$logpath=~s/RUNDIR=//g;
					} elsif ($check2==0 && $line =~ /^\[(.*)\] Info: Done\./) {
						$testend=$1;
						$check2=1;
					} elsif ($check3==0 && $line =~ /^ \* ClearCase Foundation Baseline: baseline:(.*)/) {
						$verifbaseline=$1;
					  	$verifbaseline=~ s/, .*//g;
						$check3=1;
					} elsif ($check4==0 && $line =~ /=== \s*Native Test (.*) \s*===/) {
						$nativestatus=$1; $nativestatus =~ s/ //g;
						$check4=1;
					} elsif ($check5==0 && $line =~ /^  SIMULATION (.*)\s*/) {
						$teststatus=$1;
						$check5=1;
					} elsif ($check6==0 && $line =~ /^UVM_ERROR \//) {
						$failuresig=$line;chomp($failuresig);
						$check6=1;
					}
					if(($check7==0 && $line =~ /HDL_COMPILE_DIR=.*precompiled_rtl\/(.*)\/hdl/) or ($check7==0 && $line =~ /HDL_COMPILE_DIR=.*precompiled_rtl_v2\/(.*)\/hdl/)){
						$designbaseline=$1;
						$designbaseline=~s/^ \s*//g;
						$designbaseline=~s/ \s*.*//g;
						$check7=1;
					} elsif($line =~ /\*\*\* \[vv_runbuildU\] Error /){
						$nativestatus="INCOMPLETE";
						$teststatus="INCOMPLETE";
					} elsif($line =~ /UVM_FATAL.*PH_TIMEOUT.*Explicit timeout of/){
						$nativestatus="FAILED";
						$teststatus="FAILED";
						$failuresig=$line;chomp($failuresig);
					} elsif($failuresig=="" && $line =~ /^Error: .*: Undefined symbol .*/){
						$failuresig=$line;chomp($failuresig); #Failure signature for INCOMPLETE Tests
					} elsif($failuresig=="" && $line =~ /^Process terminated by kill./){
					  	$nativestatus="KILLED";
						$teststatus="KILLED";
						$failuresig=$line;chomp($failuresig);
					} elsif($failuresig=="" && $line =~ /^.ERROR.* Command died with signal 2, without coredump/){
					  	$nativestatus="KILLED";
						$teststatus="KILLED";
						$failuresig=$line;chomp($failuresig);
					} elsif($assertion_fail eq "0" && $line =~ /\tOffending/){
						$assertion_fail=1;
					}
					if(($line =~ /ENABLE_PA_SIM=1/ or $line =~ /ENABLE_PA_SIM='1'/)) {
						$pa_sim=1;
						$pa_rtl=1;
					}
					if($line =~ /GATE_ENABLE=1/ or $line =~ /GATE_ENABLE='1'/) {
						$pa_sim=2;
						$gls=1;
					}
					if(($line =~ /OPTIONS_VECTOR=1/ or $line =~ /OPTIONS_VECTOR='1'/)) {
						$pa_sim=4;
						$vector=1;
					}
				}
				if($failuresig ne ""){
					$failuresig =~ s/,//g;
					$failuresig =~ s/;//g;
				}
				if($gls && $pa_rtl){
					if($vector==0) {$pa_sim=3;} elsif($vector==1) {$pa_sim=5;}
				}
				if($teststatus eq "" and $testend ne "") {
					$teststatus="FAILED";
				} elsif($teststatus eq "PASSED" and $assertion_fail eq "1") {
					$teststatus="ASSERTION_FAIL";
				} 
				print OUTPUT_FILE "$user,$test,$nativestatus,$teststatus,$failuresig,$teststart,$testend,$qsamarea,$designbaseline,$verifbaseline,$logpath,$pa_sim\n";	
			} 
		}
		#Not a valid test directory. Skip this.
	}
	#Not a directory. Skip this.
}
close OUTPUT_FILE;
print "Results stored at: $output_details\n";
