# state.py
from typing import TypedDict, Optional, Dict

class State(TypedDict, total=False):
    text: str
    intent: str
    response: Optional[str]
    file_metadata: Optional[Dict]
    channel_id: str
    thread_ts: str
