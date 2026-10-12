"""
Not every topic goes stale at the same rate. A model's pricing or a
provider's available model list can be wrong within weeks, confirmed
directly by this project's own build: Stage 1 hit a retired Groq model
name live, and Stage 7's MCP research needed re-verifying from scratch
within the same build because an earlier pass had only partially
captured a protocol revision. A mathematical formula or a training
algorithm doesn't carry that same risk. This builds the actual scoring
logic for deciding how much to trust a source's age, rather than
leaving that judgment as an unstated gut feeling.
"""

from datetime import date


# Volatility tiers, grounded directly in this project's own 14-stage
# build experience, not an abstract guess. Each tier names a real
# category of fact this project actually encountered going stale or
# staying stable.
VOLATILITY_HALF_LIFE_DAYS = {
    "model_pricing_and_availability": 60,     # Stage 1's retired Groq model, confirmed live
    "provider_feature_support": 90,            # Stage 3's strict-mode model list, confirmed live
    "protocol_specifications": 120,            # Stage 7's MCP revision, confirmed live
    "framework_best_practices": 180,           # Stage 12's vLLM/SGLang landscape
    "mathematical_formulas": 36500,            # effectively永久, Stage 2 and 10's math never needed re-checking
    "foundational_algorithms": 36500,          # ReAct, attention, gradient descent, unchanged since publication
}


def currency_score(category: str, source_date: date, today: date) -> dict:
    """
    A simple decay model: a source's trustworthiness halves every
    half_life_days for its category. A pricing claim from 90 days ago
    in a 60-day half-life category has decayed meaningfully. The
    identical age for a mathematical formula has decayed essentially
    not at all.
    """
    half_life = VOLATILITY_HALF_LIFE_DAYS.get(category, 90)
    age_days = (today - source_date).days
    # Standard exponential decay: 0.5 ** (age / half_life)
    confidence = 0.5 ** (age_days / half_life)

    if confidence > 0.75:
        verdict = "trust directly"
    elif confidence > 0.35:
        verdict = "spot-check before relying on it"
    else:
        verdict = "re-verify from scratch"

    return {"category": category, "age_days": age_days, "confidence": round(confidence, 3), "verdict": verdict}


def main() -> None:
    today = date(2026, 10, 12)  # matching this project's own build date

    test_cases = [
        ("model_pricing_and_availability", date(2026, 8, 1)),   # ~72 days old
        ("model_pricing_and_availability", date(2026, 10, 1)),  # ~11 days old
        ("protocol_specifications", date(2026, 7, 1)),           # ~103 days old
        ("mathematical_formulas", date(2023, 1, 1)),             # ~3 years old
        ("foundational_algorithms", date(2022, 1, 1)),           # ~4 years old
    ]

    for category, source_date in test_cases:
        result = currency_score(category, source_date, today)
        print(f"{category}, dated {source_date}:")
        print(f"  age: {result['age_days']} days, confidence: {result['confidence']}, verdict: {result['verdict']}")
        print()

    print(
        "A model pricing claim 72 days old and a foundational algorithm "
        "description nearly 4 years old get opposite treatment, "
        "correctly, because they decay at genuinely different rates. "
        "Treating every source's age the same way, either trusting "
        "everything regardless of age or re-verifying everything on "
        "principle, wastes effort in one direction and risks being wrong "
        "in the other."
    )
    print(
        "\nThis project's own build hit this exact distinction directly: "
        "Stage 1's Groq model name had gone stale within roughly two "
        "months, while Stage 2's gradient descent math, derived from "
        "calculus unchanged for centuries, needed zero re-verification "
        "regardless of how long ago it was written down."
    )


if __name__ == "__main__":
    main()
