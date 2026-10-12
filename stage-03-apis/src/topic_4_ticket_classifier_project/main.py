"""
The small real project this stage builds toward: a support ticket
classifier that combines everything covered so far. A contract prompt
(topic 2), enforced with a strict schema (topic 1), checked afterward
with a semantic validation layer (topic 3) before anything gets acted
on automatically.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["billing", "technical", "account", "other"]},
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "needs_human_review": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["category", "urgency", "needs_human_review", "summary"],
    "additionalProperties": False,
}


def build_contract_prompt(ticket_text: str) -> str:
    """The contract pattern from topic_2, applied to this specific task."""
    return f"""Classify this support ticket.

category must be exactly one of: billing, technical, account, other
urgency must be exactly one of: low, medium, high
needs_human_review should be true if the ticket mentions anything
  involving money, legal concerns, or an angry or threatening tone
summary must be one plain sentence, no more

Ticket: {ticket_text}"""


def semantic_sanity_check(result: dict, ticket_text: str) -> list:
    """
    The topic_3 layer. The schema already guarantees the shape. This
    checks whether the content actually makes sense for this specific
    ticket, the part no schema can verify on its own.
    """
    warnings = []
    money_words = ["charge", "charged", "refund", "payment", "bill"]
    if any(w in ticket_text.lower() for w in money_words) and result["category"] != "billing":
        warnings.append(
            f"Ticket mentions money-related language but was classified as "
            f"'{result['category']}', not 'billing'. Worth a second look."
        )
    if result["urgency"] == "high" and not result["needs_human_review"]:
        warnings.append(
            "Marked high urgency but not flagged for human review. "
            "That combination is usually worth double-checking."
        )
    return warnings


def main() -> None:
    client = LLMClient()

    tickets = [
        "I was charged twice for my subscription and need this fixed immediately.",
        "The app crashes every time I try to upload a photo.",
    ]

    for ticket_text in tickets:
        print(f"Ticket: {ticket_text}")
        prompt = build_contract_prompt(ticket_text)

        response = client.structured_chat(
            prompt=prompt,
            json_schema=CLASSIFICATION_SCHEMA,
            schema_name="ticket_classification",
        )
        result = json.loads(response.text)

        print(f"  category:            {result['category']}")
        print(f"  urgency:             {result['urgency']}")
        print(f"  needs_human_review:  {result['needs_human_review']}")
        print(f"  summary:             {result['summary']}")

        warnings = semantic_sanity_check(result, ticket_text)
        if warnings:
            print("  Sanity check flagged:")
            for w in warnings:
                print(f"    - {w}")
        else:
            print("  Sanity check: nothing flagged")
        print()

    print(
        "Three layers, stacked: a contract prompt that states the exact fields "
        "wanted, a strict schema that guarantees the shape of what comes back, "
        "and a semantic check that catches content the schema cannot. None of "
        "the three alone is enough. Together they are what a real classifier "
        "needs before its output drives an automatic action."
    )


if __name__ == "__main__":
    main()
