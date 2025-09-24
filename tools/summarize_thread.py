# tools/summarize_thread_node.py
from typing import TypedDict, Dict, Any
from openai import OpenAI
from utils.secrets_loader import load_secrets
import os


# ---- State Definition ----
class State(TypedDict, total=False):
    text: str
    intent: str
    result: str
    channel_id: str
    thread_ts: str


# ---- Load Secrets & Init OpenAI ----
try:
    secrets = load_secrets()
except Exception as e:
    raise RuntimeError(f"Failed to load secrets for OpenAI: {e}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---- LangGraph Node ----
def summarize_thread_node(state: State, slack_client: Any) -> State:
    """
    LangGraph node: Summarize a Slack thread using GPT-4o.

    Args:
        state: Current workflow state (must include channel_id, thread_ts)
        slack_client: Slack WebClient (passed from listener)

    Returns:
        Updated state with summary in state["result"]
    """

    channel_id = state.get("channel_id")
    thread_ts = state.get("thread_ts")

    # 1. Fetch messages in the thread
    replies = slack_client.conversations_replies(
        channel=channel_id,
        ts=thread_ts
    )

    messages = [m.get("text", "") for m in replies.get("messages", []) if "text" in m]

    if not messages:
        summary = "⚠️ No messages found in this thread to summarize."
        slack_client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=summary)
        state["result"] = summary
        return state

    # 2. Ask GPT-4o for summary
    system_prompt = """
    You are a helpful assistant. Summarize the following Slack thread clearly and concisely.
    Highlight main points, decisions, and action items if any.
    """

    user_content = "\n".join([f"- {m}" for m in messages])

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    )

    summary = response.choices[0].message.content.strip()

    # 3. Post back into Slack thread
    slack_client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text=f"📄 *Thread Summary:*\n{summary}"
    )

    # 4. Update state
    state["result"] = summary
    return state
