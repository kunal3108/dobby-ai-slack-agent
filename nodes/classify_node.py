# nodes/classify_node.py
from typing import Dict, Any
from langgraph.graph import node
from openai import OpenAI
from utils.context_loader import load_channel_context
from utils.secrets_loader import load_secrets

# Load OpenAI API key once
try:
    secrets = load_secrets()
except Exception as e:
    raise RuntimeError(f"Failed to load secrets for OpenAI: {e}")

client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))

@node
def classify_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: classify the user text into an intent using GPT-4o,
    optionally enriched with channel-specific context.

    Input:
        state["text"] - user message text
        state["channel_id"] (optional) - Slack channel for context

    Output:
        state["intent"] - chosen intent
    """
    text = state.get("text", "").strip()
    if not text:
        state["intent"] = "unknown"
        return state

    channel_id = state.get("channel_id")
    channel_context = load_channel_context(channel_id) if channel_id else ""

    system_prompt = f"""
    You are a classifier.
    Your job is to assign exactly one intent from this list:

    - create_jira_ticket → when user asks to create a Jira ticket
    - update_jira_ticket → when user asks to update an existing Jira ticket
    - summarize_thread → when user asks for a summary of the messages in a Slack thread
    - file summary → when user asks for a summary of a file shared in a Slack thread
    - publish → when user asks to publish data
    - lookup → when user asks to retrieve a data point
    - unknown → if the request does not clearly match any of the above

    Channel Context (may affect classification):
    {channel_context}

    Always return a JSON: {{"intent": "<one_of_the_above>"}}.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Text: {text}"}
            ],
            response_format={"type": "json_object"}
        )

        intent = response.choices[0].message.parsed.get("intent", "unknown")
    except Exception as e:
        intent = "unknown"
        print(f"⚠ classify_node error: {e}")

    state["intent"] = intent
    return state
