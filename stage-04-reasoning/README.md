# Stage 4 — Reasoning models, named properly

Four things to run. This stage names the actual mechanisms this project's main roadmap only listed by name until now: reasoning effort, self-consistency, best-of-N, and the process-reward-model versus outcome-reward-model distinction.

## What's actually in here

**topic_1_reasoning_effort** — the real `reasoning_effort` parameter (low, medium, high), confirmed via Groq's own current documentation to be supported specifically on `openai/gpt-oss-20b` and `openai/gpt-oss-120b`, this project's default model.

**topic_2_self_consistency** — the same word problem sampled 7 times, majority vote across the answers. No verifier needed, just counting.

**topic_3_best_of_n** — 5 candidate Python expressions, each actually evaluated by a real verifier function against a known correct answer. The verifier itself runs fully offline and has its own test coverage, since two real bugs showed up while building it.

**topic_4_prm_vs_orm** — fully offline. Two reasoning chains, one correct, one wrong-but-lucky, scored two different ways. Shows exactly where an outcome reward model's blind spot is.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key. Topics 1, 2, and 3 need it. Topic 4 needs nothing at all.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq key to `.env`. `LLM_MODEL` is already set to the project default, which this stage specifically depends on for `reasoning_effort` support.

## Running each topic

```bash
python src/topic_1_reasoning_effort/main.py
python src/topic_2_self_consistency/main.py
python src/topic_3_best_of_n/main.py
python src/topic_4_prm_vs_orm/main.py
```

Topic 4 works immediately with no key. The other three need a valid key.

## Tests

```bash
pytest tests/
```

9 tests, covering topic 3's verifier and topic 4's scoring logic, both fully offline. Topics 1 and 2 call a live model and are meant to be run and read, not asserted on.

## A note on how this was built

`reasoning_chat`'s request format was confirmed against Groq's current documentation and smoke-tested against a fake local server to verify the `reasoning_effort` field actually reaches the request body. It has not been run against the real, live Groq API, since this was built with no internet access. Topic 3's verifier, by contrast, was caught making two real mistakes (blocking `sum`/`range` entirely, and accepting a bare number as if it were a computed expression) during offline testing, both fixed before this reached you.

## What you should be able to explain once you're done

- What `reasoning_effort` actually controls, and why spending it on every request is wasteful
- Why self-consistency's majority vote works, and what kind of task it doesn't apply to
- The difference between counting votes (self-consistency) and scoring with a verifier (best-of-N)
- A concrete example of a reasoning chain an outcome reward model would score wrong, that a process reward model catches

## Next

Stage 5 moves into context engineering: what belongs in a model's context window, what doesn't, and why "context rot" means a bigger window doesn't automatically fix a reliability problem.
