# nodes/classify.py
from state import State

def classify(state: State) -> State:
    text = state["text"].lower()

    if "create a jira" in text or "create a ticket" in text:
        state["intent"] = "create_jira_ticket"
    elif "update an-" in text or "update " in text:
        state["intent"] = "update_jira_ticket"
    elif "summarize this thread" in text or "summarize" in text:
        state["intent"] = "summarize_thread"
    elif "file summary" in text:
        state["intent"] = "file summary"
    elif "publish" in text:
        state["intent"] = "publish"
    else:
        state["intent"] = "lookup"

    return state

