"""
The specific harness-engineering concern for coding agents: a tool
that can write files is dangerous if it writes them blindly. The real
pattern used across current coding agents is propose, diff, approve,
apply: generate the change, show exactly what would change as a diff,
require explicit approval before touching the real file, and only then
apply it. This builds that actual workflow, including the part most
toy examples skip, what happens when the change gets rejected.
"""

import difflib


class FileEditHarness:
    """
    Separates "the agent decided what to change" from "the change
    actually happened to a real file" with an explicit approval gate
    in between. No write ever reaches the real file without passing
    through propose_change first.
    """

    def __init__(self):
        self.pending_change = None
        self.applied_changes = []

    def propose_change(self, file_path: str, original_content: str, new_content: str) -> str:
        """Generates a real unified diff, the same format a human
        reviewer or a git diff would show, not a vague description of
        what changed."""
        diff_lines = list(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"{file_path} (current)",
            tofile=f"{file_path} (proposed)",
        ))
        self.pending_change = {
            "file_path": file_path,
            "original_content": original_content,
            "new_content": new_content,
            "diff": "".join(diff_lines),
        }
        return self.pending_change["diff"]

    def approve_and_apply(self) -> dict:
        if self.pending_change is None:
            raise ValueError("No pending change to approve. Call propose_change first.")
        applied = self.pending_change
        self.applied_changes.append(applied)
        self.pending_change = None
        return {"status": "applied", "file_path": applied["file_path"]}

    def reject(self) -> dict:
        if self.pending_change is None:
            raise ValueError("No pending change to reject.")
        rejected = self.pending_change
        self.pending_change = None
        return {"status": "rejected", "file_path": rejected["file_path"]}


def main() -> None:
    harness = FileEditHarness()

    original = """def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""

    proposed = """def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total
"""

    print("=== Proposing a change, nothing written yet ===\n")
    diff = harness.propose_change("billing.py", original, proposed)
    print(diff)
    print(f"Pending change exists: {harness.pending_change is not None}")
    print(f"Applied changes so far: {len(harness.applied_changes)}")

    print("\n=== A reviewer rejects this specific change ===\n")
    result = harness.reject()
    print(result)
    print(f"Pending change exists after rejection: {harness.pending_change is not None}")
    print(f"Applied changes after rejection: {len(harness.applied_changes)}")

    print("\n=== The agent proposes a corrected version, this time approved ===\n")
    corrected = """def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return round(total, 2)
"""
    diff2 = harness.propose_change("billing.py", original, corrected)
    print(diff2)
    result2 = harness.approve_and_apply()
    print(result2)
    print(f"Applied changes now: {len(harness.applied_changes)}")

    print(
        "\nThe rejected change never touched applied_changes at all, and "
        "attempting to approve or reject with no pending change raises an "
        "error rather than silently doing nothing. This is the actual "
        "mechanism that makes 'review before apply' a real guarantee "
        "rather than a step an agent could accidentally skip: there is no "
        "code path from propose_change directly to a real file write "
        "without passing through this gate."
    )


if __name__ == "__main__":
    main()
