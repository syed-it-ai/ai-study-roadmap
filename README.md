# AI Study Roadmap

One repo, the whole track. Each stage is a folder. Work them in order — every stage assumes you ran the one before it.

This isn't a course you watch. It's a course you run. Every stage has code you execute, tests you can break, and reading that explains what the code just showed you.

## The rule that governs everything here

Zero spend. Every API call in this repo goes to a free tier — Groq first (no card), Ollama on your own machine as the fallback. If a stage needs a key, its folder tells you where to get one free and where to put it (a local `.env`, never committed).

## The stages

**stage-01-foundations** — what an LLM actually is, before the math. Tokens, why the same prompt gives different answers, the rough shape of attention, and how mixture-of-experts routing works. Some topics call a free model; the rest run offline.

**stage-02-math** — the math that actually shows up in papers and docs: the attention formula with real numbers, RoPE positional encoding, gradient descent on one weight, and DPO loss. All offline, no key needed.

**stage-03-apis** — getting structured data out of a model reliably. Contract prompts, strict-mode structured output (constrained decoding, not just "please return JSON"), schema vs semantic validation, and a small ticket classifier that stacks all three. Topics 1, 2 and 4 call Groq's free tier; topic 3 runs offline.

More stages land here as they're built — RAG, agents, evals, fine-tuning, deployment, and the rest, one folder at a time.

## How each stage folder works

- `src/` — the code, one folder per topic, each with a runnable demo.
- `tests/` — pytest. Run them; break them; that's how you learn what the code guarantees.
- `reading/` — one file per topic: what the code demonstrated, a deeper explanation, and a short list of resources worth your time. Diagrams live in `reading/images/`.
- `README.md` — the stage's own guide: what it covers, what to install in VS Code, how to run everything.

## Try it

Pick a stage, open its README, follow it. That's the whole process.
