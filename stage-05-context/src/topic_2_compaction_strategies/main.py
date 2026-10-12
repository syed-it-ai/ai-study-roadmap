"""
A conversation keeps growing. Eventually it has to be cut down to fit
the context window. Three strategies, compared directly on the same
growing conversation. The two mechanical strategies need no API call
at all and are fully testable offline. Summarization, the third, does
need a real call, since it requires the model to actually compress
meaning, not just select or discard turns.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()


def estimate_tokens(text: str) -> int:
    """Rough estimate, about 4 characters per token in English, enough
    for comparing strategies relative to each other."""
    return max(1, len(text) // 4)


def keep_everything(turns: list) -> list:
    """The naive default: never drop anything. Fully offline."""
    return turns


def sliding_window(turns: list, keep_last_n: int) -> list:
    """Keep only the most recent N turns, drop everything older.
    Fully offline, purely mechanical."""
    return turns[-keep_last_n:]


def summarize_old_turns(client, turns: list, keep_recent_n: int):
    """Summarize everything except the most recent N turns into one
    compact message. This is the one strategy that needs a real call,
    since compressing meaning is not something slicing a list can do."""
    if len(turns) <= keep_recent_n:
        return turns
    old_turns = turns[:-keep_recent_n]
    recent_turns = turns[-keep_recent_n:]
    old_text = "\n".join(f"{t['role']}: {t['content']}" for t in old_turns)
    prompt = f"Summarize this conversation history in two sentences, keeping only facts that would matter later:\n\n{old_text}"
    response = client.chat(prompt=prompt, temperature=0.3, max_tokens=100)
    summary_turn = {"role": "system", "content": f"Earlier conversation summary: {response.text.strip()}"}
    return [summary_turn] + recent_turns


def total_tokens(turns: list) -> int:
    return sum(estimate_tokens(t["content"]) for t in turns)


def main() -> None:
    # A conversation that has grown to 10 turns.
    conversation = [
        {"role": "user", "content": "I'm having trouble resetting my password."},
        {"role": "assistant", "content": "I can help with that. Are you locked out of your account entirely?"},
        {"role": "user", "content": "No, I can log in but the reset email never arrives."},
        {"role": "assistant", "content": "Let's check your spam folder first, and confirm the email on file is correct."},
        {"role": "user", "content": "Checked spam, nothing there. The email on file is my work email."},
        {"role": "assistant", "content": "Try updating to a personal email instead, work filters sometimes block these."},
        {"role": "user", "content": "Updated it to my personal email. Still nothing after five minutes."},
        {"role": "assistant", "content": "That's unusual. Let me escalate this to check if our email service has an outage."},
        {"role": "user", "content": "Okay. Also, separately, can I change my display name while we wait?"},
        {"role": "user", "content": "Did the reset email ever get sent on your end?"},
    ]

    print(f"Full conversation: {len(conversation)} turns, {total_tokens(conversation)} estimated tokens\n")

    kept_all = keep_everything(conversation)
    print(f"Keep everything:      {len(kept_all)} turns, {total_tokens(kept_all)} tokens")

    windowed = sliding_window(conversation, keep_last_n=4)
    print(f"Sliding window (last 4): {len(windowed)} turns, {total_tokens(windowed)} tokens")
    print(f"  Lost from view: the original password reset detail (work vs personal email)")

    client = LLMClient()
    summarized = summarize_old_turns(client, conversation, keep_recent_n=4)
    print(f"Summarize + keep last 4: {len(summarized)} turns, {total_tokens(summarized)} tokens")
    print(f"  Summary generated: {summarized[0]['content']}")

    print(
        "\nThe sliding window is cheapest and needs no model call, but it "
        "silently drops the fact that the email was already switched from "
        "work to personal, information the next turn ('did it get sent?') "
        "still depends on. Summarization costs one extra call but keeps that "
        "fact alive in compressed form. Neither strategy is universally "
        "correct, the choice depends on whether the dropped detail still "
        "matters to what comes next."
    )


if __name__ == "__main__":
    main()
