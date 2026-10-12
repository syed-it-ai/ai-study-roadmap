"""
A "contract" prompt states exactly what fields you want, in what format,
with an example, instead of describing the task and hoping the model
infers the shape you had in mind. This runs the same extraction task
three times with a vague prompt and three times with a contract-style
prompt, so you can see the reliability difference directly instead of
being told it exists.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

TEXT = "Contact Priya at priya.k@example.com or call her at 555-0182 if the order is late."

VAGUE_PROMPT = f"Pull out the contact info from this: {TEXT}"

CONTRACT_PROMPT = f"""Extract contact information from the text below.

Return exactly this format, nothing else, no explanation before or after:
name: <value>
email: <value>
phone: <value>

If a field is not present in the text, write "none" for that field.

Text: {TEXT}"""


def run_n_times(client: LLMClient, prompt: str, n: int) -> None:
    for i in range(1, n + 1):
        response = client.chat(prompt=prompt, temperature=0.7, max_tokens=100)
        print(f"  [{i}] {response.text.strip()[:150]}")


def main() -> None:
    client = LLMClient()

    print("VAGUE PROMPT, asked three times:")
    print(f'"{VAGUE_PROMPT}"\n')
    run_n_times(client, VAGUE_PROMPT, 3)

    print("\nCONTRACT PROMPT, asked three times:")
    print(f'"{CONTRACT_PROMPT[:80]}..."\n')
    run_n_times(client, CONTRACT_PROMPT, 3)

    print(
        "\nLook at the shape of each set of three answers, not just the content. "
        "The vague prompt's three answers likely differ in format: a sentence, "
        "a list, maybe labeled fields, maybe not. The contract prompt's three "
        "answers should land in the same shape every time, because the prompt "
        "specified the shape instead of leaving it to be inferred."
    )
    print(
        "\nThis matters most the moment something downstream has to parse the "
        "output automatically. A human can read either version. Code parsing "
        "the response needs the shape to be predictable, not just correct."
    )


if __name__ == "__main__":
    main()
