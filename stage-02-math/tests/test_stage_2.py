"""
Every topic in Stage 2 is pure math, no API calls, so every one of them
gets a real automated test here. This is different from Stage 1, where
only the attention demo was offline-testable.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.topic_1_attention_formula.main import softmax as attn_softmax
from src.topic_2_rope_positional_encoding.main import rotate
from src.topic_3_gradient_descent_cross_entropy.main import softmax as gd_softmax, cross_entropy
from src.topic_4_dpo_loss.main import dpo_loss


# --- topic 1: attention formula ---

def test_softmax_sums_to_one():
    probs = attn_softmax(np.array([2.0, 1.0, 0.1]))
    assert abs(probs.sum() - 1.0) < 1e-9


def test_attention_favours_the_closer_key():
    q = np.array([1.0, 0.0])
    k_close = np.array([0.9, 0.1])
    k_far = np.array([-0.9, 0.1])
    scores = np.array([k_close @ q, k_far @ q])
    weights = attn_softmax(scores)
    assert weights[0] > weights[1]


# --- topic 2: RoPE ---

def test_rotation_preserves_vector_length():
    v = np.array([1.0, 0.0])
    rotated = rotate(v, angle=1.3)
    assert abs(np.linalg.norm(rotated) - np.linalg.norm(v)) < 1e-9


def test_relative_position_gives_identical_dot_product():
    theta = 0.5
    v = np.array([1.0, 0.0])

    def rotated_dot(query_pos, key_pos):
        q = rotate(v, theta * query_pos)
        k = rotate(v, theta * key_pos)
        return q @ k

    gap_near_start = rotated_dot(2, 5)
    gap_later = rotated_dot(97, 100)
    assert abs(gap_near_start - gap_later) < 1e-9


# --- topic 3: gradient descent and cross-entropy ---

def test_cross_entropy_is_zero_for_a_perfect_prediction():
    probs = np.array([0.0001, 0.0001, 0.9998])
    loss = cross_entropy(probs, true_index=2)
    assert loss < 0.001


def test_cross_entropy_is_large_for_a_confident_wrong_prediction():
    probs = np.array([0.98, 0.01, 0.01])
    loss = cross_entropy(probs, true_index=2)
    assert loss > 4.0


def test_gradient_descent_reduces_loss_each_step():
    weights = np.array([0.1, 0.1, 0.1])
    true_class = 2
    x = 1.0
    losses = []
    for _ in range(5):
        logits = weights * x
        probs = gd_softmax(logits)
        losses.append(cross_entropy(probs, true_class))
        target = np.zeros(3)
        target[true_class] = 1.0
        gradient = (probs - target) * x
        weights = weights - 0.5 * gradient
    assert all(losses[i] > losses[i + 1] for i in range(len(losses) - 1))


# --- topic 4: DPO loss ---

def test_dpo_loss_drops_as_preference_gap_grows():
    ref_chosen, ref_rejected = -4.0, -4.2
    loss_small_gap, _ = dpo_loss(-4.0, -4.2, ref_chosen, ref_rejected)
    loss_large_gap, _ = dpo_loss(-2.5, -5.8, ref_chosen, ref_rejected)
    assert loss_large_gap < loss_small_gap


def test_dpo_loss_is_positive():
    loss, _ = dpo_loss(-3.0, -5.0, -4.0, -4.2)
    assert loss > 0
