"""
Self-consistency: generate several independent reasoning paths for the
same question, then take whichever final answer shows up most often.
No extra model needed, no verifier, just counting votes. This works
because on problems with one correct answer, wrong answers tend to
scatter across different wrong values while the correct answer, reached
through different reasoning paths, keeps landing on the same number.
"""

import sys
import os
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

PROBLEM = (
    "A store had 150 items. They sold 40% of them on Monday, then "
    "received a shipment of 50 more items on Tuesday. How many items "
    "does the store have now? Answer with just the final number."
)
# Worked by hand so the correct answer is known ahead of time:
# 150 - (150 * 0.40) = 150 - 60 = 90, then 90 + 50 = 140.

N_SAMPLES = 7


def extract_number(text: str) -> str:
    """Pull the first number-looking token out of a response, so answers
    phrased slightly differently still get counted as the same vote."""
    import re
    match = re.search(r"-?\d+\.?\d*", text.replace(",", ""))
    return match.group(0) if match else text.strip()[:30]


def main() -> None:
    client = LLMClient()

    print(f"Problem: {PROBLEM}\n")
    print(f"Sampling {N_SAMPLES} independent reasoning paths at temperature 0.9:\n")

    answers = []
    for i in range(1, N_SAMPLES + 1):
        response = client.chat(prompt=PROBLEM, temperature=0.9, max_tokens=200)
        answer = extract_number(response.text)
        answers.append(answer)
        print(f"  Sample {i}: {answer}")

    votes = Counter(answers)
    winner, count = votes.most_common(1)[0]

    print(f"\nVote tally: {dict(votes)}")
    print(f"\nMajority answer: {winner} ({count} of {N_SAMPLES} samples agree)")

    print(
        "\nIf the samples split across several different numbers, that is "
        "itself useful information: it tells you this specific problem is "
        "harder for the model than it looks, and a single sample would have "
        "had a real chance of being wrong with no warning sign at all."
    )
    print(
        "\nThe cost tradeoff is direct: this used 7 full calls instead of 1. "
        "Self-consistency earns its cost specifically on problems worth "
        "getting right the first time, not on routine requests."
    )


if __name__ == "__main__":
    main()
