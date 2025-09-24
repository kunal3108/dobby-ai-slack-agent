# nodes/classify.py
from typing import Dict
from openai import OpenAI

client = OpenAI()

def classify(state: Dict) -> Dict:
    """
    Classify the user text into an intent using GPT-4o.
    """
    text = state["text"]

    system_prompt = """
    You are a classifier. 
    Your job is to assign exactly one intent from this list:

    - create_jira_ticket → when user asks to create a Jira ticket
    - update_jira_ticket → when user asks to update an existing Jira ticket
    - summarize_thread → when user asks for a summary of the messages in a Slack thread
    - file summary → when user asks for a summary of a file shared in a Slack thread
    - publish → when user asks to publish data
    - lookup → when user asks to retrieve a data point

    Always return a JSON: {"intent": "<one_of_the_above>"}.
    """

    response = client.chat.completions.create(
        model="gpt-4o",   # cheap + fast
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Text: {text}"}
        ],
        response_format={"type": "json_object"}
    )

    intent = response.choices[0].message.parsed["intent"]
    state["intent"] = intent
    return state
