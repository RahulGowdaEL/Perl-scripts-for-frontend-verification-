#!/usr/bin/env python3
import json
import random
import re
import datetime
import os
import sys
import subprocess
import shlex
from typing import Dict, List, Optional, Callable, Any

class VLSIChatbot:
    def __init__(self, config_path: str = "vlsi_config.json"):
        """
        Initialize the VLSI chatbot with configuration
        :param config_path: Path to JSON configuration file
        """
        print("Initializing VLSI Engineer Chatbot...")
        self.load_config(config_path)
        self.context = {}
        self.history = []
        self.plugins = self.load_plugins()
        self.setup_initial_state()
        print(f"VLSI Chatbot '{self.config.get('name', 'VLSI_Bot')}' ready!")
        print("Type 'quit' or 'exit' to end the conversation.")
        print("Type 'help' to see available commands.")
        
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            print(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using default configuration.")
            self.config = {
                "name": "VLSI_Bot",
                "default_responses": [
                    "I'm not sure how to respond to that.",
                    "Could you please rephrase that VLSI-related question?",
                    "I'm specialized in VLSI tasks. Can you ask me something related to chip design?"
                ],
                "plugins": [
                    "synthesis",
                    "simulation",
                    "layout",
                    "verification",
                    "power_analysis",
                    "timing_analysis"
                ],
                "personality": {
                    "tone": "technical",
                    "response_length": "detailed"
                },
                "scripts": {},
                "tools_path": {
                    "dc_shell": "/synopsys/dc/bin/dc_shell",
                    "vcs": "/synopsys/vcs/bin/vcs",
                    "icc2": "/synopsys/icc2/bin/icc2",
                    "pt": "/synopsys/pt/bin/pt_shell",
                    "perl": "/usr/bin/perl",
                    "python": "/usr/bin/python3"
                }
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            sys.exit(1)
    
    def load_plugins(self) -> Dict[str, Callable]:
        """Load and initialize VLSI plugins"""
        plugins = {}
        
        # Built-in VLSI plugins
        plugins['synthesis'] = self.handle_synthesis
        plugins['simulation'] = self.handle_simulation
        plugins['layout'] = self.handle_layout
        plugins['verification'] = self.handle_verification
        plugins['power_analysis'] = self.handle_power_analysis
        plugins['timing_analysis'] = self.handle_timing_analysis
        plugins['help'] = self.handle_help
        plugins['greetings'] = self.handle_greetings
        plugins['farewell'] = self.handle_farewell
        
        # Load custom plugins from config
        for plugin_name in self.config.get('plugins', []):
            try:
                plugin_path = f"plugins/{plugin_name}.py"
                if not os.path.exists(plugin_path):
                    print(f"Plugin file {plugin_path} not found, using built-in handler")
                    continue
                    
                # Add the plugins directory to Python path
                if 'plugins' not in sys.path:
                    sys.path.insert(0, 'plugins')
                
                # Import the plugin module
                module = __import__(plugin_name)
                plugins[plugin_name] = module.handle
                print(f"Loaded plugin: {plugin_name}")
            except ImportError as e:
                print(f"Warning: Failed to load plugin {plugin_name}: {e}")
        
        return plugins
    
    def setup_initial_state(self) -> None:
        """Initialize chatbot state"""
        self.context = {
            'user': {'name': None, 'role': 'vlsi_engineer', 'project': None},
            'conversation': {'topic': None, 'step': 0},
            'design': {'current_stage': 'unknown', 'last_action': None},
            'system': {'last_action': None, 'tools_available': self.check_tools()}
        }
    
    def check_tools(self) -> Dict[str, bool]:
        """Check which VLSI tools are available in the system"""
        tools_available = {}
        for tool, path in self.config.get('tools_path', {}).items():
            tools_available[tool] = os.path.exists(path)
        return tools_available
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate response
        :param user_input: User's message
        :return: Bot's response
        """
        # Clean the input
        user_input = user_input.strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            return "EXIT"
        
        # Add to history
        self.history.append({'user': user_input, 'time': datetime.datetime.now()})
        
        # Check for scripts first
        script_response = self.check_scripts(user_input)
        if script_response:
            return script_response
        
        # Try plugins
        for plugin_name, handler in self.plugins.items():
            response = handler(user_input, self.context)
            if response:
                return response
        
        # Fallback to pattern matching or default
        return self.fallback_response(user_input)
    
    def check_scripts(self, user_input: str) -> Optional[str]:
        """
        Check if input matches any script patterns
        :param user_input: User's message
        :return: Response if script matched, None otherwise
        """
        for script_name, script_config in self.config.get('scripts', {}).items():
            for pattern in script_config.get('patterns', []):
                if re.search(pattern, user_input, re.IGNORECASE):
                    # Execute script actions
                    return self.execute_script(script_name, script_config)
        return None
    
    def execute_script(self, script_name: str, script_config: Dict) -> str:
        """
        Execute a script's actions
        :param script_name: Name of the script
        :param script_config: Script configuration
        :return: Generated response
        """
        responses = script_config.get('responses', [])
        actions = script_config.get('actions', [])
        
        # Execute actions
        for action in actions:
            self.execute_action(action)
        
        # Update context
        self.context['system']['last_action'] = script_name
        if 'context_updates' in script_config:
            self.update_context(script_config['context_updates'])
        
        # Return random response from options
        return random.choice(responses) if responses else ""
    
    def execute_action(self, action: Dict) -> None:
        """Execute a single action"""
        action_type = action.get('type')
        
        if action_type == 'set_context':
            self.context[action['key']] = action['value']
        elif action_type == 'run_script':
            self.run_script(action['script_path'], action.get('args', []))
        elif action_type == 'call_tool':
            self.call_tool(action['tool'], action.get('args', []))
        elif action_type == 'store_data':
            self.store_data(action['key'], action['value'])
    
    def run_script(self, script_path: str, args: List[str]) -> str:
        """Run a shell, Python, or Perl script"""
        if not os.path.exists(script_path):
            return f"Error: Script not found at {script_path}"
        
        try:
            if script_path.endswith('.sh'):
                result = subprocess.run(['bash', script_path] + args, 
                                      capture_output=True, text=True, timeout=300)
            elif script_path.endswith('.py'):
                result = subprocess.run([self.config['tools_path']['python'], script_path] + args, 
                                      capture_output=True, text=True, timeout=300)
            elif script_path.endswith('.pl'):
                result = subprocess.run([self.config['tools_path']['perl'], script_path] + args, 
                                      capture_output=True, text=True, timeout=300)
            else:
                return f"Error: Unsupported script type: {script_path}"
            
            if result.returncode == 0:
                return f"Script executed successfully. Output: {result.stdout}"
            else:
                return f"Script failed. Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Script execution timed out"
        except Exception as e:
            return f"Error executing script: {str(e)}"
    
    def call_tool(self, tool: str, args: List[str]) -> str:
        """Call a VLSI tool (dc_shell, vcs, icc2, etc.)"""
        if tool not in self.config.get('tools_path', {}):
            return f"Error: Tool {tool} not configured"
        
        tool_path = self.config['tools_path'][tool]
        if not os.path.exists(tool_path):
            return f"Error: Tool not found at {tool_path}"
        
        try:
            result = subprocess.run([tool_path] + args, 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return f"Tool {tool} executed successfully. Output: {result.stdout[:500]}..."  # Limit output length
            else:
                return f"Tool {tool} failed. Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Error: {tool} execution timed out"
        except Exception as e:
            return f"Error executing {tool}: {str(e)}"
    
    def update_context(self, updates: Dict) -> None:
        """Update conversation context"""
        for key, value in updates.items():
            keys = key.split('.')
            current = self.context
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
    
    def fallback_response(self, user_input: str) -> str:
        """Generate a response when no specific handler matches"""
        # Try to extract entities for context
        self.extract_entities(user_input)
        
        # Use default responses
        return random.choice(self.config['default_responses'])
    
    def extract_entities(self, user_input: str) -> None:
        """Extract entities from user input to update context"""
        # Project name extraction
        project_match = re.search(r"project[\s\w]+([\w_]+)", user_input, re.IGNORECASE)
        if project_match:
            self.context['user']['project'] = project_match.group(1)
        
        # Design stage extraction
        stages = ['synthesis', 'simulation', 'layout', 'verification', 'power', 'timing']
        for stage in stages:
            if stage in user_input.lower():
                self.context['design']['current_stage'] = stage
                break
    
    # Built-in VLSI plugin handlers
    def handle_synthesis(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle synthesis-related queries"""
        syn_keywords = ["synthesis", "dc_shell", "design compiler", "compile", "gate-level"]
        if any(keyword in user_input.lower() for keyword in syn_keywords):
            if context['system']['tools_available'].get('dc_shell', False):
                return "I can help with synthesis tasks. Would you like to: \n" \
                       "1. Run synthesis with a specific script\n" \
                       "2. Check synthesis constraints\n" \
                       "3. Generate reports\n" \
                       "Please specify your synthesis task."
            else:
                return "Design Compiler is not available in your system. " \
                       "I can still help with synthesis concepts and scripts."
        return None
    
    def handle_simulation(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle simulation-related queries"""
        sim_keywords = ["simulation", "vcs", "verilog", "testbench", "waveform", "fsdb"]
        if any(keyword in user_input.lower() for keyword in sim_keywords):
            if context['system']['tools_available'].get('vcs', False):
                return "I can help with simulation tasks. Would you like to: \n" \
                       "1. Run RTL simulation\n" \
                       "2. Run gate-level simulation\n" \
                       "3. Generate waveforms\n" \
                       "4. Check coverage\n" \
                       "Please specify your simulation task."
            else:
                return "VCS is not available in your system. " \
                       "I can still help with simulation concepts and scripts."
        return None
    
    def handle_layout(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle layout-related queries"""
        layout_keywords = ["layout", "icc2", "innovus", "placement", "routing", "floorplan"]
        if any(keyword in user_input.lower() for keyword in layout_keywords):
            if context['system']['tools_available'].get('icc2', False):
                return "I can help with layout tasks. Would you like to: \n" \
                       "1. Create floorplan\n" \
                       "2. Run placement\n" \
                       "3. Run routing\n" \
                       "4. Generate DEF/LEF\n" \
                       "Please specify your layout task."
            else:
                return "ICC2/Innovus is not available in your system. " \
                       "I can still help with layout concepts and scripts."
        return None
    
    def handle_verification(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle verification-related queries"""
        verif_keywords = ["verification", "formal", "lvs", "drc", "erc", "equivalence"]
        if any(keyword in user_input.lower() for keyword in verif_keywords):
            return "I can help with verification tasks. Would you like to: \n" \
                   "1. Run LVS (Layout vs Schematic)\n" \
                   "2. Run DRC (Design Rule Check)\n" \
                   "3. Run formal verification\n" \
                   "4. Check equivalence\n" \
                   "Please specify your verification task."
        return None
    
    def handle_power_analysis(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle power analysis queries"""
        power_keywords = ["power", "ptpx", "primetime", "vcd", "saif", "power analysis"]
        if any(keyword in user_input.lower() for keyword in power_keywords):
            if context['system']['tools_available'].get('pt', False):
                return "I can help with power analysis tasks. Would you like to: \n" \
                       "1. Run power analysis with PrimeTime\n" \
                       "2. Generate power reports\n" \
                       "3. Create switching activity files\n" \
                       "Please specify your power analysis task."
            else:
                return "PrimeTime is not available in your system. " \
                       "I can still help with power analysis concepts."
        return None
    
    def handle_timing_analysis(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle timing analysis queries"""
        timing_keywords = ["timing", "sta", "setup", "hold", "slack", "sdc"]
        if any(keyword in user_input.lower() for keyword in timing_keywords):
            if context['system']['tools_available'].get('pt', False):
                return "I can help with timing analysis tasks. Would you like to: \n" \
                       "1. Run STA (Static Timing Analysis)\n" \
                       "2. Check setup/hold violations\n" \
                       "3. Generate timing reports\n" \
                       "4. Create constraints\n" \
                       "Please specify your timing analysis task."
            else:
                return "PrimeTime is not available in your system. " \
                       "I can still help with timing analysis concepts."
        return None
    
    def handle_help(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle help requests"""
        if "help" in user_input.lower():
            return "I'm a VLSI Engineer Chatbot. I can help with: \n" \
                   "- Synthesis (Design Compiler)\n" \
                   "- Simulation (VCS)\n" \
                   "- Layout (ICC2/Innovus)\n" \
                   "- Verification (LVS/DRC)\n" \
                   "- Power Analysis (PrimeTime)\n" \
                   "- Timing Analysis (STA)\n" \
                   "- Running scripts (Shell, Python, Perl)\n" \
                   "- Automating repetitive tasks\n\n" \
                   "Try commands like: \n" \
                   "'run synthesis for my design', \n" \
                   "'check timing violations', \n" \
                   "'run verification', \n" \
                   "'help with power analysis'"
        return None
    
    def handle_greetings(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle greeting messages"""
        greetings = ["hi", "hello", "hey", "greetings", "howdy"]
        if any(word in user_input.lower() for word in greetings):
            name = context['user']['name'] or "Engineer"
            return f"Hello {name}! I'm your VLSI assistant. How can I help with your chip design today?"
        return None
    
    def handle_farewell(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle farewell messages"""
        farewells = ["bye", "goodbye", "see you", "farewell", "see ya"]
        if any(word in user_input.lower() for word in farewells):
            name = context['user']['name'] or "Engineer"
            return f"Goodbye {name}! Happy designing! Remember to check your constraints and run verification."
        return None


def main():
    """Main function to run the VLSI chatbot"""
    # Check if config file exists, create if not
    if not os.path.exists("vlsi_config.json"):
        print("Creating default VLSI config file...")
        default_config = {
            "name": "VLSI_Bot",
            "default_responses": [
                "I'm not sure how to respond to that.",
                "Could you please rephrase that VLSI-related question?",
                "I'm specialized in VLSI tasks. Can you ask me something related to chip design?"
            ],
            "plugins": [
                "synthesis",
                "simulation",
                "layout",
                "verification",
                "power_analysis",
                "timing_analysis"
            ],
            "personality": {
                "tone": "technical",
                "response_length": "detailed"
            },
            "scripts": {
                "run_synthesis": {
                    "patterns": [
                        "run synthesis",
                        "start synthesis",
                        "synthesize design"
                    ],
                    "responses": [
                        "Running synthesis with default constraints...",
                        "Starting synthesis process...",
                        "Initiating design compilation..."
                    ],
                    "actions": [
                        {
                            "type": "run_script",
                            "script_path": "scripts/synthesis.sh",
                            "args": ["-design", "my_design"]
                        }
                    ]
                }
            },
            "tools_path": {
                "dc_shell": "/synopsys/dc/bin/dc_shell",
                "vcs": "/synopsys/vcs/bin/vcs",
                "icc2": "/synopsys/icc2/bin/icc2",
                "pt": "/synopsys/pt/bin/pt_shell",
                "perl": "/usr/bin/perl",
                "python": "/usr/bin/python3"
            }
        }
        
        with open("vlsi_config.json", "w") as f:
            json.dump(default_config, f, indent=2)
        
        # Create scripts directory
        os.makedirs("scripts", exist_ok=True)
        os.makedirs("plugins", exist_ok=True)
        
        # Create sample synthesis script
        with open("scripts/synthesis.sh", "w") as f:
            f.write("""#!/bin/bash
# Sample synthesis script
echo "Starting synthesis process for design: $2"
echo "Reading constraints..."
echo "Compiling design..."
echo "Synthesis complete!"
""")
        os.chmod("scripts/synthesis.sh", 0o755)
    
    # Initialize and run the chatbot
    bot = VLSIChatbot()
    
    # Interactive loop
    while True:
        try:
            user_input = input("VLSI> ").strip()
            if not user_input:
                continue
                
            response = bot.process_input(user_input)
            
            if response == "EXIT":
                print("Goodbye! Happy tapeout!")
                break
                
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Happy tapeout!")
            break
        except EOFError:
            print("\n\nGoodbye! Happy tapeout!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
