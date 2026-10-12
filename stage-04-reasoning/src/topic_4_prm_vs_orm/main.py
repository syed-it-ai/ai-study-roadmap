"""
An outcome reward model (ORM) only checks whether the final answer was
right. A process reward model (PRM) checks every step along the way.
This matters because a reasoning chain can land on the correct final
answer by accident, through a wrong step that happens to cancel out,
and an ORM has no way to tell the difference. This runs fully offline:
both "models" here are simple rule-based scorers, standing in for
what a trained PRM or ORM would do.
"""

# Two reasoning chains for the same problem: "A shirt costs $40. It is
# on sale for 25% off, then an extra $5 off at checkout. What is the
# final price?" Correct answer: 40 - 10 = 30, then 30 - 5 = 25.

CHAIN_CORRECT_REASONING = [
    ("Calculate 25% of $40", "25% of 40 = 10", 10),
    ("Subtract the discount from the price", "40 - 10 = 30", 30),
    ("Subtract the extra $5 off", "30 - 5 = 25", 25),
]

# This chain reaches the SAME final answer, 25, but through a wrong
# step: it mistakenly computes 25% off as subtracting 15 instead of 10,
# then makes a second, unrelated error that happens to cancel the first.
CHAIN_WRONG_BUT_LUCKY = [
    ("Calculate 25% of $40", "25% of 40 = 15", 15),           # wrong, should be 10
    ("Subtract the discount from the price", "40 - 15 = 25", 25),  # consistent with its own wrong number
    ("Subtract the extra $5 off", "25 - 5 = 25", 25),           # arithmetic error, should be 20, lands back on 25 anyway
]


def outcome_reward_score(chain: list, correct_final_answer: int) -> dict:
    """ORM: only ever looks at the last number produced."""
    final_answer = chain[-1][2]
    correct = final_answer == correct_final_answer
    return {"method": "ORM", "final_answer": final_answer, "scored_correct": correct}


def process_reward_score(chain: list, verify_step) -> dict:
    """PRM: checks every intermediate step against its own expected
    calculation, not just the final number."""
    results = []
    for description, work_shown, value in chain:
        step_ok = verify_step(description, value)
        results.append((description, value, step_ok))
    all_steps_correct = all(r[2] for r in results)
    return {"method": "PRM", "steps": results, "all_steps_correct": all_steps_correct}


def verify_step(description: str, value: int) -> bool:
    """A tiny rule-based verifier standing in for a trained PRM. Knows
    the correct intermediate value for each named step in this problem."""
    expected = {
        "Calculate 25% of $40": 10,
        "Subtract the discount from the price": 30,
        "Subtract the extra $5 off": 25,
    }
    return value == expected.get(description)


def main() -> None:
    correct_final_answer = 25

    print("Chain A: every step correct")
    for desc, work, val in CHAIN_CORRECT_REASONING:
        print(f"  {desc}: {work}")
    orm_a = outcome_reward_score(CHAIN_CORRECT_REASONING, correct_final_answer)
    prm_a = process_reward_score(CHAIN_CORRECT_REASONING, verify_step)
    print(f"  ORM result: final answer {orm_a['final_answer']}, scored correct: {orm_a['scored_correct']}")
    print(f"  PRM result: all steps correct: {prm_a['all_steps_correct']}")

    print("\nChain B: wrong steps that happen to cancel out, same final answer")
    for desc, work, val in CHAIN_WRONG_BUT_LUCKY:
        print(f"  {desc}: {work}")
    orm_b = outcome_reward_score(CHAIN_WRONG_BUT_LUCKY, correct_final_answer)
    prm_b = process_reward_score(CHAIN_WRONG_BUT_LUCKY, verify_step)
    print(f"  ORM result: final answer {orm_b['final_answer']}, scored correct: {orm_b['scored_correct']}")
    print(f"  PRM result: all steps correct: {prm_b['all_steps_correct']}")
    for desc, val, ok in prm_b['steps']:
        if not ok:
            print(f"    PRM flags: '{desc}' produced {val}, which is wrong, even though the chain still lands correctly")

    print(
        "\nBoth chains get the exact same ORM score: correct. Only the PRM "
        "can tell them apart, because it checks the reasoning itself, not "
        "just where it ends up. A chain that is right for the wrong reasons "
        "is exactly the failure mode an ORM cannot see, and the reason PRMs "
        "are what make tree search over reasoning paths possible: without "
        "step-level scores, there is nothing to prune a bad branch on until "
        "it is already too late."
    )


if __name__ == "__main__":
    main()
