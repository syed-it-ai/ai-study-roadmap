"""
Topics 1, 3, and 4 are fully offline, pure logic, no API call. Topic 2
calls a live model to demonstrate its point and is meant to be run and
read, same honest limitation as every stage so far.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_1_golden_dataset.main import GoldenDataset
from src.topic_3_ci_eval_gate.main import property_checks, run_eval_suite
from src.topic_4_checkpoint_recovery.main import (
    save_checkpoint, load_checkpoint, clear_checkpoint, CHECKPOINT_FILE, CRASH_FLAG_FILE,
)


# --- topic 1: golden dataset ---

def test_dataset_starts_empty():
    dataset = GoldenDataset()
    assert dataset.summary()["total_entries"] == 0


def test_adding_an_entry_increments_version():
    dataset = GoldenDataset()
    dataset.add_from_production_failure("input", "expected", "incident_1")
    assert dataset.version == 1


def test_each_entry_traces_back_to_a_real_incident():
    dataset = GoldenDataset()
    dataset.add_from_production_failure("input", "expected", "incident_1")
    assert dataset.entries[0]["source"] == "incident_1"


def test_dataset_grows_with_multiple_additions():
    dataset = GoldenDataset()
    dataset.add_from_production_failure("a", "b", "incident_1")
    dataset.add_from_production_failure("c", "d", "incident_2")
    assert len(dataset.entries) == 2


# --- topic 3: CI eval gate ---

def test_valid_response_passes_all_checks():
    response = {"category": "billing", "summary": "short summary", "urgency": "low"}
    assert property_checks(response) == []


def test_invalid_category_is_caught():
    response = {"category": "not_a_real_category", "summary": "test"}
    failures = property_checks(response)
    assert any("category" in f for f in failures)


def test_missing_required_field_is_caught():
    response = {"summary": "has no category field"}
    failures = property_checks(response)
    assert any("missing required field: category" in f for f in failures)


def test_oversized_summary_is_caught():
    response = {"category": "technical", "summary": "x" * 300}
    failures = property_checks(response)
    assert any("exceeds 200 characters" in f for f in failures)


def test_suite_reports_correct_pass_fail_counts():
    cases = [
        {"category": "billing", "summary": "ok"},
        {"category": "invalid_value", "summary": "bad"},
    ]
    results = run_eval_suite(cases)
    assert results[0]["passed"] is True
    assert results[1]["passed"] is False


# --- topic 4: checkpoint recovery ---

def test_checkpoint_round_trips_correctly():
    clear_checkpoint()
    save_checkpoint(3, ["step1", "step2", "step3"])
    loaded = load_checkpoint()
    assert loaded["step"] == 3
    assert len(loaded["history"]) == 3
    clear_checkpoint()


def test_load_checkpoint_with_no_file_returns_zero_state():
    clear_checkpoint()
    loaded = load_checkpoint()
    assert loaded["step"] == 0
    assert loaded["history"] == []


def test_clear_checkpoint_removes_the_file():
    save_checkpoint(1, ["a"])
    clear_checkpoint()
    assert not os.path.exists(CHECKPOINT_FILE)
    assert not os.path.exists(CRASH_FLAG_FILE)
