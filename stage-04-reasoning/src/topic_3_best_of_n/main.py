"""
Self-consistency counts votes. Best-of-N is different: it generates N
candidates and uses a separate verifier to score each one, picking the
highest scorer, rather than trusting whichever answer is most common.
This matters when wrong answers can still be the majority, or when
there is no simple way to vote because every candidate's phrasing
differs even when correct.

The verifier itself needs no API call and is fully testable offline,
unlike the generation step, which does.
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

PROBLEM = "Write a single Python expression that computes the sum of squares from 1 to 10."
EXPECTED_VALUE = sum(i * i for i in range(1, 11))  # 385, known ahead of time


def verify_expression(candidate_text: str) -> tuple[bool, str]:
    """
    The verifier: try evaluating each candidate line as a real Python
    expression, checking the result against the known correct answer.
    This is deterministic and needs no model at all, which is exactly
    what makes it trustworthy as a scorer.

    Two things this has to get right, found by testing against
    hand-crafted candidates before trusting this function:
    1. sum() and range() must actually be usable, or every correct
       answer using them would wrongly fail.
    2. A line must contain real computation (an operator or a function
       call), or a response that just states "the answer is 385" with
       no expression at all would wrongly pass.
    """
    safe_builtins = {"sum": sum, "range": range}
    has_computation = re.compile(r"[\+\-\*/]|sum\(|range\(")

    lines_to_try = candidate_text.strip().split("\n") + [candidate_text.strip()]
    # also strip common markdown code fence markers
    lines_to_try = [ln.strip().strip("`").replace("python", "", 1).strip() for ln in lines_to_try]

    for line in lines_to_try:
        if not line or not has_computation.search(line):
            continue
        try:
            result = eval(line, {"__builtins__": safe_builtins}, {})
            if result == EXPECTED_VALUE:
                return True, f"'{line}' evaluates to {result}, correct"
        except Exception:
            continue
    return False, "no expression in this response evaluated to the correct value"


def main() -> None:
    client = LLMClient()

    print(f"Problem: {PROBLEM}")
    print(f"Known correct value, computed ahead of time: {EXPECTED_VALUE}\n")

    n = 5
    candidates = []
    print(f"Generating {n} candidates:\n")
    for i in range(1, n + 1):
        response = client.chat(prompt=PROBLEM, temperature=0.8, max_tokens=100)
        candidates.append(response.text.strip())
        print(f"  Candidate {i}: {response.text.strip()[:80]}")

    print("\nScoring every candidate with the verifier:\n")
    best = None
    for i, candidate in enumerate(candidates, 1):
        passed, detail = verify_expression(candidate)
        print(f"  Candidate {i}: {'PASS' if passed else 'FAIL'} ({detail})")
        if passed and best is None:
            best = candidate

    if best:
        print(f"\nBest-of-{n} result: {best[:100]}")
    else:
        print(f"\nNone of the {n} candidates verified correctly. This happens, "
              f"and it is itself a useful signal that the problem or the "
              f"prompt needs adjustment.")

    print(
        "\nThe verifier here is a real evaluator, not a trained model, "
        "specifically because this task (does an expression compute to a "
        "known value) has a checkable, deterministic answer. That is exactly "
        "the kind of task best-of-N with a verifier is suited for."
    )


if __name__ == "__main__":
    main()
