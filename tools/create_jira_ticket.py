# tools/create_jira_ticket.py
from state import State

def create_jira_ticket(state: State) -> State:
    state["result"] = f"✅ Created Jira ticket for: {state['text']}"
    return state

