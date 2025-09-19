import math
import re

def handle(user_input: str, context: dict) -> Optional[str]:
    # Simple arithmetic calculations
    if re.search(r"calculate|what is|compute|math", user_input.lower()):
        try:
            # Extract numbers and operations
            if "+" in user_input:
                parts = user_input.split("+")
                result = float(parts[0].strip()) + float(parts[1].strip())
                return f"The result is {result}"
            elif "-" in user_input:
                parts = user_input.split("-")
                result = float(parts[0].strip()) - float(parts[1].strip())
                return f"The result is {result}"
            # Add more operations as needed
        except:
            return "I couldn't calculate that. Please provide numbers and a simple operation."
    return None
