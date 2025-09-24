# nodes/classify_node.py
from typing import Dict
from openai import OpenAI
from utils.context_loader import load_channel_context
from utils.secrets_loader import load_secrets
import os

# Load OpenAI key once
secrets = load_secrets()
client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))

def classify_node(state: Dict, channel_id: str = None) -> Dict:
    """
    LangGraph node: classify user query and extract tool-specific variables.
    """
    text = state["text"]
    channel_context = load_channel_context(channel_id) if channel_id else ""

    system_prompt = f"""
    You are a classifier and information extractor.
    - First, classify the user intent into one of:
      [create_jira_ticket, update_jira_ticket, summarize_thread,
       file summary, publish, lookup, plot]
    - Then, if intent is related to 1A_Charts:
        * lookup → extract 'metric_name' and 'dates'
        * plot   → extract 'metric_name' and 'dates'
        * publish → extract 'target_date'
    - Dates must be in dd/mm/yy format.
    - If information is missing, set value to null.

    Channel Context (may affect classification):
    {channel_context}

    Respond only in JSON:
    {{
      "intent": "<one_of_above>",
      "metric_name": "<str_or_null>",
      "dates": ["dd/mm/yy", ...] or null,
      "target_date": "<dd/mm/yy_or_null>"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",  # cheaper, faster
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )

    parsed = response.choices[0].message.parsed

    # Update state
    state["intent"] = parsed.get("intent")
    state["metric_name"] = parsed.get("metric_name")
    state["dates"] = parsed.get("dates")
    state["target_date"] = parsed.get("target_date")

    return state
