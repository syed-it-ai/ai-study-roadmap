"""
Topic 1 showed that a schema guarantees shape: the category will always
be one of four allowed values, never something else. What a schema
cannot guarantee is that the content is actually correct. An order ID
that matches the expected format can still refer to an order that does
not exist. This topic separates those two checks cleanly, and the
semantic-check function itself needs no API call at all, so it is
fully testable offline, unlike topics 1 and 2.
"""

import re


def schema_is_valid(record: dict) -> tuple[bool, str]:
    """
    The shape check. Would already be guaranteed by strict mode in a
    real pipeline, written out explicitly here so the two kinds of
    validation are visibly separate steps, not blurred together.
    """
    required = {"order_id", "email", "amount"}
    missing = required - record.keys()
    if missing:
        return False, f"missing fields: {missing}"
    if not isinstance(record["amount"], (int, float)):
        return False, "amount must be a number"
    return True, "shape is valid"


def semantic_is_plausible(record: dict, known_order_ids: set, known_emails: set) -> tuple[bool, str]:
    """
    The content check. No amount of schema enforcement can catch any
    of these. This is deliberately simple logic, not a database call,
    so it can run and be tested with no network at all.
    """
    order_id = record["order_id"]
    email = record["email"]
    amount = record["amount"]

    if not re.match(r"^ORD-\d{4,8}$", order_id):
        return False, f"'{order_id}' does not match the expected order ID pattern"
    if order_id not in known_order_ids:
        return False, f"'{order_id}' matches the pattern but does not exist in our records"
    if email not in known_emails:
        return False, f"'{email}' is not associated with this account"
    if amount <= 0 or amount > 10_000:
        return False, f"amount {amount} is outside a plausible range for a single order"
    return True, "content is plausible"


def main() -> None:
    known_order_ids = {"ORD-4471", "ORD-9902"}
    known_emails = {"priya.k@example.com"}

    test_records = [
        {"order_id": "ORD-4471", "email": "priya.k@example.com", "amount": 49.99},
        {"order_id": "ORD-4471", "email": "priya.k@example.com"},
        {"order_id": "ORD-0001", "email": "priya.k@example.com", "amount": 49.99},
        {"order_id": "ORD-4471", "email": "someone-else@example.com", "amount": 49.99},
        {"order_id": "ORD-4471", "email": "priya.k@example.com", "amount": 999999},
    ]

    for i, record in enumerate(test_records, 1):
        print(f"Record {i}: {record}")
        shape_ok, shape_msg = schema_is_valid(record)
        print(f"  Schema check:   {'PASS' if shape_ok else 'FAIL'} ({shape_msg})")
        if shape_ok:
            content_ok, content_msg = semantic_is_plausible(record, known_order_ids, known_emails)
            print(f"  Semantic check: {'PASS' if content_ok else 'FAIL'} ({content_msg})")
        else:
            print(f"  Semantic check: skipped, shape already failed")
        print()

    print(
        "Record 1 passes both. Record 3 has a well-formed order ID, exactly "
        "the shape a schema would accept, that simply does not exist. A schema "
        "alone would have let it through. Only the semantic check catches it."
    )


if __name__ == "__main__":
    main()
