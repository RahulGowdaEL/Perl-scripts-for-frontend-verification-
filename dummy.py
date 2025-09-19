#!/bin/bash
# Synthesis automation script for VLSI designs
# Usage: ./synthesis.sh <design_name> <constraint_file>

DESIGN_NAME=${1:-my_design}
CONSTRAINT_FILE=${2:-constraints/default.sdc}

echo "Starting synthesis process for design: $DESIGN_NAME"
echo "Using constraints: $CONSTRAINT_FILE"

# Check if files exist
if [ ! -f "rtl/$DESIGN_NAME.v" ]; then
    echo "Error: RTL file rtl/$DESIGN_NAME.v not found!"
    exit 1
fi

if [ ! -f "$CONSTRAINT_FILE" ]; then
    echo "Error: Constraint file $CONSTRAINT_FILE not found!"
    exit 1
fi

# Create reports directory
mkdir -p reports

# Generate DC script
cat > scripts/"$DESIGN_NAME"_dc.tcl << EOF
set design $DESIGN_NAME
set search_path ". /libs/std_cells"
set target_library "std_cells.db"
set link_library "* std_cells.db"

read_verilog rtl/$DESIGN_NAME.v
current_design $DESIGN_NAME
link

read_sdc $CONSTRAINT_FILE

compile_ultra

write -format verilog -hierarchy -output netlist/${DESIGN_NAME}_gate.v
write_sdc -version 2.1 -output netlist/${DESIGN_NAME}_gate.sdc

report_timing -delay max -max_paths 10 > reports/${DESIGN_NAME}_timing.rpt
report_area > reports/${DESIGN_NAME}_area.rpt
report_power > reports/${DESIGN_NAME}_power.rpt
report_qor > reports/${DESIGN_NAME}_qor.rpt

exit
EOF

# Run Design Compiler
echo "Running Design Compiler..."
dc_shell -f scripts/"$DESIGN_NAME"_dc.tcl

if [ $? -eq 0 ]; then
    echo "Synthesis completed successfully!"
    echo "Reports generated in reports/ directory"
else
    echo "Synthesis failed! Check the logs for errors."
    exit 1
fi
