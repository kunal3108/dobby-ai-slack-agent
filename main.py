# main.py
import json
from slack_listener.listener import SlackListener
from nodes.classify import classify
from tools.routers import handle_intent   # new: router for executing tools

def query_processor(user_query, client, channel_id, thread_ts):
    """
    Entry point for processing a Slack message.
    """
    # Step 1: Build state
    state = {"text": user_query, "intent": None, "result": None}

    # Step 2: Classify intent (with channel context)
    state = classify(state, channel_id=channel_id)
    print(f"🔍 Classified intent: {state['intent']}")

    # Step 3: Route to appropriate tool
    state = handle_intent(state, client, channel_id, thread_ts)

    # Step 4: Return response
    return {"success": True, "response": state.get("result")}


if __name__ == "__main__":
    # Example allowed channel(s)
    ALLOWED_CHANNELS = ["C099UK7HF2A"]

    # Instantiate listener with query_processor
    listener = SlackListener(
        allowed_channels=ALLOWED_CHANNELS,
        query_processor=query_processor
    )

    print("🤖 Donna AI Slack Agent is live with classification + tools...")
    listener.start_listening()
