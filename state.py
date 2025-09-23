# state.py
from typing import TypedDict

class State(TypedDict):
    text: str
    intent: str
    result: str | None
