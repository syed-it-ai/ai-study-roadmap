"""
A single fact, buried at the start, middle, and end of the same long
context, asked about with the exact same question each time. If the
model were using its context evenly, position would not matter. It
does. This is a well-documented, currently unsolved phenomenon called
"lost in the middle" (position bias) and, at a broader scale across
noisier long contexts, "context rot."

Confirmed current as of this build: research through mid-2026 is
explicit that no production model, including ones with million-token
windows, has fully eliminated this. A bigger context window does not
fix it.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

TARGET_FACT = "The emergency generator's access code is 4817."
QUESTION = "What is the emergency generator's access code? Answer with just the number."

FILLER_PARAGRAPHS = [
    "The quarterly maintenance schedule was updated to reflect new vendor availability.",
    "Parking permits for the east lot renew automatically each January.",
    "The cafeteria will be closed for renovations during the second week of the month.",
    "New hires complete orientation in the main conference room on their first Monday.",
    "The recycling program now accepts a wider range of plastic materials.",
    "Building access hours were extended to accommodate the night shift team.",
    "The fire drill originally scheduled for Tuesday was moved to Thursday.",
    "Visitor badges must be returned to the front desk before leaving the building.",
    "The IT helpdesk ticket system was migrated to a new platform last month.",
    "Conference room bookings now require approval from a team lead.",
    "The company picnic has been tentatively set for the third weekend of summer.",
    "Desk assignments on the third floor were reorganized to open up a new team space.",
]


def build_context(fact_position: str) -> str:
    """Insert the target fact at the start, middle, or end of the filler text."""
    paragraphs = FILLER_PARAGRAPHS.copy()
    if fact_position == "start":
        paragraphs.insert(0, TARGET_FACT)
    elif fact_position == "middle":
        paragraphs.insert(len(paragraphs) // 2, TARGET_FACT)
    elif fact_position == "end":
        paragraphs.append(TARGET_FACT)
    return "\n\n".join(paragraphs)


def main() -> None:
    client = LLMClient()

    results = {}
    for position in ["start", "middle", "end"]:
        context = build_context(position)
        prompt = f"{context}\n\n{QUESTION}"
        response = client.chat(prompt=prompt, temperature=0.0, max_tokens=20)
        answer = response.text.strip()
        correct = "4817" in answer
        results[position] = (answer, correct)
        print(f"Fact placed at: {position:7s} -> answer: {answer!r:30s} correct: {correct}")

    print(
        "\nSame fact, same question, same total context. Only the position "
        "changed. If the middle result is wrong or hedged while start and end "
        "are confident and correct, that is the U-shaped pattern research has "
        "documented since 2023 and confirmed repeatedly through 2026, on this "
        "project's own model, not just in a paper."
    )
    print(
        "\nThis is also why 'just put everything in the context window' is not "
        "a complete RAG strategy. Where retrieved content gets placed in the "
        "prompt matters as much as whether it was retrieved at all."
    )


if __name__ == "__main__":
    main()
