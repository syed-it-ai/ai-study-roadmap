# Stage 3 — Building with LLM APIs for real

Four things to run. This stage moves from understanding the mechanism (Stages 1 and 2) to the actual engineering layer: getting output you can trust enough to act on automatically.

## What's actually in here

**topic_1_structured_output** — a real call using strict-mode structured output, true constrained decoding. The response is guaranteed to match the schema exactly: a category from four fixed values, never anything else.

**topic_2_prompts_as_contracts** — the same extraction task run three times with a vague prompt and three times with an explicit one. Watch the shape of the answers, not just their content.

**topic_3_schema_vs_semantic_validation** — the one topic in this stage that runs fully offline. Five test records showing exactly where a schema check's guarantees end and a semantic check's job begins. A well-formed order ID that simply doesn't exist is the clearest example.

**topic_4_ticket_classifier_project** — the applied project. A real ticket classifier combining all three: a contract prompt, a strict schema, and a semantic sanity check afterward.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key (console.groq.com, no card). This stage specifically depends on Groq's strict-mode structured output, which is currently confirmed to support `openai/gpt-oss-120b`, this project's default model. If you ever switch models, check console.groq.com/docs/structured-outputs first.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and add your Groq key. `LLM_MODEL` is already set to the project default.

## Running each topic

```bash
python src/topic_1_structured_output/main.py
python src/topic_2_prompts_as_contracts/main.py
python src/topic_3_schema_vs_semantic_validation/main.py
python src/topic_4_ticket_classifier_project/main.py
```

Topic 3 works immediately with no key needed. The other three need your Groq key to be valid, since they make real calls.

## Tests

```bash
pytest tests/
```

Only topic 3 has automated tests, the same honest limitation as Stage 1: topics 1, 2, and 4 all call a live API and are meant to be run and read, not asserted on in a test suite.

## A note on how this was built

The request format for `structured_chat` (the `response_format` with `json_schema` and `strict: true`) was written against Groq's own current documentation and smoke-tested against a fake local server to confirm the request actually carries the strict flag, not just claims to. It has not been run against the real, live Groq API, since this was built somewhere with no internet access. If something needs a small adjustment once you run it for real, that's an expected first pass, not carelessness.

## What you should be able to explain once you're done

- What constrained decoding actually guarantees, and what it does not
- Why a vague prompt can be correct and still unreliable
- The specific difference between a schema check and a semantic check, with a concrete example of each catching something the other misses
- How to combine a contract prompt, a schema, and a semantic check into one small real pipeline

## Next

Stage 4 moves into reasoning models and test-time compute, when the extra cost and latency of a model that "thinks" before answering actually earns its keep, and the named techniques, self-consistency, best-of-N, process reward models, behind that decision.
