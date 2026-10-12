"""
A realtime voice pipeline has a latency budget the same way a web
request does, except users notice voice latency far more acutely:
anything past roughly 500ms of silence after a person stops talking
starts to feel unnatural. This breaks an actual cascaded pipeline
(speech-to-text, then an LLM, then text-to-speech) into its stages and
computes where the time actually goes, fully offline since this is
arithmetic on realistic stage timings, not a live call.
"""


def compute_pipeline_latency(stt_ms: float, llm_ttft_ms: float, tts_first_byte_ms: float, network_rtt_ms: float) -> dict:
    """
    The actual stages a cascaded (STT -> LLM -> TTS) voice pipeline runs
    through sequentially before the user hears anything back. Each
    stage's time adds directly to what the user experiences as silence.
    """
    total = stt_ms + llm_ttft_ms + tts_first_byte_ms + network_rtt_ms
    stages = {
        "Speech-to-text (transcribing the user)": stt_ms,
        "LLM time-to-first-token": llm_ttft_ms,
        "Text-to-speech, first audio byte": tts_first_byte_ms,
        "Network round trip": network_rtt_ms,
    }
    return {"stages": stages, "total_ms": total}


def identify_bottleneck(stages: dict) -> tuple:
    bottleneck = max(stages, key=stages.get)
    return bottleneck, stages[bottleneck]


def main() -> None:
    # Realistic current figures for a cascaded pipeline: a cloud STT
    # service, a hosted LLM, and a cloud TTS service, each adding its
    # own latency before the user hears a single word back.
    cascaded = compute_pipeline_latency(
        stt_ms=150, llm_ttft_ms=400, tts_first_byte_ms=200, network_rtt_ms=80,
    )

    print("Cascaded pipeline (STT -> LLM -> TTS), by stage:\n")
    for stage, ms in cascaded["stages"].items():
        bar = "#" * int(ms / 10)
        print(f"  {stage:40s} {ms:5.0f}ms  {bar}")
    print(f"\n  Total time to first audio back to the user: {cascaded['total_ms']:.0f}ms")

    bottleneck_name, bottleneck_ms = identify_bottleneck(cascaded["stages"])
    print(f"  Bottleneck: {bottleneck_name} ({bottleneck_ms:.0f}ms, {100*bottleneck_ms/cascaded['total_ms']:.0f}% of total)")

    # A speech-to-speech model (OpenAI Realtime, Gemini Live, AWS Nova
    # Sonic) collapses STT, reasoning, and TTS into one model handling
    # audio in and audio out directly, removing two of the four stages.
    speech_to_speech = compute_pipeline_latency(
        stt_ms=0, llm_ttft_ms=300, tts_first_byte_ms=0, network_rtt_ms=80,
    )
    print(f"\nSpeech-to-speech model (one model, audio in and out directly):")
    print(f"  Total time to first audio back to the user: {speech_to_speech['total_ms']:.0f}ms")

    savings = cascaded["total_ms"] - speech_to_speech["total_ms"]
    print(f"\nLatency saved by collapsing the pipeline: {savings:.0f}ms ({100*savings/cascaded['total_ms']:.0f}% reduction)")

    print(
        "\nThe cascaded pipeline's bottleneck here is the LLM's own "
        "time-to-first-token, not the audio stages, which is the opposite "
        "of what most people assume before actually measuring it. This is "
        "also exactly why prompt caching (this project's Stage 1) matters "
        "even more in a voice context: shaving time off the LLM stage "
        "directly shortens what a caller experiences as awkward silence."
    )
    print(
        "\nThe tradeoff speech-to-speech doesn't remove: a single model "
        "handling transcription, reasoning, and speech generation together "
        "is harder to inspect and debug mid-pipeline than three separate, "
        "individually swappable stages. Lower latency and easier debugging "
        "pull in opposite directions here."
    )


if __name__ == "__main__":
    main()
