"""
Two genuinely different architectures exist for voice AI, confirmed as
the current 2026 landscape: speech-to-speech models (OpenAI Realtime,
Gemini Live, AWS Nova Sonic, xAI Realtime) handle audio in and audio
out with one model and one connection. Cascaded pipelines (separate
speech-to-text, LLM, and text-to-speech stages) are slower, confirmed
directly in this stage's latency topic, but each stage is independently
inspectable, swappable, and debuggable.
"""


def recommend_architecture(latency_is_critical: bool, needs_per_stage_debugging: bool,
                            needs_to_swap_providers_per_stage: bool, needs_custom_voice_cloning: bool) -> str:
    """
    The decision logic made explicit. Order matters: debugging and
    provider flexibility are checked before raw latency, because a
    team that genuinely needs mid-pipeline visibility will regret a
    speech-to-speech choice regardless of how much faster it is.
    """
    if needs_per_stage_debugging or needs_to_swap_providers_per_stage:
        return "Cascaded (STT -> LLM -> TTS): independent stages, each inspectable and swappable on its own."
    if needs_custom_voice_cloning:
        return "Cascaded, with a dedicated TTS provider: speech-to-speech models offer fixed voice options, not custom cloning."
    if latency_is_critical:
        return "Speech-to-speech (OpenAI Realtime, Gemini Live, Nova Sonic): fewer stages, lower latency, confirmed by this stage's own measurement."
    return "Either works. Default to cascaded for now, it's easier to debug, and revisit if latency becomes the actual bottleneck."


def main() -> None:
    scenarios = [
        {
            "name": "A phone support agent where every 100ms of delay measurably hurts satisfaction",
            "latency_is_critical": True, "needs_per_stage_debugging": False,
            "needs_to_swap_providers_per_stage": False, "needs_custom_voice_cloning": False,
        },
        {
            "name": "A voice agent a team needs to debug stage by stage during early development",
            "latency_is_critical": True, "needs_per_stage_debugging": True,
            "needs_to_swap_providers_per_stage": False, "needs_custom_voice_cloning": False,
        },
        {
            "name": "A branded assistant that must speak in a specific cloned voice",
            "latency_is_critical": True, "needs_per_stage_debugging": False,
            "needs_to_swap_providers_per_stage": False, "needs_custom_voice_cloning": True,
        },
        {
            "name": "An early internal prototype, nothing latency-sensitive yet",
            "latency_is_critical": False, "needs_per_stage_debugging": False,
            "needs_to_swap_providers_per_stage": False, "needs_custom_voice_cloning": False,
        },
    ]

    for s in scenarios:
        recommendation = recommend_architecture(
            s["latency_is_critical"], s["needs_per_stage_debugging"],
            s["needs_to_swap_providers_per_stage"], s["needs_custom_voice_cloning"],
        )
        print(f"Scenario: {s['name']}")
        print(f"  -> {recommendation}\n")

    print(
        "Debugging and provider flexibility are checked before raw latency "
        "in this decision function, deliberately. A team that needs to see "
        "exactly what the transcription produced, or swap in a different "
        "LLM mid-project without touching the voice layer, will regret "
        "choosing speech-to-speech for the latency win alone, since a "
        "single model handling everything removes exactly that visibility."
    )
    print(
        "\nThis stage's own latency topic measured the actual tradeoff: "
        "830ms for a cascaded pipeline against 380ms for speech-to-speech "
        "on the same realistic stage timings, a 54% reduction. That number "
        "is real and worth taking seriously. It's also not the only thing "
        "that matters when choosing an architecture."
    )


if __name__ == "__main__":
    main()
