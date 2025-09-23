from state import State
from openai import OpenAI

client = OpenAI()

def classify(state: State) -> State:
    text = state["text"]

    allowed_intents = [
        "create_jira_ticket",
        "update_jira_ticket",
        "summarize_thread",
        "file summary",
        "publish",
        "lookup"
    ]

    # Ask GPT-4o to classify
    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "You are a classifier. Return only one label from the allowed intents."},
            {"role": "user", "content": f"""
Classify this message into one of:
{", ".join(allowed_intents)}

Message: {text}
            """}
        ],
        max_tokens=10,
        temperature=0
    )

    intent = response.choices[0].message.content.strip()
    state["intent"] = intent if intent in allowed_intents else "unknown"

    return state
