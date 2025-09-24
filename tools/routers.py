# tools/routers.py
from nodes.create_jira_ticket import create_jira_ticket
from nodes.update_jira_ticket import update_jira_ticket
from nodes.summarize_thread import summarize_thread

def handle_intent(state, client, channel_id, thread_ts):
    """
    Route classified state to the right tool.
    """
    intent = state["intent"]

    if intent == "create_jira_ticket":
        state = create_jira_ticket(state)
    elif intent == "update_jira_ticket":
        state = update_jira_ticket(state)
    elif intent == "summarize_thread":
        state = summarize_thread(state, client, channel_id, thread_ts)
    elif intent in ["lookup", "file summary", "publish"]:
        state["result"] = f"ℹ️ Intent '{intent}' detected but handler not implemented yet."
    else:
        state["result"] = "⚠️ Unknown intent."

    return state
