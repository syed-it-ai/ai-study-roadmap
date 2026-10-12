"""
What this shows you: why a 120B parameter model can run about as fast as
a much smaller one. The model you've been calling all through this stage,
openai/gpt-oss-120b, uses exactly this architecture.

No API call needed. This is a toy router, small enough to read end to end,
showing the actual mechanism: most of the model's parameters sit idle on
any single token, and only a handful of "experts" actually do work.
"""

import numpy as np

np.random.seed(7)


def make_toy_experts(n_experts: int, dim: int):
    """
    Each "expert" here is just a small random matrix standing in for a
    real feed-forward network. In an actual model these are trained;
    here they're just different enough from each other to make the
    routing decision visible.
    """
    return [np.random.randn(dim, dim) * 0.5 for _ in range(n_experts)]


def route(token_vector: np.ndarray, router_weights: np.ndarray, top_k: int):
    """
    The router's entire job: score every expert against this token,
    and pick the top_k highest scores. Nothing more complicated than
    a dot product and an argsort.
    """
    scores = router_weights @ token_vector
    chosen = np.argsort(scores)[::-1][:top_k]
    return chosen, scores


def main() -> None:
    n_experts = 8
    top_k = 2
    dim = 4

    experts = make_toy_experts(n_experts, dim)
    router_weights = np.random.randn(n_experts, dim) * 0.5

    tokens = {
        "the":     np.array([0.9, 0.1, 0.2, 0.0]),
        "router":  np.array([0.1, 0.8, 0.3, 0.4]),
        "decides": np.array([0.2, 0.3, 0.9, 0.1]),
    }

    total_params = n_experts * dim * dim
    active_params_per_token = top_k * dim * dim

    print(f"Total experts: {n_experts}, each a {dim}x{dim} matrix")
    print(f"Total parameters across all experts: {total_params}")
    print(f"Parameters actually used per token (top_k={top_k}): {active_params_per_token}")
    print(f"Fraction of the model actually active on any single token: {active_params_per_token/total_params:.0%}\n")

    for word, vec in tokens.items():
        chosen, scores = route(vec, router_weights, top_k)
        idle = [i for i in range(n_experts) if i not in chosen]
        print(f'Token "{word}":')
        print(f"  experts activated: {sorted(chosen.tolist())}")
        print(f"  experts left idle: {idle}")
        print()

    print(
        "Every token in this run activated only 2 of the 8 experts available. "
        "The other 6, and every parameter inside them, did zero work for that "
        "token. That is the entire mechanism. A model with far more total "
        "parameters can still run fast, because most of it is idle at any "
        "given moment, and which part is idle changes token by token."
    )


if __name__ == "__main__":
    main()
