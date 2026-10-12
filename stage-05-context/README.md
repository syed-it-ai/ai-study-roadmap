# Stage 5 — Context engineering

Four things to run. "Context engineering" is the 2026 term for what used to be called prompt engineering: what belongs in a model's context window, what doesn't, and why a bigger window doesn't fix a reliability problem by itself.

## What's actually in here

**topic_1_lost_in_the_middle** — the same fact, the same question, asked three times with only its position in a long context changed. A real, currently-unsolved phenomenon, demonstrated on this project's own model, not just described.

**topic_2_compaction_strategies** — the same 10-turn conversation compacted three ways. Two strategies run fully offline; the third needs one real call to actually summarize meaning.

**topic_3_context_tiers** — fully offline. A `ContextAssembler` with three separate budgets. Its own eviction logic drops the most relevant fact in a test run, which is the real point: a tiered budget structurally helps, but doesn't automatically fix relevance.

**topic_4_agents_md** — the current cross-tool standard for giving a coding agent persistent project context. The same request, with and without a small AGENTS.md's conventions attached.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key. Topics 1 and 4 need it, and topic 2 needs it for its summarization step. Topic 3 needs nothing at all.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq key to `.env`.

## Running each topic

```bash
python src/topic_1_lost_in_the_middle/main.py
python src/topic_2_compaction_strategies/main.py
python src/topic_3_context_tiers/main.py
python src/topic_4_agents_md/main.py
```

Topic 3 works immediately with no key.

## Tests

```bash
pytest tests/
```

9 tests, covering topic 2's compaction logic and topic 3's tier budgeting, both fully offline.

## A note on how this was built

Topics 1, 2, and 4 call a live model and were smoke-tested for request correctness, not live-tested, same honest limitation as every stage so far. Topic 3's eviction bug (the refund policy getting dropped while less relevant content survived) is real and was found by actually running the code and reading the output, not predicted in advance. It's kept in deliberately, because it demonstrates the actual limitation of FIFO eviction better than a contrived example would have.

## What you should be able to explain once you're done

- Why "lost in the middle" happens, and why a bigger context window doesn't fix it
- The real tradeoff between a sliding window and summarization when compacting a conversation
- Why giving separate budgets to different context tiers helps, and what it still doesn't solve on its own
- What AGENTS.md is, how it differs from Claude Code's own CLAUDE.md, and why one wins when both are present

## Next

Stage 6 moves into RAG: hybrid search, reranking, and the specific finding that most production RAG failures are context-assembly problems, not retrieval-quality problems, which this stage's tiers and compaction work feeds directly into.
