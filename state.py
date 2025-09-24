# state.py
from typing import TypedDict

class State(TypedDict, total=False):
    text: str       # user query
    intent: str     # classifier output
    result: str     # tool output
    channel_id: str
    thread_ts: str
