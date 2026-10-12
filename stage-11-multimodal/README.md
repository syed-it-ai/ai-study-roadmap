# Stage 11 — Multimodal, voice, and realtime

Four things to run, all of them pure Python, no external library needed beyond the standard library and pytest for testing.

**An honest note before anything else**: this sandbox has no vision model access, no image or audio files, and no connection to a voice API. Every topic here is built around the real engineering that surrounds a vision or voice call rather than the call itself: state machines, latency math, validation logic, architecture decisions. This is most of the actual engineering effort in a multimodal pipeline anyway, once the call itself has been made.

## What's actually in here

**topic_1_turn_taking_state_machine** — a real state machine for a voice conversation's turns, with barge-in modeled as its own explicit transition, not an afterthought. Confirmed against current provider practice: semantic end-of-turn detection, not a fixed silence timer.

**topic_2_latency_budget** — real arithmetic across a cascaded voice pipeline's stages (speech-to-text, LLM, text-to-speech), identifying the actual bottleneck, then comparing against a speech-to-speech architecture's measured latency.

**topic_3_document_extraction** — schema extraction and semantic validation on invoice fields, using explicitly-labeled simulated OCR text since no vision model is available here. A second example proves the validation actually catches two real, planted problems.

**topic_4_speech_architecture_decision** — a real decision function choosing between speech-to-speech and cascaded architectures across four scenarios, using this stage's own measured latency numbers.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- Nothing else. No API key, no provider account, no internet connection.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running each topic

```bash
python src/topic_1_turn_taking_state_machine/main.py
python src/topic_2_latency_budget/main.py
python src/topic_3_document_extraction/main.py
python src/topic_4_speech_architecture_decision/main.py
```

All four work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

16 tests, covering all four topics in full, since every topic in this stage is pure logic.

## A note on how this was built

Topic 3's first version only demonstrated a clean invoice passing validation, which never actually proved the validation logic catches a real problem, just asserted it would in prose. Fixed by adding a second simulated invoice with two planted issues (a due date before the invoice date, and an unusually large amount), both of which extract with perfectly valid formatting and only get caught by the semantic check. This is the same honesty standard as every other stage: a claim about what code does gets demonstrated, not just described.

## What you should be able to explain once you're done

- Why barge-in needs to be modeled as its own state transition, and what semantic end-of-turn detection fixes about a fixed silence timer
- Where latency actually accumulates in a cascaded voice pipeline, and why the LLM stage, not the audio stages, is often the real bottleneck
- A concrete example of a document field that extracts cleanly but fails semantic validation, and why that distinction matters
- Why the fastest voice architecture isn't automatically the right choice, and what requirements should be checked before latency

## Next

Stage 12 moves into deployment and inference: self-hosting versus API economics done properly, and the LLM gateway layer most tutorials skip entirely.
