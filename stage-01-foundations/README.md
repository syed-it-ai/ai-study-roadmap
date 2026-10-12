# Stage 1 — Foundations

Three small, real things to run. Not a theory dump.

Before this stage, "LLM" is mostly a buzzword. After it, you should be able to look at a model's response and have a rough, honest idea of what actually just happened, not the full math behind it (that's Stage 2), just enough to stop being confused by what you see on screen.

## What's actually in here

**topic_1_tokens_and_counting** — sends a few different pieces of text to a free model and looks at the real token counts the API hands back. No separate tokenizer library needed. The number you're actually billed on is already sitting in the response if you look for it.

**topic_2_same_prompt_different_answers** — sends the exact same prompt several times and prints every answer side by side. It opens with a short offline demo showing that the request leaving your machine is byte-identical every call: no weights travel in either direction, so the model on call 2 is bit-for-bit the same model as on call 1. What you're watching in the live part is randomness in how the next word gets picked, not the model knowing something differently each time.

**topic_3_attention_rough_shape** — runs with no internet and no API key at all. A small, deliberately made-up example (hand-written numbers, not real learned embeddings) showing the core shape of attention: compare a word against every other word, turn those comparisons into weights, use the weights to decide what to pay attention to. The real formula is saved for Stage 2 on purpose, this is just the shape of the idea.

**topic_4_mixture_of_experts** — also runs with no internet needed. A toy router with 8 experts, activating only 2 per token. This is the actual architecture behind `openai/gpt-oss-120b`, the model used throughout this stage, and it's why that model runs at roughly half the speed of the smaller one rather than six times slower.

## Before you start

You need:

- Python 3.10 or newer
- VS Code with the Python extension installed (search "Python" in the Extensions panel, it's the Microsoft one)
- A free API key from one provider. Pick one:
  - **Groq** (fastest to set up) — go to console.groq.com, sign up, create a key. No credit card needed. The default model here is `openai/gpt-oss-20b` (small and fast); the other free text models at the time of writing are `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`, and `qwen/qwen3.8-27b`. Groq rotates this list, so if calls start failing, check console.groq.com/docs/rate-limits for what's currently free.
  - **Google AI Studio (Gemini)** — aistudio.google.com, generate a key. The free tier covers the Flash models.
  - **Ollama (local, no key at all)** — install from ollama.com, then run `ollama pull qwen2.5:7b` once. Everything after that runs on your own machine, no rate limit, no network call.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and fill in `LLM_PROVIDER` and `LLM_API_KEY`. If you're using Ollama, leave `LLM_API_KEY` blank and make sure `ollama serve` is running in another terminal first.

## Running each topic

```bash
python3 src/topic_1_tokens_and_counting/main.py
python3 src/topic_2_same_prompt_different_answers/main.py
python3 src/topic_3_attention_rough_shape/main.py
python3 src/topic_4_mixture_of_experts/main.py
```

Topics 3 and 4 need nothing else and will work immediately. Topics 1 and 2 need your API key to actually be valid, since they make real calls to a real provider. (Topic 2's opening demo — the part showing requests carry no weights — runs offline either way.)

## Tests

```bash
pytest tests/
```

Topic 3 has an automated test, and there's a small offline test of the shared client that runs it against a fake local HTTP server to check the request and response handling. Topic 4's router has a test too, since it's fully offline — it just checks the router picks exactly the top-2 scoring experts. Topics 1 and 2 call a live API, so they're meant to be run and read by eye, not asserted on in a test suite.

## A note on how this was built

The request format for each provider (Groq, Gemini) was written against each provider's own documentation and smoke-tested against a fake local server to check the request and response handling actually works. It has not been run against the real, live APIs, since this was put together somewhere with no internet access. If a request shape needs a small adjustment once you run it for real, that's a normal first pass, not something done carelessly. Topic 3 has been run for real and its output is in the code's own docstring.

## What you should be able to explain once you're done

- What a token actually is, and why it isn't the same thing as a word or a character
- Why sending the same prompt twice doesn't always give you the same answer, and why that has nothing to do with the model forgetting anything
- The rough shape of what attention is doing, in plain terms, before you've seen the actual formula

## Reading material

The `reading/` folder has one file per topic — each one goes deeper on exactly what that topic's code demonstrates, with a short list of the best current resources on it. Read a topic's file before or after running its code; either order works.

## Next

Stage 2 picks up the math this stage deliberately left out: the real attention formula, RoPE, and the loss functions behind fine-tuning. Nothing here needs to be memorized first, just understood once.
