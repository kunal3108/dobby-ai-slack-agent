from langgraph.graph import StateGraph, END
from state import State
from nodes.classify import classify
from tools.create_jira_ticket import create_jira_ticket
from tools.update_jira_ticket import update_jira_ticket
from tools.summarize_thread import summarize_thread

# Build the graph
builder = StateGraph(State)

builder.add_node("classify", classify)
builder.add_node("create_jira_ticket", create_jira_ticket)
builder.add_node("update_jira_ticket", update_jira_ticket)
builder.add_node("summarize_thread", summarize_thread)

# Routing
builder.add_edge("classify", "create_jira_ticket", condition=lambda s: s["intent"]=="create_jira_ticket")
builder.add_edge("classify", "update_jira_ticket", condition=lambda s: s["intent"]=="update_jira_ticket")
builder.add_edge("classify", "summarize_thread", condition=lambda s: s["intent"]=="summarize_thread")
builder.add_edge("classify", END, condition=lambda s: s["intent"] in ["lookup", "file summary", "publish"])

builder.add_edge("create_jira_ticket", END)
builder.add_edge("update_jira_ticket", END)
builder.add_edge("summarize_thread", END)

graph = builder.compile()
