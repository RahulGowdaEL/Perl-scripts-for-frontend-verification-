import json
import random
from typing import Dict, List, Optional, Callable, Any
import re
import datetime

class Chatbot:
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the chatbot with configuration
        :param config_path: Path to JSON configuration file
        """
        self.load_config(config_path)
        self.context = {}
        self.history = []
        self.plugins = self.load_plugins()
        self.setup_initial_state()
        
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "name": "CustomBot",
                "default_responses": ["I'm not sure how to respond to that."],
                "plugins": [],
                "personality": {
                    "tone": "friendly",
                    "response_length": "medium"
                },
                "scripts": {}
            }
    
    def load_plugins(self) -> Dict[str, Callable]:
        """Load and initialize plugins"""
        plugins = {}
        
        # Built-in plugins
        plugins['greetings'] = self.handle_greetings
        plugins['farewell'] = self.handle_farewell
        plugins['time'] = self.handle_time_query
        plugins['help'] = self.handle_help
        
        # Load custom plugins from config
        for plugin_name in self.config.get('plugins', []):
            try:
                module = __import__(f"plugins.{plugin_name}", fromlist=['handle'])
                plugins[plugin_name] = module.handle
            except ImportError:
                print(f"Warning: Plugin {plugin_name} not found")
        
        return plugins
    
    def setup_initial_state(self) -> None:
        """Initialize chatbot state"""
        self.context = {
            'user': {'name': None, 'preferences': {}},
            'conversation': {'topic': None, 'step': 0},
            'system': {'last_action': None}
        }
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate response
        :param user_input: User's message
        :return: Bot's response
        """
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
        elif action_type == 'call_api':
            self.call_external_api(action['url'], action.get('params', {}))
        elif action_type == 'store_data':
            self.store_data(action['key'], action['value'])
    
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
        # Simple name extraction
        name_match = re.search(r"(?:my name is|i'm|I am) ([A-Za-z]+)", user_input, re.IGNORECASE)
        if name_match and not self.context['user']['name']:
            self.context['user']['name'] = name_match.group(1)
    
    # Built-in plugin handlers
    def handle_greetings(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle greeting messages"""
        greetings = ["hi", "hello", "hey", "greetings"]
        if any(word in user_input.lower() for word in greetings):
            name = context['user']['name'] or "there"
            return random.choice([
                f"Hello {name}! How can I help you today?",
                f"Hi {name}! What can I do for you?",
                f"Greetings {name}! How may I assist you?"
            ])
        return None
    
    def handle_farewell(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle farewell messages"""
        farewells = ["bye", "goodbye", "see you", "farewell"]
        if any(word in user_input.lower() for word in farewells):
            name = context['user']['name'] or "friend"
            return random.choice([
                f"Goodbye {name}! Have a great day!",
                f"See you later {name}!",
                f"Farewell {name}! Come back anytime!"
            ])
        return None
    
    def handle_time_query(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle time-related queries"""
        time_phrases = ["what time is it", "current time", "what's the time"]
        if any(phrase in user_input.lower() for phrase in time_phrases):
            now = datetime.datetime.now()
            return f"The current time is {now.strftime('%H:%M')}."
        return None
    
    def handle_help(self, user_input: str, context: Dict) -> Optional[str]:
        """Handle help requests"""
        if "help" in user_input.lower():
            return "I can help with various tasks. You can ask me about time, or say hello! " \
                   "My capabilities can be extended through plugins and scripts."
        return None
    
    # External integration methods
    def call_external_api(self, url: str, params: Dict) -> Any:
        """Make API calls to external services"""
        # Implementation would use requests or similar library
        pass
    
    def store_data(self, key: str, value: Any) -> None:
        """Store data persistently"""
        # Implementation would use database or storage system
        pass


{
    "name": "CustomBot",
    "default_responses": [
        "I'm not sure I understand. Could you rephrase that?",
        "That's an interesting point. Could you tell me more?",
        "I'm still learning. Can you ask me something else?"
    ],
    "plugins": ["weather", "calculator"],
    "personality": {
        "tone": "professional",
        "response_length": "medium"
    },
    "scripts": {
        "order_pizza": {
            "patterns": [
                "I want to order a pizza",
                "can I get a pizza",
                "pizza delivery"
            ],
            "responses": [
                "Great! What size pizza would you like? (small, medium, large)",
                "I can help with pizza orders. What size are you thinking?"
            ],
            "actions": [
                {
                    "type": "set_context",
                    "key": "conversation.topic",
                    "value": "pizza_order"
                },
                {
                    "type": "set_context",
                    "key": "conversation.step",
                    "value": 1
                }
            ],
            "context_updates": {
                "current_order": {"item": "pizza", "stage": "size"}
            }
        },
        "book_appointment": {
            "patterns": [
                "I need an appointment",
                "schedule a meeting",
                "book a time"
            ],
            "responses": [
                "I can help schedule appointments. What day works for you?",
                "Let's book that. What's your preferred date?"
            ],
            "actions": [
                {
                    "type": "call_api",
                    "url": "/api/calendar/check_availability"
                }
            ]
        }
    }
}
