"""
Only Topic 3 gets an automated test here. Topics 1 and 2 call a real
API and need a live key, which isn't something a test suite should
depend on. Run those two by hand and read the output yourself.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.topic_3_attention_rough_shape.main import attention_scores


def test_weights_sum_to_one():
    query = np.array([1.0, 0.0, 0.0])
    keys = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    weights = attention_scores(query, keys)
    assert abs(weights.sum() - 1.0) < 1e-9


def test_closer_vector_gets_more_weight():
    query = np.array([0.9, 0.8, 0.1])
    close_key = np.array([0.85, 0.75, 0.15])
    far_key = np.array([0.1, 0.2, 0.9])
    keys = np.array([close_key, far_key])
    weights = attention_scores(query, keys)
    assert weights[0] > weights[1]


def test_identical_query_and_key_gets_highest_possible_share():
    query = np.array([1.0, 2.0, 3.0])
    keys = np.array([query, np.array([-1.0, -2.0, -3.0])])
    weights = attention_scores(query, keys)
    assert weights[0] > 0.99
