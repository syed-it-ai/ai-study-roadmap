"""
AGENTS.md is the cross-tool standard for giving a coding agent persistent
project context, confirmed as of mid-2026 to be read natively by over
20 tools and used across more than 60,000 repositories. Claude Code
uses its own, richer CLAUDE.md format but reads AGENTS.md as a fallback
when no CLAUDE.md is present.

This runs the same coding request twice: once with no project
instructions, once with a small AGENTS.md's content prepended, so the
behavior difference is something you see, not something you're told
about.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

SAMPLE_AGENTS_MD = """# AGENTS.md

## Code style
- Every function must have a docstring and full type hints.
- Never use bare `except:`. Always catch a specific exception.
- Prefer early returns over nested if/else.

## Testing
- Every new function needs at least one test case alongside it.
"""

TASK = "Write a Python function that divides two numbers and returns the result."


def main() -> None:
    client = LLMClient()

    print("Request with no project instructions:\n")
    plain_response = client.chat(prompt=TASK, temperature=0.3, max_tokens=250)
    print(plain_response.text.strip())

    print("\n" + "=" * 60)
    print("\nSame request, with this AGENTS.md prepended:\n")
    print(SAMPLE_AGENTS_MD)

    guided_prompt = f"{SAMPLE_AGENTS_MD}\n\nFollow the conventions above. Task: {TASK}"
    guided_response = client.chat(prompt=guided_prompt, temperature=0.3, max_tokens=250)
    print("Response:\n")
    print(guided_response.text.strip())

    print(
        "\nLook for the specific things the AGENTS.md asked for: a docstring, "
        "type hints, a specific exception caught instead of a bare except, "
        "and a test case alongside the function. The plain request has no "
        "reason to include any of these. The guided one has explicit "
        "instructions to.",
    )
    print(
        "\nThis file is read once, automatically, at the start of every "
        "session in a tool that supports it. Nobody has to remember to paste "
        "these conventions into every single request by hand."
    )


if __name__ == "__main__":
    main()
