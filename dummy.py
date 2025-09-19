{
    "name": "LinuxChatBot",
    "default_responses": [
        "I'm not sure I understand. Could you rephrase that?",
        "That's an interesting point. Could you tell me more?",
        "I'm still learning. Can you ask me something else?"
    ],
    "plugins": [],
    "personality": {
        "tone": "friendly",
        "response_length": "medium"
    },
    "scripts": {
        "order_pizza": {
            "patterns": [
                "I want to order a pizza",
                "can I get a pizza",
                "pizza delivery",
                "order pizza"
            ],
            "responses": [
                "Great! What size pizza would you like? (small, medium, large)",
                "I can help with pizza orders. What size are you thinking?",
                "Pizza! Excellent choice. What size would you like?"
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
        }
    }
}
