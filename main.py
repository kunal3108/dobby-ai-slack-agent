from slack_listener.listener import SlackListener
from graph.classifier_graph import graph

def langgraph_query_processor(user_query, client, channel_id, thread_ts):
    result = graph.invoke({"text": user_query})
    return {
        "success": True,
        "response": result.get("result", f"🤖 Intent classified as {result['intent']}")
    }

if __name__ == "__main__":
    ALLOWED_CHANNELS = ["C099UK7HF2A"]  # Replace with your channel IDs

    listener = SlackListener(
        allowed_channels=ALLOWED_CHANNELS,
        query_processor=langgraph_query_processor
    )

    print("Bot configuration:", listener.get_bot_info())
    listener.start_listening()

