"""
Any tool with a real-world side effect needs to survive being called
twice with the same input, confirmed directly in this project's own
main roadmap as a named Stage 8 topic. Agents retry failed calls
constantly: timeouts, transient errors, rate limits. That's normal and
usually correct. The problem is a tool with no concept of "I already
did this." Fully offline, no model call needed to demonstrate this.
"""


class PaymentProcessor:
    """A deliberately naive, non-idempotent version first, to make the
    failure concrete before fixing it."""

    def __init__(self):
        self.charges = []

    def charge(self, customer_id: str, amount: float) -> dict:
        # No check for whether this exact charge already happened.
        # Every call is treated as a brand new charge.
        self.charges.append({"customer_id": customer_id, "amount": amount})
        return {"status": "charged", "amount": amount, "total_charges": len(self.charges)}


class IdempotentPaymentProcessor:
    """The fix: an idempotency key ties separate attempts back to the
    same logical action. A retry carrying the same key becomes a no-op."""

    def __init__(self):
        self.processed_keys = {}

    def charge(self, customer_id: str, amount: float, idempotency_key: str) -> dict:
        if idempotency_key in self.processed_keys:
            # Already handled. Return the original result, do nothing new.
            original = self.processed_keys[idempotency_key]
            return {**original, "note": "duplicate request, no new charge made"}

        result = {"status": "charged", "amount": amount, "customer_id": customer_id}
        self.processed_keys[idempotency_key] = result
        return result


def simulate_agent_retry_on_timeout(charge_fn, attempts: int = 3):
    """
    Simulates exactly what happens in a real agent: a network timeout
    triggers an automatic retry, and the agent has no way of knowing
    whether the first attempt actually succeeded before timing out.
    """
    results = []
    for attempt in range(1, attempts + 1):
        results.append(charge_fn())
    return results


def main() -> None:
    print("=== Naive processor: no idempotency, retried 3 times after a simulated timeout ===\n")
    naive = PaymentProcessor()
    naive_results = simulate_agent_retry_on_timeout(
        lambda: naive.charge("cust_4471", 49.99)
    )
    for i, r in enumerate(naive_results, 1):
        print(f"  Attempt {i}: {r}")
    print(f"\n  Total actual charges recorded: {len(naive.charges)}")
    print(f"  Customer billed: ${sum(c['amount'] for c in naive.charges):.2f} for one $49.99 purchase")

    print("\n=== Idempotent processor: same retry pattern, same idempotency key each time ===\n")
    idempotent = IdempotentPaymentProcessor()
    idempotent_results = simulate_agent_retry_on_timeout(
        lambda: idempotent.charge("cust_4471", 49.99, idempotency_key="order_8821_charge")
    )
    for i, r in enumerate(idempotent_results, 1):
        print(f"  Attempt {i}: {r}")
    print(f"\n  Total unique charges actually processed: {len(idempotent.processed_keys)}")

    print(
        "\nBoth processors received the exact same three calls, simulating "
        "an agent retrying after a timeout with no way of knowing whether "
        "the first attempt had actually gone through. The naive version "
        "charged the customer three times. The idempotent version "
        "recognized the second and third attempts as the same logical "
        "action and did nothing new."
    )
    print(
        "\nThe key insight: the retry itself was not the bug in either "
        "version. Retrying after a timeout is normal, correct behavior. "
        "The bug is a tool with no way to recognize 'I have already done "
        "this exact thing.'"
    )


if __name__ == "__main__":
    main()
