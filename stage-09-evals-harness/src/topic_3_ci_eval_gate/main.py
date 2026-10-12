"""
Confirmed directly in this project's own main roadmap: an eval that
cannot block a bad merge is decoration, not a safety net. This builds
a real gate, the kind that would actually run in CI, using the actual
mechanism that stops a merge: a non-zero exit code. Fully offline, no
model call needed, since the properties being checked here are
structural, not semantic.
"""

import sys


def property_checks(response: dict) -> list:
    """
    The property-assertion layer from this project's established eval
    ladder: deterministic, structural checks, not semantic judgment.
    Each one is cheap, fast, and either passes or fails with no
    ambiguity.
    """
    failures = []

    if "category" not in response:
        failures.append("missing required field: category")
    elif response["category"] not in {"billing", "technical", "account", "other"}:
        failures.append(f"category '{response.get('category')}' is not one of the allowed values")

    if "summary" not in response:
        failures.append("missing required field: summary")
    elif len(response.get("summary", "")) > 200:
        failures.append("summary exceeds 200 characters")

    if "urgency" in response and response["urgency"] not in {"low", "medium", "high"}:
        failures.append(f"urgency '{response['urgency']}' is not a valid value")

    return failures


def run_eval_suite(test_cases: list) -> dict:
    """Runs every test case through the property checks and reports a
    pass/fail summary, the thing a CI job would actually read."""
    results = []
    for i, case in enumerate(test_cases, 1):
        failures = property_checks(case)
        results.append({"case": i, "passed": len(failures) == 0, "failures": failures})
    return results


def main() -> int:
    """Returns a real exit code. 0 means every case passed, the merge
    can proceed. Non-zero means something failed, and in a real CI
    pipeline this is exactly what blocks the merge from completing."""
    test_cases = [
        {"category": "billing", "summary": "Customer wants a refund for a duplicate charge.", "urgency": "high"},
        {"category": "unknown_category", "summary": "This should fail the category check.", "urgency": "low"},
        {"summary": "This is missing its category field entirely."},
        {"category": "technical", "summary": "A" * 250, "urgency": "medium"},
    ]

    results = run_eval_suite(test_cases)

    print("Eval results:\n")
    all_passed = True
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  Case {r['case']}: {status}")
        for f in r["failures"]:
            print(f"    - {f}")
        if not r["passed"]:
            all_passed = False

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n{passed} of {total} cases passed.")

    if all_passed:
        print("\nAll checks passed. Exit code 0: this would let a real CI pipeline proceed with the merge.")
        return 0
    else:
        print(f"\n{total - passed} case(s) failed. Exit code 1: this would block a real CI pipeline from merging.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n(Actual process exit code: {exit_code})")
    sys.exit(exit_code)
