"""
Supervised fine-tuning teaches a model to copy good examples. DPO
teaches it something different: given two responses to the same
prompt, one marked better than the other, push the model toward
preferring the better one, without ever training a separate reward
model or running a reinforcement learning loop.

This works through the actual DPO loss on one preference pair.
"""

import numpy as np


def dpo_loss(
    policy_logprob_chosen: float,
    policy_logprob_rejected: float,
    ref_logprob_chosen: float,
    ref_logprob_rejected: float,
    beta: float = 0.1,
) -> float:
    """
    The DPO loss, implemented directly from its definition: how much
    more (in log-probability terms) the current policy favours the
    chosen response over the rejected one, compared to how much the
    original reference model favoured it, scaled by beta.
    """
    policy_logratio = policy_logprob_chosen - policy_logprob_rejected
    ref_logratio = ref_logprob_chosen - ref_logprob_rejected
    logits = beta * (policy_logratio - ref_logratio)
    # -log(sigmoid(x)) is the loss; sigmoid turns the logit into a
    # probability that the policy correctly prefers the chosen response.
    loss = -np.log(1 / (1 + np.exp(-logits)))
    return loss, logits


def main() -> None:
    # A single preference pair: a prompt, a chosen (better) response,
    # a rejected (worse) one. In practice these come from human raters
    # or another model doing the comparing.
    print('Prompt: "How do I reset my password?"')
    print('Chosen:   "Go to Settings, select Security, then Reset Password."')
    print('Rejected: "I am not sure, maybe check the app somewhere."\n')

    # Log-probabilities a model assigns to generating each full response.
    # These are stand-ins for real numbers a model would compute token
    # by token, summed across the response.
    ref_logprob_chosen = -4.0     # the untouched reference model's score
    ref_logprob_rejected = -4.2   # reference model barely prefers chosen already

    print("Before any training (the reference model's own preference):")
    ref_diff = ref_logprob_chosen - ref_logprob_rejected
    print(f"  log-probability gap (chosen - rejected): {ref_diff:.3f}")
    print("  A small positive gap: barely prefers the chosen response.\n")

    print("As DPO training updates the policy across a few steps:")
    # Simulate the policy's preference growing stronger over a few
    # training steps, which is what DPO's gradient actually pushes for.
    policy_logprob_pairs = [
        (-4.0, -4.2),   # step 0: identical to the reference model, no training yet
        (-3.6, -4.5),   # step 1: starting to favour chosen more
        (-3.0, -5.0),   # step 2: favouring chosen much more strongly
        (-2.5, -5.8),   # step 3: strong preference learned
    ]

    for step, (pc, pr) in enumerate(policy_logprob_pairs):
        loss, logits = dpo_loss(pc, pr, ref_logprob_chosen, ref_logprob_rejected)
        print(f"  step {step}: policy gap = {pc - pr:.2f}, DPO loss = {loss:.4f}")

    print(
        "\nThe loss drops as the policy's preference for the chosen response "
        "grows relative to the reference model's own preference. Nothing here "
        "needed a learned reward model or a reinforcement learning loop, only "
        "the preference pair itself and the reference model's original scores."
    )
    print(
        "\nWhere this fits next to GRPO, covered later in this roadmap: DPO "
        "needs a labeled pair, better or worse, decided by a person or another "
        "model. GRPO needs a verifier that can check correctness automatically, "
        "which is why GRPO dominates math and code, where correctness is "
        "checkable, while DPO remains the default for subjective quality, tone, "
        "and style, where there often is no single verifiable right answer."
    )


if __name__ == "__main__":
    main()
