# graph/workflow.py
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from nodes.classify_node import classify_node
from tools.summarize_thread import summarize_thread_node
from tools.lookup import lookup_node
from tools.publish import publish_node

# Shared state schema
State = Dict[str, Any]

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
        # Add a fallback response
        state["result"] = f"⚠️ Unknown intent: {intent}"
        return END

def build_graph():
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("classify", classify_node)
    graph.add_node("summarize_thread", summarize_thread_node)
    graph.add_node("lookup", lookup_node)
    graph.add_node("publish", publish_node)

    # Entry point
    graph.set_entry_point("classify")

    # Route after classify
    graph.add_conditional_edges("classify", route_based_on_intent)

    # End nodes
    graph.add_edge("summarize_thread", END)
    graph.add_edge("lookup", END)
    graph.add_edge("publish", END)

    return graph.compile()
