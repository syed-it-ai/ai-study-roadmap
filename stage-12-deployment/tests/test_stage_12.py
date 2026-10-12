"""
Every topic in Stage 12 is pure logic with no API call, the same
property as Stages 2, 10, and 11, since this stage's content (batching
simulation, gateway routing, quantization math, cost calculation) is
all arithmetic and control flow, not something that needs a live model
to demonstrate.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.topic_1_continuous_batching.main import simulate_static_batching, simulate_continuous_batching
from src.topic_2_llm_gateway_fallback.main import (
    LLMGateway, ProviderError, make_always_fails_provider, make_working_provider,
)
from src.topic_3_quantization_math.main import quantize_to_int8
from src.topic_4_self_host_vs_api.main import (
    naive_cost_per_million_tokens, real_cost_per_million_tokens, find_break_even_tokens_per_day,
)


# --- topic 1: continuous batching ---

def test_continuous_batching_is_never_slower_than_static():
    requests = [2, 3, 2, 15, 2, 3, 2, 2, 14, 3, 2, 2, 3, 13, 2, 2]
    static = simulate_static_batching(requests, batch_size=4)
    continuous = simulate_continuous_batching(requests, batch_size=4)
    assert continuous["total_time"] <= static["total_time"]


def test_continuous_batching_has_higher_utilization_with_mixed_durations():
    requests = [2, 3, 2, 15, 2, 3, 2, 2, 14, 3, 2, 2, 3, 13, 2, 2]
    static = simulate_static_batching(requests, batch_size=4)
    continuous = simulate_continuous_batching(requests, batch_size=4)
    assert continuous["utilization"] > static["utilization"]


def test_uniform_durations_make_batching_strategy_irrelevant():
    # if every request takes the same time, static and continuous
    # batching should produce the same wall-clock time
    requests = [5] * 8
    static = simulate_static_batching(requests, batch_size=4)
    continuous = simulate_continuous_batching(requests, batch_size=4)
    assert abs(static["total_time"] - continuous["total_time"]) < 1e-6


# --- topic 2: gateway fallback ---

def test_gateway_uses_first_working_provider():
    gateway = LLMGateway([("a", make_working_provider("a", "A"))])
    result = gateway.chat("test")
    assert result["served_by"] == "a"


def test_gateway_falls_back_when_primary_fails():
    gateway = LLMGateway([
        ("primary", make_always_fails_provider("primary")),
        ("backup", make_working_provider("backup", "B")),
    ])
    result = gateway.chat("test")
    assert result["served_by"] == "backup"


def test_gateway_raises_when_all_providers_fail():
    gateway = LLMGateway([
        ("a", make_always_fails_provider("a")),
        ("b", make_always_fails_provider("b")),
    ])
    try:
        gateway.chat("test")
        assert False, "should have raised ProviderError"
    except ProviderError:
        pass


def test_gateway_logs_every_attempt_including_failures():
    gateway = LLMGateway([
        ("primary", make_always_fails_provider("primary")),
        ("backup", make_working_provider("backup", "B")),
    ])
    gateway.chat("test")
    assert len(gateway.call_log) == 2
    assert "failed" in gateway.call_log[0]["status"]
    assert gateway.call_log[1]["status"] == "success"


# --- topic 3: quantization ---

def test_dequantized_values_are_close_to_original():
    weights = np.array([-0.342, 0.128, 0.891, -0.675, 0.045, 0.332])
    result = quantize_to_int8(weights)
    error = np.abs(weights - result["dequantized"])
    assert error.max() < 0.01  # int8 quantization should be reasonably precise on this range


def test_quantized_values_stay_within_int8_range():
    weights = np.array([-0.342, 0.128, 0.891, -0.675, 0.045, 0.332])
    result = quantize_to_int8(weights)
    assert result["quantized"].min() >= 0
    assert result["quantized"].max() <= 255


# --- topic 4: self-host vs API ---

def test_real_cost_exceeds_naive_cost():
    naive = naive_cost_per_million_tokens(2.0, 500_000)
    real = real_cost_per_million_tokens(2.0, 500_000, utilization=0.5, staffing_overhead_multiplier=2.0)
    assert real > naive


def test_real_multiplier_lands_in_confirmed_range():
    naive = naive_cost_per_million_tokens(2.0, 500_000)
    real = real_cost_per_million_tokens(2.0, 500_000, utilization=0.5, staffing_overhead_multiplier=2.0)
    multiplier = real / naive
    assert 3.0 <= multiplier <= 5.0  # the confirmed real-world range


def test_break_even_scales_correctly_with_price():
    # a cheaper API should require far more daily tokens to break even
    break_even_expensive = find_break_even_tokens_per_day(100.0, api_price_per_million_tokens=15.0)
    break_even_cheap = find_break_even_tokens_per_day(100.0, api_price_per_million_tokens=0.2)
    assert break_even_cheap > break_even_expensive
