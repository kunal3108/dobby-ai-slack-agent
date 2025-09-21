from slack_listener.listener import SlackListener

if __name__ == "__main__":
    print("🤖 Slack bot is starting...")
    listener = SlackListener()
    listener.start_listening()
