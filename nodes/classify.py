from typing import Dict
from openai import OpenAI
from utils.context_loader import load_channel_context   
from utils.secrets_loader import load_secrets
import os

# Ensure OpenAI key is loaded
load_secrets()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify(state: Dict, channel_id: str = None) -> Dict:
    """
    Classify the user text into an intent using GPT-4o,
    enriched with channel-specific context.
    """
    text = state["text"]
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

    Channel Context (may affect classification):
    {channel_context}

    Always return a JSON: {{"intent": "<one_of_the_above>"}}.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Text: {text}"}
        ],
        response_format={"type": "json_object"}
    )

    intent = response.choices[0].message.parsed["intent"]
    state["intent"] = intent
    return state
