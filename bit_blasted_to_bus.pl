#!/usr/bin/perl
use strict;
use warnings;
use POSIX qw(strftime);
use File::Find;
use v5.8.8;
use Getopt::Long qw(GetOptions);
use Pod::Usage qw(pod2usage);
 
my $man = 0;
my $help = 0;

# Creating temp directory which stores the output files 
#my $date = strftime "%m%d%Y", localtime;
my $date = strftime "%H%M%S_%m%d%Y", localtime;
mkdir "temp_$date";

my $WRAPPER_NAME;
my $MODULE_NAME; 
my $INSTANCE_NAME;

# Input file for which the bit-blaster wrapper will be generated
my $INPUT_FILE_PATH;
my $INPUT_FH;
# All the bussed port container
my $BUSSED_PORT_FILE_PATH = "temp_$date/bussed_ports.list";
my $BUSSED_PORT_FH;
# All the bit-blasted ports container
my $BB_PORT_FILE_PATH = "temp_$date/bitblasted_ports.list";
my $BB_PORT_FH;
# Output file : Bit-Blaster wrapper file 
my $WRAPPER_BB_FILE_PATH;
my $WRAPPER_BB_FH;

# -----------------------------------------------------------------------------
# Find the line and delete from the file
# Info : This sub-routine will find the given pattern in the file and if the 
#        pattern exist in the first serached line then that line will be 
#        removed from the file.
# -----------------------------------------------------------------------------
sub remove_line_if_already_exist_in_file  {
  my $FILE_PATH = $_[0];
  my $match_line = $_[1];
  my $found = 0;
  my @file;
  my $FH;

  undef @file;

  # If file doen't exist then create it
  if (!(-e $FILE_PATH)) {
    open $FH, '>', $FILE_PATH or die "[Err] : Not able to open $FILE_PATH file for writing...$!";
    close $FH;
  }

  open $FH, '<', $FILE_PATH or die "[Err] : Not able to open $FILE_PATH file for reading...$!";
  @file = <$FH>;
  close $FH;

  foreach my $line (@file) {
    if($line =~ / $match_line,/) {
      $line = '';
      $found = 1;
      last;
    }
  }

  if($found) {
    open $FH, '>', $FILE_PATH or die "[Err] : Not able to open $FILE_PATH file for reading...$!";
    print $FH @file;
    close($FH);
  }
}

# -----------------------------------------------------------------------------
# Generate the files for bit-blasted ports and bussed ports
# Info : This sub-routine will read the input file and generate two files, 
#        1) Bussed port informations
#        1) Bit-Blasted port informations
# -----------------------------------------------------------------------------
sub generate_ports {
  my $module_found     = 0          ;
  my $port_found       = 0          ;
  my $is_port_continue = 0          ;
  my @index            = 0          ;
  my $bb_port_found    = 0          ;
  my $push_bb_port     = 0          ;
  my $bb_line          = 0          ;
  my $prev_port_name   = "harshitp" ;
  my $io_type          = 0          ;
  my $port             = 0          ;
  my @line_split                    ; 
  my @port_split                    ; 
  my @bb_line                       ; 

  # Opening Input file for reading
  open $INPUT_FH, '<', $INPUT_FILE_PATH or die "[Err] : Not able to open $INPUT_FILE_PATH file...$!";

  # Opening a file for writing a bit-blasted port information
  open $BB_PORT_FH, '>>', $BB_PORT_FILE_PATH or die "[Err] : Not able to open $BB_PORT_FILE_PATH file for writing...$!";

  undef @index;
  undef @bb_line;

  while (my $line = <$INPUT_FH>) {
    chomp $line;

    undef @line_split;
    undef @port_split;

    # ~~~~~ If the line contains comment, then ignore ~~~~~
    if(substr($line, 0, 2) eq "//") {
      #print "Commented line\n";
    }
    # ~~~~~~ Check if blank line, ignore ~~~~~
    elsif($line =~ /^\s*$/){
      #print "Blank line\n";
    }
    else {
    # ~~~~~ Process of detecting the $MODULE_NAME from the $INPUT_FILE ~~~~~
    #print "<<<< line = $line >>>>\n";
    if ($line =~ /module $MODULE_NAME /) {
      print "[Info] : module $MODULE_NAME found... \n";
      $module_found = 1;
      $push_bb_port = 1;
    }
    # ~~~~~ Process of detecting the endmodule from the netlist file ~~~~~
    elsif ($line =~ /endmodule/ and $module_found == 1) {
      print "[Info] : Found 'endmodule' for $MODULE_NAME \n";
      $module_found = 0;
      $port_found = 0;
      last;
    }

    # ~~~~~ Process of detecting the port end condition ~~~~~
    if ($line =~ /\)/ and $module_found == 1 and $port_found == 0) {
      $port_found = 1;
    }

    # ~~~~~ Process of creating bussed signals and pushed into one file ~~~~~
    if ($module_found == 1 and $port_found == 1 and (($line =~ /^\s*input / or $line =~ /^\s*output / or $line =~ /^\s*inout /) or $is_port_continue == 1)) {

      if ($line =~ /;/) {
      	$is_port_continue = 0;
      }
      else {
      	$is_port_continue = 1;
      }

      $line =~ s/,/ /g;
      $line =~ s/;/ /g;
      @line_split = split (' ', $line);

      # Holds 'input' or 'output' string
      if (($line =~ /^\s*input / or $line =~ /^\s*output / or $line =~ /^\s*inout /)) {
        $io_type = shift @line_split;
      }

      foreach $port (@line_split) {
        # Processing the bit-blasted IO ports
        # if : process for bit-blasted port (ex. \d[2], \d[1], \d[0])
        if($port =~ /^\\/) {
          $port =~ s/^\\//g;
          $port =~ s/]//g;

          undef @port_split;

          # Splitting to get port name and index number
          @port_split = split ('\[', $port);

          # Logic to discriminate two consecutive but different bit-blasted ports
          if($port_split[0] ne $prev_port_name) {
            $bb_port_found = 0;
          }
          if($bb_port_found == 0) {
            $index[0] = $port_split[1];
          }
          $bb_port_found = 1;
          
          # Logic to generate the bussed port from bit-blasted
          $line = "$io_type  [$index[0] : $port_split[1]]  $port_split[0],";
          remove_line_if_already_exist_in_file ($BUSSED_PORT_FILE_PATH, "$port_split[0]");

          $prev_port_name = $port_split[0];
        }
        # else : Normal io ports generation
        else {
          $bb_port_found = 0;
          $line = "$io_type $port,";
        }
        # Opening a file for writing bussed port information
        open $BUSSED_PORT_FH, '>>', $BUSSED_PORT_FILE_PATH or die "[Err] : Not able to open $BUSSED_PORT_FILE_PATH file for writing...$!";
        print $BUSSED_PORT_FH "$line\n";
        close $BUSSED_PORT_FH;
      }
    }

    # ~~~~~ Process of detecting the bit-blasted signals and pushed into one file ~~~~~
    if ($push_bb_port == 1) {
      $bb_line = $line;
      $bb_line =~ s/,//g;

      if ($bb_line =~ /\(/) {
        undef @bb_line;
        @bb_line = split ('\(', $bb_line);
        $bb_line = $bb_line[1];
      }
      if ($bb_line =~ /\)/) {
        undef @bb_line;
        @bb_line = split ('\)', $bb_line);
        $bb_line = $bb_line[0];
      }

      undef @bb_line;
      
      @bb_line = split (' ', $bb_line);

      foreach $bb_line (@bb_line) {
        print $BB_PORT_FH "$bb_line\n";
      }
      if ($port_found == 1) {
        $push_bb_port = 0;
      }
    }
    }
  }
  close $BB_PORT_FH;
  close $INPUT_FH;
}

# -----------------------------------------------------------------------------
# Add the bus ports into the wrapper file. 
# -----------------------------------------------------------------------------
sub process_bussed_ports  {
  my @file;
  my $line;

  open $BUSSED_PORT_FH, '<', $BUSSED_PORT_FILE_PATH or die "[Err] : Not able to open $BUSSED_PORT_FILE_PATH file for reading...$!";
  @file = <$BUSSED_PORT_FH>;
  close $BUSSED_PORT_FH;

  $file[-1] =~ s/,//g;

  foreach my $line (@file) {
    chomp $line;
    print $WRAPPER_BB_FH "  $line\n";
  }
  undef @file;
  print "[Info] : Generated IO Bussed ports for bit-blaster wrapper ($WRAPPER_NAME)\n";

}

# -----------------------------------------------------------------------------
# Connect the bussed ports to the bit-blasted ports in the wrapper file. 
# -----------------------------------------------------------------------------
sub process_bb_ports_link  {
  my $bussed_port;
  my $bb_to_bus_link;
  my @bb_port_file;
  my @file;

  open $BB_PORT_FH, '<', $BB_PORT_FILE_PATH or die "[Err] : Not able to open $BB_PORT_FILE_PATH file for reading...$!";
  @bb_port_file = <$BB_PORT_FH>;
  close $BB_PORT_FH;

  foreach my $bb_port (@bb_port_file) {
    chomp $bb_port;
    $bussed_port = $bb_port;
    $bussed_port =~ s/\\//g;
    $bb_to_bus_link = ".$bb_port                    ($bussed_port),";
    push @file, $bb_to_bus_link; 
  }
  undef @bb_port_file;
  
  $file[-1] =~ s/,//g;

  foreach my $line (@file) {
    chomp $line;
    print $WRAPPER_BB_FH "    $line\n";
  }
  undef @file;

  print "[Info] : Port linking completed between bit-blaster wrapper ($WRAPPER_NAME) and bit-blasted module ($MODULE_NAME)\n";

}

# -----------------------------------------------------------------------------
# This method will generate the bit-blaster wrapper file 
# -----------------------------------------------------------------------------
sub generate_bitblaster_wrapper {
  
  print $WRAPPER_BB_FH "module $WRAPPER_NAME (\n";
  # Generate a file which contains all the bussed io ports
  generate_ports();

  process_bussed_ports();
  print $WRAPPER_BB_FH ");\n\n";

  print $WRAPPER_BB_FH "  $MODULE_NAME $INSTANCE_NAME (\n";
  process_bb_ports_link();
  print $WRAPPER_BB_FH "  );\n";
  print $WRAPPER_BB_FH "endmodule : $WRAPPER_NAME\n";
}

# -----------------------------------------------------------------------------
# Script start from here :
# -----------------------------------------------------------------------------
# If no arguments were given, then allow STDIN to be used only
# if it's not connected to a terminal (otherwise print usage)
pod2usage("$0: No input given.")  if ((@ARGV == 0) && (-t STDIN));

GetOptions(
  'iFile=s'    => \$INPUT_FILE_PATH,
  'wrapper=s'  => \$WRAPPER_NAME,
  'module=s'   => \$MODULE_NAME,
  'instance=s' => \$INSTANCE_NAME,
  'help|?'     => \$help,
  'man'        => \$man
) or pod2usage(2); 

# Parse options and print usage if there is a syntax error,
# or if usage was explicitly requested.
pod2usage(1) if $help;
pod2usage(-verbose => 2) if $man;

print "[Info] : Creating ouput directory : temp_$date\n";
print "[Info] : Generating a bit-blaster wrapper ($WRAPPER_NAME) for a bit-blasted ($MODULE_NAME) module...\n";
print "[Info] : A bit-blasted ($MODULE_NAME) module will be read from file : $INPUT_FILE_PATH\n";

$WRAPPER_BB_FILE_PATH = "temp_$date/$MODULE_NAME.bitblaster_wrapper.v";

# Opening an bit-blaster wrapper file for writing
open $WRAPPER_BB_FH, '>', $WRAPPER_BB_FILE_PATH or die "[Err] : Not able to open $WRAPPER_BB_FILE_PATH file...$!";

# Removing the files if already exist
unlink ($BB_PORT_FILE_PATH) if -e $BB_PORT_FILE_PATH;
unlink ($BUSSED_PORT_FILE_PATH) if -e $BUSSED_PORT_FILE_PATH;

# Generate the bit-blaster wrapper for the bit-blasted module
generate_bitblaster_wrapper();

close $WRAPPER_BB_FH;
print "[Done] : Bit-Blaster wrapper has been generated : $WRAPPER_BB_FILE_PATH \n";
# -----------------------------------------------------------------------------
# End of Script : 
# -----------------------------------------------------------------------------

__END__
 
=head1 NAME
 
auto_gen_bitblaster_wrapper.pl
 
=head1 DESCRIPTION
 
This script reads the given Bit-Blasted input file and generats the Bit-Blaster wrapper output file by mapping each bit-blasted signal to the related bussed signals.
 Step wise process:
    1) Read the Bit-Blasted input file provided in the 'iFile' switch and Search the module name provided in the 'module' switch.
    2) Generate the Bussed signals from the Bit-Blasted signals.
    3) Create wrapper module based on the name provided in the 'wrapper' switch.
    4) Map the Bussed ports and Bit-Blasted ports and instantiate the Bit-Blasted module. Instance name will be picked from the 'instance' switch.
    5) Output files will be generated in the temp_<TIME>_<DATE> directory under same path where this script invokes. 
    6) Name of the output file will be <module>.bitblaster_wrapper.v
