from slack_listener.listener import SlackListener

if __name__ == "__main__":
    listener = SlackListener()
    listener.start_listening()
