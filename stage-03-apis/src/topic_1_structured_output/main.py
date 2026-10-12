"""
Ask a model to return JSON by just asking nicely, and eventually it adds
a sentence before the brackets, or uses a field name you did not ask
for, or returns a number as a string. Structured output with strict
mode removes the guessing: the model is physically blocked from
generating a token that would break the schema, not just checked
afterward.

Confirmed for this project: Groq's strict mode (true constrained
decoding) covers a specific model list, which includes this project's
own default, openai/gpt-oss-120b. If you ever change LLM_MODEL, check
whether strict mode still applies before trusting this.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["billing", "technical", "account", "other"],
        },
        "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high"],
        },
        "summary": {
            "type": "string",
            "description": "One sentence summarising the issue",
        },
    },
    "required": ["category", "urgency", "summary"],
    "additionalProperties": False,
}


def main() -> None:
    client = LLMClient()

    ticket_text = (
        "I was charged twice for my subscription this month and I need "
        "this fixed before my card gets charged again next week."
    )

    prompt = f"Classify this support ticket: {ticket_text}"

    print(f"Ticket: {ticket_text}\n")
    print("Calling with strict: true (constrained decoding)...\n")

    response = client.structured_chat(
        prompt=prompt,
        json_schema=TICKET_SCHEMA,
        schema_name="ticket_classification",
    )

    print("Raw response text (should be valid JSON matching the schema exactly):")
    print(response.text)

    import json
    parsed = json.loads(response.text)
    print(f"\nParsed category: {parsed['category']}")
    print(f"Parsed urgency:  {parsed['urgency']}")
    print(f"Parsed summary:  {parsed['summary']}")

    print(
        "\nNotice what is guaranteed here and what is not. The category is "
        "guaranteed to be one of the four allowed values, never anything else, "
        "because the schema restricts it. Whether 'billing' is actually the "
        "*correct* category is a separate question the schema cannot answer. "
        "Shape is guaranteed. Correctness of the content is still on you."
    )


if __name__ == "__main__":
    main()
