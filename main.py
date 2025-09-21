from slack_listener.listener import SlackListener
if __name__ == "__main__":
    # Example configuration
    ALLOWED_CHANNELS = ['C099UK7HF2A']  # Replace with your channel IDs
    
    # Create listener with default processor
    listener = SlackListener(
        allowed_channels=ALLOWED_CHANNELS,
        #query_processor=create_default_query_processor()
    )
    
    # Print configuration
    print("Bot configuration:", listener.get_bot_info())
    
    # Start listening
    listener.start_listening() 
