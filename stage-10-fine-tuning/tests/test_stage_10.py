"""
Every topic in Stage 10 is pure math with no API call, the same
property as Stage 2, so every topic gets full automated test coverage.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.topic_1_sft_dpo_rlhf_decision.main import recommend_approach
from src.topic_2_lora_dora_math.main import (
    full_finetuning_parameter_count, lora_parameter_count, lora_update, dora_update,
)
from src.topic_3_grpo_loss.main import verify_answer, grpo_advantage, grpo_clipped_objective
from src.topic_4_knowledge_distillation.main import softmax, hard_label_loss, soft_label_loss


# --- topic 1: decision framework ---

def test_verifiable_reward_routes_to_grpo():
    result = recommend_approach(False, False, True, False)
    assert "GRPO" in result


def test_preference_pairs_on_subjective_problem_routes_to_dpo():
    result = recommend_approach(False, True, False, True)
    assert "DPO" in result


def test_labeled_examples_alone_routes_to_sft():
    result = recommend_approach(True, False, False, False)
    assert "SFT" in result


def test_subjective_with_no_other_signal_routes_to_rlhf():
    result = recommend_approach(False, False, False, True)
    assert "RLHF" in result


def test_no_signal_at_all_recommends_collecting_data():
    result = recommend_approach(False, False, False, False)
    assert "Insufficient" in result


# --- topic 2: LoRA/DoRA math ---

def test_lora_uses_far_fewer_parameters_than_full_finetuning():
    full = full_finetuning_parameter_count(4096, 4096)
    lora = lora_parameter_count(4096, 4096, rank=16)
    assert lora < full * 0.05  # confirmed current finding: well under 5% at this scale


def test_lora_parameter_count_formula_is_correct():
    # rows*rank + rank*cols
    assert lora_parameter_count(100, 100, 10) == (100*10 + 10*100)


def test_lora_and_dora_produce_different_results_from_the_same_inputs():
    np.random.seed(1)
    W0 = np.random.randn(8, 8) * 0.1
    A = np.random.randn(2, 8) * 0.01
    B = np.random.randn(8, 2) * 0.01
    lora_result = lora_update(W0, A, B)
    dora_result = dora_update(W0, A, B)
    assert not np.allclose(lora_result, dora_result)


# --- topic 3: GRPO ---

def test_verify_answer_rewards_exact_match():
    assert verify_answer(42.0, 42.0) == 1.0


def test_verify_answer_penalizes_wrong_answer():
    assert verify_answer(41.0, 42.0) == 0.0


def test_grpo_advantage_is_zero_mean_within_group():
    rewards = np.array([1.0, 0.0, 1.0, 0.0])
    advantages = grpo_advantage(rewards)
    assert abs(advantages.mean()) < 1e-9


def test_correct_responses_get_positive_advantage():
    rewards = np.array([1.0, 0.0, 1.0, 0.0])
    advantages = grpo_advantage(rewards)
    assert advantages[0] > 0
    assert advantages[1] < 0


def test_clipping_actually_bounds_extreme_ratios():
    advantages = np.array([1.0])
    extreme_ratio = np.array([5.0])  # far outside any reasonable clip range
    objective = grpo_clipped_objective(advantages, extreme_ratio, epsilon=0.2)
    assert objective <= 1.2  # clipped to at most (1+epsilon)*advantage


# --- topic 4: distillation ---

def test_softmax_output_sums_to_one():
    probs = softmax(np.array([1.0, 2.0, 3.0]))
    assert abs(probs.sum() - 1.0) < 1e-9


def test_hard_label_loss_is_low_for_confident_correct_prediction():
    probs = np.array([0.95, 0.02, 0.02, 0.01])
    loss = hard_label_loss(probs, true_class=0)
    assert loss < 0.1


def test_soft_label_loss_rewards_matching_the_full_teacher_distribution():
    teacher = np.array([0.7, 0.2, 0.05, 0.05])
    matching_student = np.array([0.7, 0.2, 0.05, 0.05])
    different_student = np.array([0.25, 0.25, 0.25, 0.25])
    matching_loss = soft_label_loss(matching_student, teacher)
    different_loss = soft_label_loss(different_student, teacher)
    assert matching_loss < different_loss
