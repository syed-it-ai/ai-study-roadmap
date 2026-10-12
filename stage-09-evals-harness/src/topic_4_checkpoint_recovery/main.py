"""
Confirmed as a real, current research area for this build: long-horizon
agent execution needs a way to recover from a crash partway through,
rather than restarting from scratch or, worse, continuing to run
unsupervised the way the documented 11-day, $47,000 runaway-agent
incident did. This extends Stage 8's ReAct loop with checkpointing:
the agent's state gets saved after every step, so a crash can resume
from the last good step instead of starting over or looping forever.
Fully offline, a simulated crash included directly in the demo.
"""

import json
import os

CHECKPOINT_FILE = "/tmp/agent_checkpoint.json"
CRASH_FLAG_FILE = "/tmp/agent_crash_already_happened.flag"


def save_checkpoint(step: int, history: list) -> None:
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"step": step, "history": history}, f)


def load_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"step": 0, "history": []}


def clear_checkpoint() -> None:
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
    if os.path.exists(CRASH_FLAG_FILE):
        os.remove(CRASH_FLAG_FILE)


def crash_already_happened() -> bool:
    """A real crash, like a timeout or an out-of-memory kill, happens
    once per attempt. This models that: the first time this step runs,
    it crashes. On retry, exactly like a real transient failure, it
    succeeds, because whatever caused it (a dropped connection, a
    momentary resource spike) is not guaranteed to recur."""
    if os.path.exists(CRASH_FLAG_FILE):
        return True
    open(CRASH_FLAG_FILE, "w").close()
    return False


# A scripted sequence of steps standing in for real model calls, with a
# crash injected at step 3 that happens exactly once, so the recovery
# path actually makes progress on retry instead of looping on the same
# failure forever.
SCRIPTED_STEPS = [
    "Checked inventory for gadget: 0 in stock",
    "Checked inventory for widget: 42 in stock",
    "__SIMULATED_CRASH_ONCE__",
    "Checked price for widget: $9.99",
    "Final answer: Recommend widget, in stock at $9.99",
]


def run_with_recovery(max_steps: int = 10):
    """
    Runs the scripted steps, saving a checkpoint after each one. If a
    crash is hit, the function returns early, simulating a real process
    dying. A second call resumes from the saved checkpoint instead of
    starting over.
    """
    checkpoint = load_checkpoint()
    step = checkpoint["step"]
    history = checkpoint["history"]

    if step > 0:
        print(f"Resuming from checkpoint at step {step}, {len(history)} steps already completed.\n")

    while step < len(SCRIPTED_STEPS) and step < max_steps:
        action = SCRIPTED_STEPS[step]

        if action == "__SIMULATED_CRASH_ONCE__":
            if not crash_already_happened():
                print(f"Step {step + 1}: CRASH. Process dies here, unexpectedly, mid-execution.")
                save_checkpoint(step, history)  # last good state, saved before the crash
                return None  # simulates the process actually dying
            action = "Checked price for gadget: $24.99 (succeeded on retry)"

        print(f"Step {step + 1}: {action}")
        history.append(action)
        step += 1
        save_checkpoint(step, history)

    clear_checkpoint()
    return history


def main() -> None:
    clear_checkpoint()  # start clean for this demo

    print("=== First run: crashes partway through ===\n")
    result = run_with_recovery()
    if result is None:
        print("\nProcess has 'died'. Nothing further runs in this call.")

    print("\n=== Second run: same function call, after the 'crash' ===\n")
    final_result = run_with_recovery()

    print(f"\nFinal history: {final_result}")
    print(
        "\nThe second run did not redo the inventory checks it had already "
        "completed. It resumed from exactly the step the checkpoint saved, "
        "right after the crash, and finished the remaining steps. Without "
        "this, a crash partway through a long agent task means either "
        "restarting the entire task from scratch, repeating every already-"
        "completed action, including any with real side effects, or losing "
        "the task entirely."
    )
    print(
        "\nThis is the structural fix for the failure class behind the "
        "documented 11-day runaway agent incident already referenced in "
        "this project: a process with no checkpoint and no way to verify "
        "its own progress has no way to tell 'still working' apart from "
        "'stuck looping forever.' A checkpoint gives something external "
        "the ability to inspect exactly how far the agent actually got."
    )


if __name__ == "__main__":
    main()
