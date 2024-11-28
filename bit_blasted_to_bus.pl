#!/usr/bin/perl
use strict;
use warnings;
use POSIX qw(strftime);
use File::Copy;
use Getopt::Long qw(GetOptions);
use Pod::Usage qw(pod2usage);

# Timestamp for directory and file naming
my $date = strftime "%H%M%S_%m%d%Y", localtime;
mkdir "temp_$date";

# Input and output variables
my ($INPUT_FILE_PATH, $MODULE_NAME, $WRAPPER_NAME, $INSTANCE_NAME, $OUTPUT_FILE_PATH);
my $EXTRACTED_SIGNALS_FILE = "temp_$date/extracted_signals.list";

# Temporary files for bussed and bit-blasted ports
my $BUSSED_PORT_FILE_PATH = "temp_$date/bussed_ports.list";
my $BB_PORT_FILE_PATH     = "temp_$date/bitblasted_ports.list";

# File handles
my ($INPUT_FH, $BUSSED_PORT_FH, $BB_PORT_FH, $WRAPPER_BB_FH);

# Parse options
GetOptions(
    'iFile=s'    => \$INPUT_FILE_PATH,
    'module=s'   => \$MODULE_NAME,
    'wrapper=s'  => \$WRAPPER_NAME,
    'instance=s' => \$INSTANCE_NAME,
    'oFile=s'    => \$OUTPUT_FILE_PATH,
    'help|?'     => sub { pod2usage(1) },
    'man'        => sub { pod2usage(-verbose => 2) },
) or pod2usage(2);

die "[Err] : Input file not provided!\n" unless $INPUT_FILE_PATH;
die "[Err] : Module name not provided!\n" unless $MODULE_NAME;
die "[Err] : Wrapper name not provided!\n" unless $WRAPPER_NAME;
die "[Err] : Instance name not provided!\n" unless $INSTANCE_NAME;

# Backup input file
my $backup_file = "$INPUT_FILE_PATH.bak";
copy($INPUT_FILE_PATH, $backup_file) or die "[Err] : Unable to create backup: $!";

# Remove temporary files if they exist
unlink $BUSSED_PORT_FILE_PATH if -e $BUSSED_PORT_FILE_PATH;
unlink $BB_PORT_FILE_PATH if -e $BB_PORT_FILE_PATH;

# -----------------------------------------------------------------------------
# Subroutine to remove duplicates from a file
# -----------------------------------------------------------------------------
sub remove_line_if_already_exist_in_file {
    my ($FILE_PATH, $match_line) = @_;
    my @file;
    if (-e $FILE_PATH) {
        open my $FH, '<', $FILE_PATH or die "[Err] : Cannot open $FILE_PATH for reading...$!";
        @file = <$FH>;
        close $FH;
    }
    @file = grep { !/$match_line/ } @file;
    open my $FH, '>', $FILE_PATH or die "[Err] : Cannot open $FILE_PATH for writing...$!";
    print $FH @file;
    close $FH;
}

# -----------------------------------------------------------------------------
# Generate ports and populate bit-blasted and bussed port files
# -----------------------------------------------------------------------------
sub generate_ports {
    open $INPUT_FH, '<', $INPUT_FILE_PATH or die "[Err] : Cannot open $INPUT_FILE_PATH...$!";
    open $BB_PORT_FH, '>>', $BB_PORT_FILE_PATH or die "[Err] : Cannot open $BB_PORT_FILE_PATH...$!";

    my $module_found = 0;
    my $port_found = 0;
    my $is_port_continue = 0;

    while (my $line = <$INPUT_FH>) {
        chomp $line;

        if ($line =~ /module\s+$MODULE_NAME/) {
            $module_found = 1;
        }
        elsif ($line =~ /endmodule/ && $module_found) {
            last;
        }

        if ($module_found && $line =~ /^\s*(input|output|inout)\s+/) {
            $line =~ s/,/ /g;
            $line =~ s/;/ /g;

            my ($io_type, @ports) = split ' ', $line;
            foreach my $port (@ports) {
                if ($port =~ /^\\/) {
                    $port =~ s/^\\//;
                    $port =~ s/\]//g;
                    remove_line_if_already_exist_in_file($BUSSED_PORT_FILE_PATH, $port);
                }
                print $BB_PORT_FH "$port\n";
            }
        }
    }

    close $BB_PORT_FH;
    close $INPUT_FH;
}

# -----------------------------------------------------------------------------
# Generate bit-blaster wrapper
# -----------------------------------------------------------------------------
sub generate_bitblaster_wrapper {
    open $WRAPPER_BB_FH, '>', $OUTPUT_FILE_PATH or die "[Err] : Cannot open $OUTPUT_FILE_PATH...$!";
    print $WRAPPER_BB_FH "module $WRAPPER_NAME (\n";
    generate_ports();
    process_bussed_ports();
    print $WRAPPER_BB_FH ");\n\n  $MODULE_NAME $INSTANCE_NAME (\n";
    process_bb_ports_link();
    print $WRAPPER_BB_FH "  );\nendmodule : $WRAPPER_NAME\n";
    close $WRAPPER_BB_FH;
}

# -----------------------------------------------------------------------------
# Insert bussed ports into the wrapper
# -----------------------------------------------------------------------------
sub process_bussed_ports {
    open $BUSSED_PORT_FH, '<', $BUSSED_PORT_FILE_PATH or die "[Err] : Cannot open $BUSSED_PORT_FILE_PATH...$!";
    my @file = <$BUSSED_PORT_FH>;
    close $BUSSED_PORT_FH;

    $file[-1] =~ s/,//g;
    print $WRAPPER_BB_FH "  $_" foreach @file;
}

# -----------------------------------------------------------------------------
# Connect bit-blasted ports to the wrapper
# -----------------------------------------------------------------------------
sub process_bb_ports_link {
    open $BB_PORT_FH, '<', $BB_PORT_FILE_PATH or die "[Err] : Cannot open $BB_PORT_FILE_PATH...$!";
    my @file = <$BB_PORT_FH>;
    close $BB_PORT_FH;

    $file[-1] =~ s/,//g;
    foreach my $line (@file) {
        chomp $line;
        print $WRAPPER_BB_FH "    .$line ($line),\n";
    }
}

# -----------------------------------------------------------------------------
# Modify the input file as per requirements
# -----------------------------------------------------------------------------
sub modify_input_file {
    open my $IN, '<', $INPUT_FILE_PATH or die "[Err] : Cannot open $INPUT_FILE_PATH...$!";
    open my $OUT, '>', $OUTPUT_FILE_PATH or die "[Err] : Cannot open $OUTPUT_FILE_PATH...$!";
    open my $EXTRACT_FH, '>', $EXTRACTED_SIGNALS_FILE or die "[Err] : Cannot open $EXTRACTED_SIGNALS_FILE...$!";

    my $inside_module = 0;
    my $inside_port_list = 0;

    while (my $line = <$IN>) {
        chomp $line;

        if ($line =~ /module\s+$MODULE_NAME/) {
            $inside_module = 1;
            print $OUT "$line\n";
            next;
        }
        if ($inside_module && $line =~ /\);/) {
            print $OUT join("\n", @bussed_ports), "\n";
            print $OUT "$line\n";
            $inside_port_list = 0;
            next;
        }
        if ($inside_module && $line =~ /endmodule/) {
            $inside_module = 0;
        }

        if ($line =~ /wire\s+\\(\S+\[\d+:\d+\]\S+);/) {
            print $EXTRACT_FH "$1\n";
            next;
        }

        print $OUT "$line\n";
    }

    close $IN;
    close $OUT;
    close $EXTRACT_FH;
}

# -----------------------------------------------------------------------------
# Main execution
# -----------------------------------------------------------------------------
generate_bitblaster_wrapper();
modify_input_file();
print "[Done] : Bit-Blaster wrapper generated and input file modified.\n";
