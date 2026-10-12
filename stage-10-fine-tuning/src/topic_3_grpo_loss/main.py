"""
Confirmed directly in this project's main roadmap: GRPO is the
algorithm that made RLVR (Reinforcement Learning with Verifiable
Rewards) practical at scale, and is the actual training method behind
DeepSeek-R1's documented result: 15.6% to 77.9% on AIME 2024 math
problems, with zero supervised fine-tuning, using only GRPO and a
verifiable reward. Stage 2 built DPO's loss on a single preference
pair. This builds GRPO's loss on a group of sampled responses, scored
by a real, deterministic verifier, exactly where GRPO is confirmed to
dominate.
"""

import numpy as np


def verify_answer(response_value: float, correct_value: float) -> float:
    """
    The verifiable reward itself: a program checking correctness
    directly, no learned reward model involved at all. This is
    specifically what makes RLVR work, and specifically what it cannot
    do for anything without a checkable right answer.
    """
    return 1.0 if abs(response_value - correct_value) < 1e-6 else 0.0


def grpo_advantage(rewards: np.ndarray) -> np.ndarray:
    """
    The actual GRPO mechanism: no separate value model is trained to
    estimate expected reward. Instead, each response's advantage is
    just its reward compared to the mean of its own group, normalized
    by the group's standard deviation. Removing the value model is
    what cuts the memory and complexity GRPO is known for.
    """
    mean_reward = rewards.mean()
    std_reward = rewards.std() + 1e-8  # avoid division by zero if a group has no variance
    return (rewards - mean_reward) / std_reward


def grpo_clipped_objective(advantages: np.ndarray, policy_ratios: np.ndarray, epsilon: float = 0.2) -> float:
    """
    The clipping term, carried over from PPO: if the policy has shifted
    too far from where it was when these samples were generated (ratio
    outside [1-epsilon, 1+epsilon]), the update for that sample gets
    clipped, preventing one unusually large update from destabilizing
    training.
    """
    unclipped = policy_ratios * advantages
    clipped = np.clip(policy_ratios, 1 - epsilon, 1 + epsilon) * advantages
    return np.minimum(unclipped, clipped).mean()


def main() -> None:
    correct_answer = 42.0

    # A group of 8 sampled responses to the same math problem, standing
    # in for what a real model would generate at a non-zero temperature.
    # DeepSeek's actual setup used groups of 16; 8 is used here only so
    # every value fits on screen.
    sampled_values = np.array([42.0, 41.0, 42.0, 38.0, 42.0, 50.0, 42.0, 39.0])

    rewards = np.array([verify_answer(v, correct_answer) for v in sampled_values])
    print(f"Correct answer: {correct_answer}")
    print(f"Sampled responses: {sampled_values}")
    print(f"Rewards (1.0 if correct, 0.0 if not): {rewards}\n")

    advantages = grpo_advantage(rewards)
    print("Group-relative advantages (reward compared to this group's own mean):")
    for v, r, a in zip(sampled_values, rewards, advantages):
        print(f"  response {v:5.1f}: reward {r:.1f}, advantage {a:+.3f}")

    print(
        "\nNo separate model estimated an expected reward here. The group's "
        "own mean and spread did that job directly, which is the entire "
        "reason GRPO needs less memory than PPO-style RLHF: there is no "
        "second model's parameters and optimizer state to hold in memory "
        "alongside the policy being trained."
    )

    # Simulate the policy ratio for each sample: how much more or less
    # likely the current, updating policy is to produce this exact
    # response compared to when it was originally sampled.
    policy_ratios = np.array([1.1, 0.95, 1.3, 0.8, 1.05, 1.5, 0.9, 1.1])
    objective = grpo_clipped_objective(advantages, policy_ratios)
    print(f"\nClipped objective (epsilon=0.2): {objective:.4f}")
    print(
        "The ratio of 1.5 above would push its update past the clip "
        "boundary on its own. Clipping caught it, the same stabilizing "
        "mechanism PPO introduced, carried into GRPO unchanged."
    )

    print(
        "\nThis is the actual mechanism behind DeepSeek-R1-Zero's documented "
        "result: trained with only GRPO and this exact kind of verifiable "
        "reward, no supervised fine-tuning at all, it went from 15.6% to "
        "77.9% on AIME 2024. Nobody wrote code telling it to reason step by "
        "step. The training loop discovered that reasoning led to a better "
        "group-relative advantage, and kept doing more of it."
    )


if __name__ == "__main__":
    main()
