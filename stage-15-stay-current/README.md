# Stage 15 — Stay current

Four things to run, all pure Python, no external library beyond pytest. This is the final stage, and unlike every stage before it, it isn't about a technical concept, it's about a habit. All four topics here codify the exact discipline this 14-stage project has been running on itself the entire time.

## What's actually in here

**topic_1_source_currency_scoring** — a real decay model scoring how much to trust a source based on its age and its topic's actual volatility. Grounded directly in this project's own build history: Stage 1's retired Groq model (stale within ~2 months) versus Stage 2's gradient descent math (unchanged for decades).

**topic_2_reading_loop_tracker** — a stateful tracker for the article-docs-build-reread loop from this project's main roadmap. Correctly rejects any attempt to skip straight from reading to rereading without building something in between, and surfaces exactly which topics are stuck before that step.

**topic_3_signal_vs_noise_curation** — real scoring for "pick 2, not 10," confirmed against a real 2026 finding: over 3,000 AI newsletters launched on one platform in 2023 alone. The lowest-scoring candidate in this topic's own test case is cut specifically for overlapping with a source already kept, not for being bad in isolation.

**topic_4_claims_vs_verified** — the capstone. A real scanner distinguishing a backed claim (real test, real printed output) from an unbacked one (confident phrasing, nothing behind it), directly modeled on the single most repeated bug pattern across all 14 prior stages.

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
python src/topic_1_source_currency_scoring/main.py
python src/topic_2_reading_loop_tracker/main.py
python src/topic_3_signal_vs_noise_curation/main.py
python src/topic_4_claims_vs_verified/main.py
```

All four work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

13 tests, covering all four topics in full.

## A note on how this was built

Topic 4 is a direct reflection on this entire project's own build, not an abstract exercise. Every example of an "unbacked claim" it references (Stage 1's flat embeddings, Stage 12's 1.4x multiplier bug, Stage 13's accidentally-identical skill priorities) is a real bug this exact project's own `stage-build-patterns.md` recorded, caught by the same discipline this final topic tries to generalize: don't trust a confident sentence, check what's actually behind it.

## What you should be able to explain once you're done

- Why the same source age means very different things depending on what kind of fact it's making a claim about
- Why a reading habit that stops at "article read" produces a feeling of learning without much of the substance, and how to catch it happening
- The actual discipline behind "pick 2, not 10": scoring sources by what they add beyond what's already being read, not by whether they're good in isolation
- Why the word "confirmed" in a sentence is not itself evidence, and how to check what's actually backing a claim before trusting it

## This project

This is Stage 15 of 15, the final stage of a 16-stage roadmap (Stage 0 skipped as pure setup). Each stage was built the same way: real code, real tests where the content allowed it, original diagrams matched to their concept, research checked against current sources rather than assumed, and bugs caught by actually running things rather than trusting that they worked. `stage-build-patterns.md` records the full history of what was learned building it this way, stage by stage.
