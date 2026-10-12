"""
A reasoning model can "think" before answering, generating internal
reasoning tokens that never get shown to you directly but shape the
final answer. reasoning_effort controls how much of that thinking
happens: low, medium, or high.

Confirmed on Groq's own documentation: this parameter is supported
specifically on openai/gpt-oss-20b and openai/gpt-oss-120b, this
project's own default model, not every model Groq hosts.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

HARD_PROBLEM = (
    "A train leaves station A at 60 mph heading toward station B, 300 "
    "miles away. At the same moment, a train leaves station B heading "
    "toward station A at 40 mph, but it stops for 15 minutes exactly "
    "halfway through its journey. How long after the first train "
    "departs do the two trains meet?"
)


def main() -> None:
    client = LLMClient()

    print(f"Problem: {HARD_PROBLEM}\n")

    for effort in ["low", "medium", "high"]:
        print(f"--- reasoning_effort = {effort} ---")
        start = time.time()
        response = client.reasoning_chat(prompt=HARD_PROBLEM, reasoning_effort=effort)
        elapsed = time.time() - start

        print(f"Time taken: {elapsed:.1f}s")
        print(f"Completion tokens used: {response.completion_tokens}")
        print(f"Answer: {response.text.strip()[:300]}")
        print()

    print(
        "Compare completion tokens and time across the three runs, not just "
        "the final answer. Higher effort should spend more tokens and more "
        "time working through the problem before answering. On a genuinely "
        "tricky problem like this one, that extra work is what separates a "
        "right answer from a confidently wrong one."
    )
    print(
        "\nThe real decision this parameter represents: low effort for simple "
        "lookups and classification, higher effort specifically for problems "
        "with multiple steps where an early mistake compounds. Using high "
        "effort on every request multiplies cost and latency for no benefit "
        "on the easy ones."
    )


if __name__ == "__main__":
    main()
