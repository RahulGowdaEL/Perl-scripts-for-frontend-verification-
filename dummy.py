{
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
