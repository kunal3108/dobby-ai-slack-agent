# main.py
from langgraph.graph import StateGraph
from state import State
from nodes.slack_listener import SlackListenerNode
from nodes.classify import classify  # your GPT-4o intent classifier

graph = StateGraph(State)
graph.add_node("classify", classify)
graph.set_entry_point("classify")

workflow = graph.compile()

slack_listener = SlackListenerNode(workflow)
slack_listener.start()
