"""
Excessive agency is confirmed as LLM03:2026 in OWASP's current Top 10,
and its single biggest promotion in the 2026 rewrite: the 2025 list
treated agency as a downstream concern, the 2026 list treats it as the
control deciding whether a successful prompt injection is a minor
inconvenience or a real incident. The logic: if an injection succeeds
but the agent that got hijacked can only read data, the damage is
limited. If the same injection succeeds against an agent that can send
money or delete records, the damage is not.

This builds the actual scoping check: given an action an agent wants
to take, does its current permission scope actually allow it, checked
independently of whether the instruction to take that action was
legitimate or injected.
"""


class ActionScope:
    """
    Defines the actual ceiling on what an agent can do, regardless of
    what any single instruction, legitimate or injected, asks for.
    This is the control OWASP's 2026 list specifically elevated:
    agency as the thing limiting blast radius when injection defenses
    (this stage's topic 1) are not perfect, because they never are.
    """

    def __init__(self, allowed_actions: set, max_value_per_action: float = None):
        self.allowed_actions = allowed_actions
        self.max_value_per_action = max_value_per_action

    def check(self, action: str, value: float = None) -> dict:
        reasons = []
        if action not in self.allowed_actions:
            reasons.append(f"'{action}' is outside this scope's allowed actions {sorted(self.allowed_actions)}")
        if value is not None and self.max_value_per_action is not None and value > self.max_value_per_action:
            reasons.append(f"value {value} exceeds this scope's per-action limit of {self.max_value_per_action}")
        return {"allowed": len(reasons) == 0, "reasons": reasons}


def main() -> None:
    # Two agents doing the same job, support ticket handling, with
    # genuinely different agency scopes.
    read_only_scope = ActionScope(allowed_actions={"read_ticket", "add_comment"})
    broad_scope = ActionScope(allowed_actions={"read_ticket", "add_comment", "issue_refund", "close_account"}, max_value_per_action=500.0)

    # The same, potentially-injected instruction, attempted against both.
    attempted_action = "issue_refund"
    attempted_value = 9999.00

    print(f"Attempted action: {attempted_action}, value: ${attempted_value}\n")

    result_narrow = read_only_scope.check(attempted_action, attempted_value)
    print(f"Read-only scope: {'ALLOWED' if result_narrow['allowed'] else 'BLOCKED'}")
    for r in result_narrow["reasons"]:
        print(f"  - {r}")

    result_broad = broad_scope.check(attempted_action, attempted_value)
    print(f"\nBroad scope: {'ALLOWED' if result_broad['allowed'] else 'BLOCKED'}")
    for r in result_broad["reasons"]:
        print(f"  - {r}")

    # The same action, a reasonable value, against the broad scope.
    reasonable_attempt = broad_scope.check("issue_refund", 45.00)
    print(f"\nSame broad scope, a reasonable $45 refund instead: {'ALLOWED' if reasonable_attempt['allowed'] else 'BLOCKED'}")

    print(
        "\nIf this attempted $9,999 refund came from a legitimate request, "
        "both scopes handled it defensibly: the narrow one blocked it "
        "outright, the broad one blocked it specifically for exceeding a "
        "sane per-action limit. If it came from an injected instruction "
        "hidden in a ticket's content, exactly the same two outcomes "
        "apply, and that's the actual point. The scope doesn't need to "
        "know whether an instruction was legitimate or injected, because "
        "it's checking what the action would do, not where the "
        "instruction to do it came from."
    )
    print(
        "\nThis is confirmed directly as why OWASP promoted this risk to "
        "third place in 2026: a perfect prompt injection defense is not "
        "achievable, confirmed in this stage's previous topic. Scoping "
        "agency is what keeps a successful injection from becoming "
        "catastrophic even when the injection defense itself fails."
    )


if __name__ == "__main__":
    main()
