"""
Topics 3 and 4 have real offline-testable logic (the verifier functions
themselves need no API call). Topics 1 and 2 call a live model and are
meant to be run and read, same honest limitation as every prior stage.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_3_best_of_n.main import verify_expression, EXPECTED_VALUE
from src.topic_4_prm_vs_orm.main import (
    outcome_reward_score, process_reward_score, verify_step,
    CHAIN_CORRECT_REASONING, CHAIN_WRONG_BUT_LUCKY,
)


# --- topic 3: best-of-N verifier ---

def test_correct_generator_expression_passes():
    ok, _ = verify_expression("sum(i*i for i in range(1, 11))")
    assert ok is True


def test_correct_list_comprehension_passes():
    ok, _ = verify_expression("sum([i**2 for i in range(1,11)])")
    assert ok is True


def test_spelled_out_arithmetic_passes():
    ok, _ = verify_expression("1+4+9+16+25+36+49+64+81+100")
    assert ok is True


def test_bare_number_with_no_computation_fails():
    ok, _ = verify_expression("The answer is 385")
    assert ok is False


def test_wrong_expression_fails():
    ok, _ = verify_expression("sum(range(1, 11))")  # sum, not sum of squares
    assert ok is False


def test_markdown_code_fence_is_handled():
    ok, _ = verify_expression("```python\nsum(i*i for i in range(1,11))\n```")
    assert ok is True


# --- topic 4: PRM vs ORM ---

def test_orm_cannot_distinguish_correct_from_lucky_chain():
    orm_correct = outcome_reward_score(CHAIN_CORRECT_REASONING, 25)
    orm_lucky = outcome_reward_score(CHAIN_WRONG_BUT_LUCKY, 25)
    assert orm_correct["scored_correct"] is True
    assert orm_lucky["scored_correct"] is True  # ORM wrongly scores both the same


def test_prm_distinguishes_correct_from_lucky_chain():
    prm_correct = process_reward_score(CHAIN_CORRECT_REASONING, verify_step)
    prm_lucky = process_reward_score(CHAIN_WRONG_BUT_LUCKY, verify_step)
    assert prm_correct["all_steps_correct"] is True
    assert prm_lucky["all_steps_correct"] is False  # PRM correctly catches the bad steps


def test_prm_flags_the_specific_wrong_steps():
    result = process_reward_score(CHAIN_WRONG_BUT_LUCKY, verify_step)
    wrong_steps = [desc for desc, val, ok in result["steps"] if not ok]
    assert len(wrong_steps) == 2
    assert "Calculate 25% of $40" in wrong_steps
