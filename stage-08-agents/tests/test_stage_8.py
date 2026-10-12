"""
The workflow half of topic 1, all of topic 2's parsing logic, and all
of topic 3 are fully offline. The agent/LLM-driven halves of topics 1,
2, and 4 call a live model and are meant to be run and read.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_1_workflow_vs_agent.main import workflow_lookup_order, ORDERS
from src.topic_2_react_loop.main import parse_action
from src.topic_3_tool_idempotency.main import (
    PaymentProcessor, IdempotentPaymentProcessor, simulate_agent_retry_on_timeout,
)


# --- topic 1: the workflow half, fully deterministic ---

def test_workflow_handles_a_known_shipped_order():
    result = workflow_lookup_order("ORD-1001")
    assert "shipped" in result
    assert "1Z999AA1" in result


def test_workflow_uses_placeholder_for_missing_tracking():
    result = workflow_lookup_order("ORD-1002")
    assert "NO TRACKING AVAILABLE" in result


def test_workflow_gives_a_bare_failure_for_unknown_order():
    result = workflow_lookup_order("ORD-9999")
    assert "not found" in result


# --- topic 2: parsing logic ---

def test_parse_action_extracts_tool_and_argument():
    tool, arg = parse_action("Thought: check it.\nAction: check_inventory(widget)")
    assert tool == "check_inventory"
    assert arg == "widget"


def test_parse_action_returns_none_for_final_answer():
    tool, arg = parse_action("Thought: done.\nFinal Answer: Yes, in stock.")
    assert tool is None


def test_parse_action_returns_none_for_malformed_response():
    tool, arg = parse_action("I am not following the format at all.")
    assert tool is None


# --- topic 3: idempotency ---

def test_naive_processor_charges_multiple_times_on_retry():
    processor = PaymentProcessor()
    results = simulate_agent_retry_on_timeout(lambda: processor.charge("cust_1", 10.0), attempts=3)
    assert len(processor.charges) == 3


def test_idempotent_processor_charges_only_once_on_retry():
    processor = IdempotentPaymentProcessor()
    results = simulate_agent_retry_on_timeout(
        lambda: processor.charge("cust_1", 10.0, idempotency_key="order_1"), attempts=3
    )
    assert len(processor.processed_keys) == 1


def test_idempotent_processor_marks_duplicates():
    processor = IdempotentPaymentProcessor()
    processor.charge("cust_1", 10.0, idempotency_key="order_1")
    second = processor.charge("cust_1", 10.0, idempotency_key="order_1")
    assert "duplicate" in second.get("note", "")


def test_different_idempotency_keys_are_treated_as_different_charges():
    processor = IdempotentPaymentProcessor()
    processor.charge("cust_1", 10.0, idempotency_key="order_1")
    processor.charge("cust_1", 10.0, idempotency_key="order_2")
    assert len(processor.processed_keys) == 2
