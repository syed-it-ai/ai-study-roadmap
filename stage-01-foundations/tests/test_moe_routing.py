"""
Offline test for the mixture-of-experts router in topic 4.

The router's whole job is: score every expert against the token, pick
the top_k highest. This test checks that contract directly — the chosen
experts are exactly the top_k scorers, and everything else is idle.
"""

import numpy as np

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_4_mixture_of_experts.main import route


def test_route_picks_top_k_scorers():
    rng = np.random.RandomState(0)
    n_experts, dim, top_k = 8, 4, 2
    router_weights = rng.randn(n_experts, dim)
    token = rng.randn(dim)

    chosen, scores = route(token, router_weights, top_k)

    assert len(chosen) == top_k
    assert len(set(chosen.tolist())) == top_k  # no duplicates
    # chosen are the top_k by score, in descending order
    expected = np.argsort(scores)[::-1][:top_k]
    assert (chosen == expected).all()


def test_route_active_plus_idle_covers_all_experts():
    rng = np.random.RandomState(1)
    n_experts, dim, top_k = 8, 4, 2
    router_weights = rng.randn(n_experts, dim)
    token = rng.randn(dim)

    chosen, _ = route(token, router_weights, top_k)
    idle = [i for i in range(n_experts) if i not in chosen]

    assert len(idle) == n_experts - top_k
    assert sorted(chosen.tolist() + idle) == list(range(n_experts))
