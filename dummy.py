python3 chatbot.py
Initializing VLSI Engineer Chatbot...
Configuration loaded from vlsi_config.json
Traceback (most recent call last):
  File "chatbot.py", line 513, in <module>
    main()
  File "chatbot.py", line 484, in main
    bot = VLSIChatbot()
  File "chatbot.py", line 22, in __init__
    self.plugins = self.load_plugins()
  File "chatbot.py", line 97, in load_plugins
    module = __import__(plugin_name)
  File "plugins/synthesis.py", line 5, in <module>
    def handle(user_input: str, context: dict) -> Optional[str]:
NameError: name 'Optional' is not defined
