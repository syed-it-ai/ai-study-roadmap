"""
What this shows you: the model's weights never change between these calls.
Nothing is being retrained or updated while this script runs. What changes
is which word gets picked at each step, because picking is partly random.

Run this once and read the output before changing anything. The point
is to actually see the variation, not just be told it happens.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

PROMPT = "In one short sentence, describe what a database index is for."


def demo_requests_carry_no_weights() -> None:
    """
    Offline. Shows that between two calls, nothing about the model's state
    travels over the wire at all — so there is nothing here that could
    change the weights. They live on the provider's machines, not in
    your script, and no call you make can touch them.
    """
    import json
    import requests

    sent_bodies = []

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [{"message": {"content": "(demo answer, not from a real model)"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }

    real_post = requests.post

    def capture_post(url, **kwargs):
        sent_bodies.append(json.dumps(kwargs.get("json"), sort_keys=True))
        return FakeResponse()

    # Temporary stand-in key for this offline demo only. Restored below
    # so the live part afterwards still sees the real environment.
    previous_key = os.environ.get("LLM_API_KEY")
    os.environ["LLM_API_KEY"] = "demo-key-not-real"
    client = LLMClient(provider="groq")

    requests.post = capture_post
    try:
        client.chat(prompt=PROMPT, temperature=0.9, max_tokens=60)
        client.chat(prompt=PROMPT, temperature=0.9, max_tokens=60)
    finally:
        requests.post = real_post
        if previous_key is None:
            del os.environ["LLM_API_KEY"]
        else:
            os.environ["LLM_API_KEY"] = previous_key

    print("Part 0 — what actually travels over the wire (offline demo)")
    print(f"  request body, call 1: {sent_bodies[0]}")
    print(f"  request body, call 2: {sent_bodies[1]}")
    print(f"  byte-identical:       {sent_bodies[0] == sent_bodies[1]}")
    print(
        "\n  Every call sends the same prompt, the same model name, the same "
        "settings — and nothing else. No weights travel in either direction, "
        "so the model answering call 2 is bit-for-bit the same model that "
        "answered call 1. The 'frozen' in frozen weights is literal."
    )


def run_n_times(client: LLMClient, temperature: float, n: int) -> None:
    print(f"\ntemperature = {temperature}")
    for i in range(1, n + 1):
        response = client.chat(prompt=PROMPT, temperature=temperature, max_tokens=60)
        print(f"  [{i}] {response.text.strip()}")


def main() -> None:
    demo_requests_carry_no_weights()

    try:
        client = LLMClient()
    except ValueError as exc:
        print(f"\nLive demo skipped: {exc}")
        print("Put a free key in your .env (see the README), then run this again.")
        return

    print(f'\nPrompt sent every time, unchanged: "{PROMPT}"')

    try:
        # Default/higher temperature: expect genuinely different wording each time.
        run_n_times(client, temperature=0.9, n=3)

        # Temperature near zero: expect the answers to converge, though "near
        # deterministic" is the honest phrase. Some providers still show tiny
        # variation even at temperature 0, which is itself worth noticing.
        run_n_times(client, temperature=0.0, n=3)
    except Exception as exc:  # no internet, bad key, provider down — say so plainly
        print(f"\nLive demo could not reach the provider: {exc}")
        print("Check your internet connection and your key in .env, then run again.")
        return

    print(
        "\nThe weights behind every one of those calls were identical. "
        "Temperature controls how much the model is allowed to deviate "
        "from its single most likely next word at each step, not whether "
        "the model 'knows' something differently each time."
    )


if __name__ == "__main__":
    main()
