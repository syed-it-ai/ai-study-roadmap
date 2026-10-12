"""
Topics 2 and 3 have real offline-testable logic. Topics 1 and 4 both
call a live model to demonstrate their point and are meant to be run
and read, same honest limitation as every prior stage.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_2_compaction_strategies.main import (
    keep_everything, sliding_window, estimate_tokens, total_tokens,
)
from src.topic_3_context_tiers.main import ContextAssembler


# --- topic 2: compaction ---

SAMPLE_CONVERSATION = [
    {"role": "user", "content": "First message in the conversation."},
    {"role": "assistant", "content": "First reply."},
    {"role": "user", "content": "Second message."},
    {"role": "assistant", "content": "Second reply."},
    {"role": "user", "content": "Third and most recent message."},
]


def test_keep_everything_drops_nothing():
    result = keep_everything(SAMPLE_CONVERSATION)
    assert len(result) == len(SAMPLE_CONVERSATION)


def test_sliding_window_keeps_only_most_recent():
    result = sliding_window(SAMPLE_CONVERSATION, keep_last_n=2)
    assert len(result) == 2
    assert result[-1]["content"] == "Third and most recent message."


def test_sliding_window_drops_the_oldest_first():
    result = sliding_window(SAMPLE_CONVERSATION, keep_last_n=3)
    contents = [t["content"] for t in result]
    assert "First message in the conversation." not in contents


def test_token_estimate_scales_with_length():
    short = estimate_tokens("hi")
    long = estimate_tokens("hi " * 100)
    assert long > short


def test_total_tokens_sums_across_turns():
    total = total_tokens(SAMPLE_CONVERSATION)
    manual_sum = sum(estimate_tokens(t["content"]) for t in SAMPLE_CONVERSATION)
    assert total == manual_sum


# --- topic 3: context tiers ---

def test_permanent_tier_rejects_content_over_budget():
    assembler = ContextAssembler(permanent_budget=5, retrieved_budget=50, session_budget=50)
    try:
        assembler.set_permanent("This sentence is definitely longer than five tokens worth of budget.")
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_retrieved_tier_evicts_oldest_when_over_budget():
    assembler = ContextAssembler(permanent_budget=50, retrieved_budget=15, session_budget=50)
    assembler.add_retrieved("First chunk added, should be evicted eventually.")
    assembler.add_retrieved("Second chunk, also fairly long.")
    assembler.add_retrieved("Third chunk pushes the budget over the edge.")
    assert "First chunk" not in " ".join(assembler.retrieved_chunks)


def test_session_tier_keeps_most_recent_turn():
    assembler = ContextAssembler(permanent_budget=50, retrieved_budget=50, session_budget=10)
    assembler.add_session_turn("user", "An older turn that should get dropped eventually.")
    assembler.add_session_turn("user", "A newer turn that should survive.")
    remaining = [c for _, c in assembler.session_turns]
    assert "A newer turn that should survive." in remaining


def test_tiers_are_independent_budgets():
    assembler = ContextAssembler(permanent_budget=5, retrieved_budget=5, session_budget=100)
    assembler.add_session_turn("user", "A very long session turn that should not be limited by the tiny permanent or retrieved budgets at all, since each tier has its own separate ceiling.")
    assert len(assembler.session_turns) == 1
