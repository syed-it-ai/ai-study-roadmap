"""
Every topic in Stage 11 is pure logic with no API call, the same
property as Stages 2 and 10, since no vision or voice API is available
in this sandbox. Every topic gets full automated test coverage.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_1_turn_taking_state_machine.main import TurnTakingMachine, State
from src.topic_2_latency_budget.main import compute_pipeline_latency, identify_bottleneck
from src.topic_3_document_extraction.main import extract_fields, semantic_validate
from src.topic_4_speech_architecture_decision.main import recommend_architecture


# --- topic 1: turn-taking state machine ---

def test_normal_turn_ends_back_at_listening():
    machine = TurnTakingMachine()
    machine.user_starts_speaking()
    machine.semantic_end_of_turn_detected()
    machine.agent_starts_responding()
    machine.agent_finishes_responding()
    assert machine.state == State.LISTENING


def test_barge_in_interrupts_agent_speaking():
    machine = TurnTakingMachine()
    machine.user_starts_speaking()
    machine.semantic_end_of_turn_detected()
    machine.agent_starts_responding()
    assert machine.state == State.AGENT_SPEAKING
    machine.user_starts_speaking()  # barge-in
    assert machine.state == State.USER_SPEAKING


def test_barge_in_is_logged_distinctly_from_a_normal_turn_start():
    machine = TurnTakingMachine()
    machine.user_starts_speaking()
    machine.semantic_end_of_turn_detected()
    machine.agent_starts_responding()
    machine.user_starts_speaking()
    last_transition = machine.transition_log[-1]
    assert "BARGE-IN" in last_transition[2]


def test_end_of_turn_only_fires_while_user_is_speaking():
    machine = TurnTakingMachine()
    machine.semantic_end_of_turn_detected()  # called with no one speaking
    assert machine.state == State.LISTENING  # should have no effect


# --- topic 2: latency budget ---

def test_pipeline_latency_sums_all_stages():
    result = compute_pipeline_latency(100, 200, 50, 30)
    assert result["total_ms"] == 380


def test_bottleneck_identifies_the_largest_stage():
    result = compute_pipeline_latency(100, 400, 50, 30)
    name, ms = identify_bottleneck(result["stages"])
    assert ms == 400


def test_speech_to_speech_is_faster_than_cascaded_in_this_comparison():
    cascaded = compute_pipeline_latency(150, 400, 200, 80)
    speech_to_speech = compute_pipeline_latency(0, 300, 0, 80)
    assert speech_to_speech["total_ms"] < cascaded["total_ms"]


# --- topic 3: document extraction ---

def test_extract_fields_pulls_all_expected_values():
    text = "INVOICE #INV-123\nDate: 2026-01-01\nBill To: Test Co\nAmount Due: $100.00\nDue Date: 2026-02-01"
    fields = extract_fields(text)
    assert fields["invoice_number"] == "INV-123"
    assert fields["amount_due"] == "100.00"


def test_missing_field_is_none_not_a_crash():
    text = "INVOICE #INV-123\nDate: 2026-01-01"
    fields = extract_fields(text)
    assert fields["amount_due"] is None


def test_semantic_validation_catches_due_date_before_invoice_date():
    fields = {"invoice_number": "X", "date": "2026-09-15", "bill_to": "Y",
              "amount_due": "100.00", "due_date": "2026-09-01"}
    warnings = semantic_validate(fields)
    assert any("earlier than the invoice date" in w for w in warnings)


def test_semantic_validation_catches_unusually_large_amount():
    fields = {"invoice_number": "X", "date": "2026-09-15", "bill_to": "Y",
              "amount_due": "124750.00", "due_date": "2026-10-01"}
    warnings = semantic_validate(fields)
    assert any("unusually large" in w for w in warnings)


def test_semantic_validation_passes_a_clean_invoice():
    fields = {"invoice_number": "X", "date": "2026-09-15", "bill_to": "Y",
              "amount_due": "1247.50", "due_date": "2026-10-15"}
    warnings = semantic_validate(fields)
    assert warnings == []


# --- topic 4: architecture decision ---

def test_debugging_need_routes_to_cascaded_even_if_latency_matters():
    result = recommend_architecture(True, True, False, False)
    assert "Cascaded" in result


def test_voice_cloning_need_routes_to_cascaded():
    result = recommend_architecture(True, False, False, True)
    assert "Cascaded" in result


def test_pure_latency_priority_routes_to_speech_to_speech():
    result = recommend_architecture(True, False, False, False)
    assert "Speech-to-speech" in result


def test_no_strong_requirement_defaults_to_cascaded():
    result = recommend_architecture(False, False, False, False)
    assert "cascaded" in result.lower()
