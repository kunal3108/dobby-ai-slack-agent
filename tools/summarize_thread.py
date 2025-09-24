# tools/summarize_thread.py
from typing import Dict
from openai import OpenAI

client = OpenAI()

def summarize_thread(state: Dict, slack_client, channel_id: str, thread_ts: str) -> Dict:
    """
    Summarize a Slack thread using GPT-4o and post the summary back to Slack.

    Args:
        state: dictionary holding workflow state
        slack_client: Slack WebClient (from slack_bolt.App.client)
        channel_id: Slack channel ID
        thread_ts: parent thread timestamp

    Returns:
        Updated state with summary text in state["result"]
    """

    # 1. Get all messages in the thread
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

    # 2. Ask GPT-4o for a summary
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

