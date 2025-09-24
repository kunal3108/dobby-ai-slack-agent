# graph/workflow.py
from typing import Dict
from langgraph.graph import StateGraph
from nodes.classify import classify
from tools.summarize_thread import summarize_thread
from tools.lookup import lookup_tool
from tools.publish import publish_tool

# Shared state schema
State = Dict[str, str]

def route_based_on_intent(state: State) -> str:
    """Decide next node based on classified intent."""
    intent = state.get("intent")
    if intent == "summarize_thread":
        return "summarize_thread"
    elif intent == "lookup":
        return "lookup"
    elif intent == "publish":
        return "publish"
    else:
        return "end"   # fallback

def build_graph():
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("classify", classify)
    graph.add_node("summarize_thread", summarize_thread)
    graph.add_node("lookup", lookup_tool)
    graph.add_node("publish", publish_tool)

    # Entry point
    graph.set_entry_point("classify")

    # Route after classify
    graph.add_conditional_edges("classify", route_based_on_intent)

    # End nodes
    graph.set_finish_point("summarize_thread")
    graph.set_finish_point("lookup")
    graph.set_finish_point("publish")

    return graph.compile()
