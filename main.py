from slack_listener.listener import SlackListener
import json

if __name__ == "__main__":
    print("🤖 Donna Slack bot is starting...")

    # Instantiate the listener
    listener = SlackListener()

    # Wrap the original handler with extra logging
    original_handler = listener._handle_message_event

    def debug_wrapper(event, say):
        print("\n📩 Incoming Slack event in main.py:")
        try:
            print(json.dumps(event, indent=2))
        except Exception:
            print(event)

        # Call the original logic
        original_handler(event, say)

    # Monkey-patch the handler
    listener._handle_message_event = debug_wrapper

    # Start the listener
    listener.start_listening()
