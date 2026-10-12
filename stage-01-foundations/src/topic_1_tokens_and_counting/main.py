"""
What this shows you: a token is not a word and not a character.
It is whatever chunk the model's tokenizer decided to treat as one unit,
and you only find out how a given piece of text was chopped up by asking.

We're not installing a separate tokenizer library for this. Every API
response already tells you how many tokens your input and output used,
in the `usage` field. That's the real number you're billed on, so it's
the one worth looking at directly.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()


def show_token_count(client: LLMClient, label: str, text: str) -> None:
    response = client.chat(prompt=text, max_tokens=5)
    words = len(text.split())
    print(f"\n{label}")
    print(f"  text:            {text!r}")
    print(f"  word count:      {words}")
    print(f"  prompt tokens:   {response.prompt_tokens}")
    if response.prompt_tokens and words:
        ratio = response.prompt_tokens / words
        print(f"  tokens per word: {ratio:.2f}")


def main() -> None:
    client = LLMClient()

    # Plain English. Expect tokens-per-word to land close to 1.3, the
    # commonly-quoted average for everyday English text.
    show_token_count(client, "Ordinary sentence", "The cat sat quietly by the window.")

    # A made-up word the tokenizer almost certainly never saw as a whole
    # unit during training. Watch the tokens-per-word ratio jump.
    show_token_count(client, "An unfamiliar / made-up word", "Zylbraqtonium is not a real chemical.")

    # A number. This is the one worth paying attention to: long numbers
    # often get split in ways that don't respect place value at all,
    # which is a big part of why models fumble arithmetic on big numbers.
    show_token_count(client, "A long number", "The total came to 48213967 exactly.")

    print(
        "\nNotice the ratio is never fixed. It depends on what the text "
        "actually contains, not just how many characters or words it has. "
        "This is also the number your bill is calculated from, every call."
    )


if __name__ == "__main__":
    main()
