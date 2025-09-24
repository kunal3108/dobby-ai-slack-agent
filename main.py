#main.py

from slack_listener.listener import SlackListener
from graph.workflow import build_graph

# Build LangGraph
graph = build_graph()

def query_processor(user_query, client, channel_id, thread_ts):
    # Pass Slack message into LangGraph
    state = {"text": user_query, "intent": None, "result": None}
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
