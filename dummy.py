#!/usr/bin/env python3
import os
import subprocess

def handle(user_input: str, context: dict) -> Optional[str]:
    """
    Handle synthesis-related commands for VLSI designs
    """
    syn_keywords = ["synthesis", "dc_shell", "design compiler", "compile", "gate-level", "synthesize"]
    
    if any(keyword in user_input.lower() for keyword in syn_keywords):
        # Extract design name if mentioned
        design_name = "my_design"
        if "design" in user_input.lower():
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() == "design" and i+1 < len(words):
                    design_name = words[i+1]
                    break
        
        # Check what specific synthesis task is requested
        if "run" in user_input.lower() or "start" in user_input.lower():
            return run_synthesis(design_name, context)
        elif "constraint" in user_input.lower():
            return check_constraints(design_name)
        elif "report" in user_input.lower():
            return generate_reports(design_name)
        else:
            return f"I can help with synthesis tasks for design '{design_name}'. " \
                   "Would you like to run synthesis, check constraints, or generate reports?"
    
    return None

def run_synthesis(design_name: str, context: dict) -> str:
    """Run synthesis process"""
    # Check if Design Compiler is available
    if context['system']['tools_available'].get('dc_shell', False):
        try:
            # Create a simple DC script
            dc_script = f"""
set design {design_name}
read_verilog rtl/{design_name}.v
read_constraints constraints/{design_name}.sdc
compile
write -format verilog -output netlist/{design_name}_gate.v
report_timing > reports/{design_name}_timing.rpt
report_area > reports/{design_name}_area.rpt
report_power > reports/{design_name}_power.rpt
exit
"""
            
            with open(f"scripts/{design_name}_dc.tcl", "w") as f:
                f.write(dc_script)
            
            # Run Design Compiler
            result = subprocess.run([
                context['config']['tools_path']['dc_shell'],
                "-f", f"scripts/{design_name}_dc.tcl"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return f"Synthesis completed for {design_name}! Timing, area, and power reports generated."
            else:
                return f"Synthesis failed for {design_name}. Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Synthesis timed out for {design_name}. Please check your constraints."
        except Exception as e:
            return f"Error running synthesis: {str(e)}"
    else:
        return "Design Compiler is not available. I can help you create synthesis scripts instead."

def check_constraints(design_name: str) -> str:
    """Check synthesis constraints"""
    constraint_file = f"constraints/{design_name}.sdc"
    if os.path.exists(constraint_file):
        with open(constraint_file, 'r') as f:
            constraints = f.read()
        
        # Simple constraint analysis
        clock_count = constraints.count("create_clock")
        max_delay_count = constraints.count("set_max_delay")
        min_delay_count = constraints.count("set_min_delay")
        
        return f"Constraint analysis for {design_name}:\n" \
               f"- {clock_count} clock definitions\n" \
               f"- {max_delay_count} max delay constraints\n" \
               f"- {min_delay_count} min delay constraints\n" \
               "Would you like to see detailed constraints?"
    else:
        return f"Constraint file {constraint_file} not found. Would you like to create one?"

def generate_reports(design_name: str) -> str:
    """Generate synthesis reports"""
    report_files = [
        f"reports/{design_name}_timing.rpt",
        f"reports/{design_name}_area.rpt",
        f"reports/{design_name}_power.rpt"
    ]
    
    existing_reports = [f for f in report_files if os.path.exists(f)]
    
    if existing_reports:
        report_info = "\n".join([f"- {os.path.basename(f)}" for f in existing_reports])
        return f"Available reports for {design_name}:\n{report_info}\n" \
               "Which report would you like to analyze?"
    else:
        return f"No reports found for {design_name}. Would you like to run synthesis first?"
