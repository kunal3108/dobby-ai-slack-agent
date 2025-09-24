# main.py
from slack_listener.listener import SlackListener
from graph.workflow import build_graph

# Build LangGraph once
graph = build_graph()

def query_processor(user_query, client, channel_id, thread_ts):
    """
    Entry point for SlackListener → LangGraph.
    Passes user text and Slack context into the workflow.
    """
    # Build initial state with all required fields
    state = {
        "text": user_query,
        "intent": None,
        "result": None,
        "channel_id": channel_id,
        "thread_ts": thread_ts,
        "slack_client": client,   # pass Slack WebClient directly
    }

    # Run through LangGraph
    final_state = graph.invoke(state)

    return {"success": True, "response": final_state.get("result")}

if __name__ == "__main__":
    ALLOWED_CHANNELS = ["C099UK7HF2A"]

    listener = SlackListener(
        allowed_channels=ALLOWED_CHANNELS,
        query_processor=query_processor
    )

    print("🤖 Dobby AI Slack Agent is live with LangGraph workflow...")
    listener.start_listening()
