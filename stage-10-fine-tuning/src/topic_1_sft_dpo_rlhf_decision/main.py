"""
Four different post-training approaches exist because they solve four
different shaped problems, not because one superseded the others. This
builds a real decision function from the clean mental model this
project's own roadmap establishes, run against five realistic
scenarios, so the decision is demonstrated, not just described in
prose.
"""


def recommend_approach(has_labeled_examples: bool, has_preference_pairs: bool,
                        has_verifiable_reward: bool, problem_is_subjective: bool) -> str:
    """
    The decision logic, made explicit instead of left as a vague
    feeling. Order matters: a verifiable reward is checked first,
    because when one genuinely exists, it is almost always the
    strongest signal available.
    """
    if has_verifiable_reward and not problem_is_subjective:
        return "GRPO (RLVR): a program can check correctness directly. This is what math and code training use."
    if has_preference_pairs and problem_is_subjective:
        return "DPO: two candidate responses, one marked better, no verifiable right answer, just a comparison."
    if has_labeled_examples and not has_preference_pairs:
        return "SFT: you have correct examples to copy. Teaches tone and format, not judgment between options."
    if problem_is_subjective and not has_verifiable_reward and not has_preference_pairs:
        return "RLHF: the problem runs deeper than any single comparison, needs a learned reward model over many examples."
    return "Insufficient signal for any of these. Start by collecting labeled examples or preference pairs."


def main() -> None:
    scenarios = [
        {
            "name": "Teaching a support bot your company's tone and formatting",
            "has_labeled_examples": True, "has_preference_pairs": False,
            "has_verifiable_reward": False, "problem_is_subjective": False,
        },
        {
            "name": "Training a model to prefer concise answers over verbose ones",
            "has_labeled_examples": False, "has_preference_pairs": True,
            "has_verifiable_reward": False, "problem_is_subjective": True,
        },
        {
            "name": "Training a model to solve math problems correctly",
            "has_labeled_examples": False, "has_preference_pairs": False,
            "has_verifiable_reward": True, "problem_is_subjective": False,
        },
        {
            "name": "Aligning a model's overall helpfulness and harmlessness broadly",
            "has_labeled_examples": False, "has_preference_pairs": False,
            "has_verifiable_reward": False, "problem_is_subjective": True,
        },
        {
            "name": "A brand new product with no data of any kind yet",
            "has_labeled_examples": False, "has_preference_pairs": False,
            "has_verifiable_reward": False, "problem_is_subjective": False,
        },
    ]

    for s in scenarios:
        recommendation = recommend_approach(
            s["has_labeled_examples"], s["has_preference_pairs"],
            s["has_verifiable_reward"], s["problem_is_subjective"],
        )
        print(f"Scenario: {s['name']}")
        print(f"  -> {recommendation}\n")

    print(
        "The verifiable-reward check runs first deliberately. When a program "
        "can check correctness directly, that signal is stronger than any "
        "human preference label, which is exactly why GRPO-style training "
        "dominates math and code, and exactly why it cannot help with "
        "anything subjective, there being no program that can check whether "
        "a joke landed."
    )
    print(
        "\nThis project's Stage 2 already built the actual DPO loss, worked "
        "on a real preference pair. This topic is the decision layer above "
        "that: knowing which of these four approaches a given problem "
        "actually calls for, before writing any training code at all."
    )


if __name__ == "__main__":
    main()
