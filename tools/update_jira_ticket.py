# tools/update_jira_ticket.py
from state import State

def update_jira_ticket(state: State) -> State:
    state["result"] = f"✅ Updated Jira with: {state['text']}"
    return state

