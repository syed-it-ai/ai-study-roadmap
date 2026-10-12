# AI Study Roadmap

One repo, the whole track. Each stage is a folder. Work them in order — every stage assumes you ran the one before it.

This isn't a course you watch. It's a course you run. Every stage has code you execute, tests you can break, and reading that explains what the code just showed you.

## The rule that governs everything here

Zero spend. Every API call in this repo goes to a free tier — Groq first (no card), Ollama on your own machine as the fallback. If a stage needs a key, its folder tells you where to get one free and where to put it (a local `.env`, never committed).

## The stages

**stage-01-foundations** — what an LLM actually is, before the math. Tokens, why the same prompt gives different answers, the rough shape of attention, and how mixture-of-experts routing works. Some topics call a free model; the rest run offline.

**stage-02-math** — the math that actually shows up in papers and docs: the attention formula with real numbers, RoPE positional encoding, gradient descent on one weight, and DPO loss. All offline, no key needed.

**stage-03-apis** — getting structured data out of a model reliably. Contract prompts, strict-mode structured output (constrained decoding, not just "please return JSON"), schema vs semantic validation, and a small ticket classifier that stacks all three. Topics 1, 2 and 4 call Groq's free tier; topic 3 runs offline.

**stage-04-reasoning** — when a reasoning model earns its extra latency and tokens. Reasoning effort levels on the gpt-oss models, self-consistency voting across samples, best-of-N with a verifier, and PRM vs ORM (why grading the steps beats grading only the final answer). Topics 1–3 call Groq's free tier; topic 4 runs offline.

**stage-05-context** — context engineering: what lives permanently in the prompt, what gets retrieved per request, and what fades with the session. Lost-in-the-middle, compaction strategies (sliding window vs summarize), context tier budgets with outside-in eviction, and AGENTS.md as the permanent-instruction file every coding tool reads. Topics 1, 2 and 4 call Groq's free tier; topic 3 runs offline.

**stage-06-rag** — production RAG, where the failures are usually in context assembly, not retrieval. Hybrid search (BM25 + dense fused with RRF), reranking the actually-relevant answer to the top, chunking strategies that don't split facts mid-sentence, and retrieve-first vs naive stuffing. Topics 1 and 3 run offline; topics 2 and 4 call Groq's free tier.

**stage-07-tools-mcp** — tools and MCP. The tool schema is the safety boundary: a vague schema lets the model guess an account and call anyway, a scoped one forces it to ask first. The current MCP revision (stateless protocol, self-contained messages), why Sampling/Roots/Logging were deprecated (SEP-2577 killed the back-channel), and permission scoping — same registry, three gates, three different reaches. Topics 2–4 run offline; topic 1 calls Groq's free tier.

**stage-08-agents** — agents and workflows. Workflows by default: who decides control flow, the programmer or the model at runtime. The ReAct loop (with a step budget, because a stuck loop never stops on its own), the Orchestrator-Workers pattern, and why side effects demand idempotency — 3 retries, 1 real charge instead of 3. Topic 3 runs offline; topics 1, 2 and 4 call Groq's free tier.

**stage-09-evals-harness** — evals that actually gate merges. A golden dataset grown from real incidents (not invented on day one), calibrating an LLM-as-judge against its documented false-negative rate, a CI gate that blocks the merge on exit code 1, and checkpoint recovery so a crashed run resumes instead of starting over. Topics 1, 3 and 4 run offline; topic 2 calls Groq's free tier.

**stage-10-fine-tuning** — fine-tuning, only after the eval baseline from stage 9. Which method for which signal (verifiable reward → GRPO, preference pairs → DPO, labeled examples → SFT, none → RLHF), the LoRA/DoRA math (131K trainable instead of 16.7M), GRPO's group-relative scoring with no value model, and knowledge distillation — why the teacher's soft labels carry signal hard labels throw away. All offline, no key needed.

**stage-11-multimodal** — voice is latency and turn-taking engineering. Turn-taking as a state machine (barge-in skips LISTENING entirely), where the milliseconds actually go (cascaded 830ms vs speech-to-speech 380ms — the LLM's own time-to-first-token is the bottleneck either way), cascaded vs speech-to-speech decided by debugging and voice-cloning needs before raw latency, and document extraction where the schema passes both invoices but only the semantic check catches the real problems. All offline, no key needed.

**stage-12-deployment** — serving and the self-host math. Continuous batching vs static (78% vs 40% GPU utilization on the same 16 requests), a provider gateway where the application code never changes across primary/fallback/total-failure, quantization memory math (FP8 as the 2026 default, INT4 when memory is the binding constraint), and the break-even line that depends entirely on which API you're actually comparing against — 6M tokens/day is right at the edge for frontier pricing and 80x short against cheap APIs. All offline, no key needed.

**stage-13-coding-agents** — coding agents, safety first. One SKILL.md read identically by 30+ tools (project priority beats user priority on conflict), a human approval gate where no code path reaches a real file without passing through it (approve/reject with no pending change raises, never silently no-ops), sandboxing as two independent gates — command and path, each blocking different attacks — and choosing a tool by confirmed differentiators, not brand preference. All offline, no key needed.

**stage-14-safety-security** — design against the lethal trifecta. Prompt injection defense in three layers, none sufficient alone (filtering alone is confirmed not reliable). Excessive agency scoping: the same $9,999 refund is blocked whether it came from a legitimate request or an injected one — the scope checks what the action would do, not where the instruction came from. The lethal trifecta detector: private data + untrusted content + external communication together is the only dangerous overlap. And an OWASP Top 10 audit that maps this specific app's features to the risks they actually trigger. All offline, no key needed.

More stages land here as they're built — staying current, and the rest, one folder at a time.

## How each stage folder works

- `src/` — the code, one folder per topic, each with a runnable demo.
- `tests/` — pytest. Run them; break them; that's how you learn what the code guarantees.
- `reading/` — one file per topic: what the code demonstrated, a deeper explanation, and a short list of resources worth your time. Diagrams live in `reading/images/`.
- `README.md` — the stage's own guide: what it covers, what to install in VS Code, how to run everything.

## Try it

Pick a stage, open its README, follow it. That's the whole process.
