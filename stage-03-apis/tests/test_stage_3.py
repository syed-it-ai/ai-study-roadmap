"""
Only topic_3 gets automated tests here. Topics 1, 2, and 4 all call a
real API via structured_chat or chat, and need a live key, which is
not something a test suite should depend on. Run those by hand and
read the output, same as Stage 1's API-dependent topics.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_3_schema_vs_semantic_validation.main import schema_is_valid, semantic_is_plausible

KNOWN_IDS = {"ORD-4471", "ORD-9902"}
KNOWN_EMAILS = {"priya.k@example.com"}


def test_valid_record_passes_schema():
    record = {"order_id": "ORD-4471", "email": "priya.k@example.com", "amount": 49.99}
    ok, _ = schema_is_valid(record)
    assert ok is True


def test_missing_field_fails_schema():
    record = {"order_id": "ORD-4471", "email": "priya.k@example.com"}
    ok, msg = schema_is_valid(record)
    assert ok is False
    assert "amount" in msg


def test_non_numeric_amount_fails_schema():
    record = {"order_id": "ORD-4471", "email": "priya.k@example.com", "amount": "forty"}
    ok, _ = schema_is_valid(record)
    assert ok is False


def test_well_formed_but_unknown_order_id_fails_semantic_check():
    record = {"order_id": "ORD-0001", "email": "priya.k@example.com", "amount": 49.99}
    ok, msg = semantic_is_plausible(record, KNOWN_IDS, KNOWN_EMAILS)
    assert ok is False
    assert "does not exist" in msg


def test_known_order_with_known_email_passes_semantic_check():
    record = {"order_id": "ORD-4471", "email": "priya.k@example.com", "amount": 49.99}
    ok, _ = semantic_is_plausible(record, KNOWN_IDS, KNOWN_EMAILS)
    assert ok is True


def test_mismatched_email_fails_semantic_check():
    record = {"order_id": "ORD-4471", "email": "wrong@example.com", "amount": 49.99}
    ok, msg = semantic_is_plausible(record, KNOWN_IDS, KNOWN_EMAILS)
    assert ok is False
    assert "not associated" in msg


def test_implausible_amount_fails_semantic_check():
    record = {"order_id": "ORD-4471", "email": "priya.k@example.com", "amount": 999999}
    ok, msg = semantic_is_plausible(record, KNOWN_IDS, KNOWN_EMAILS)
    assert ok is False
    assert "outside a plausible range" in msg


def test_malformed_order_id_fails_semantic_check_before_lookup():
    record = {"order_id": "not-an-order-id", "email": "priya.k@example.com", "amount": 49.99}
    ok, msg = semantic_is_plausible(record, KNOWN_IDS, KNOWN_EMAILS)
    assert ok is False
    assert "does not match the expected" in msg
