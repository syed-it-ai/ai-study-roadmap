# Stage 6 — RAG: hybrid search, reranking, chunking, and when to retrieve at all

Four things to run. This stage covers the four levers current 2026 sources agree most RAG quality actually comes from, plus the question of whether retrieval is even still necessary now that context windows are enormous.

## What's actually in here

**topic_1_hybrid_search** — fully offline. BM25 and a simple dense scorer, both implemented from scratch, fused with Reciprocal Rank Fusion. The exact error code in the test query ranks correctly because BM25 catches what a pure dense search would likely miss.

**topic_2_reranking** — the model itself used as a reranker on the top 4 candidates from hybrid search. Cites Anthropic's own measured numbers: reranking cut retrieval failure from 5.7% to 1.9%.

**topic_3_chunking_strategies** — fully offline. The same document, cut two ways. Fixed-size chunking visibly slices a fact in half mid-word. Sentence-aware chunking doesn't.

**topic_4_rag_vs_stuffing** — the current "RAG retrieves, long context refines" consensus, tested directly: the same question, with and without retrieval narrowing the corpus first. Ties directly back to Stage 5's lost-in-the-middle finding.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key. Topics 2 and 4 need it. Topics 1 and 3 need nothing at all.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Running each topic

```bash
python src/topic_1_hybrid_search/main.py
python src/topic_2_reranking/main.py
python src/topic_3_chunking_strategies/main.py
python src/topic_4_rag_vs_stuffing/main.py
```

Topics 1 and 3 work immediately with no key.

## Tests

```bash
pytest tests/
```

9 tests, covering topic 1's BM25, cosine similarity, and RRF logic, and topic 3's chunking logic, both fully offline.

## A note on how this was built

No BM25 library was available offline, so it's implemented directly from the actual formula rather than imported, which also means the mechanism is fully visible rather than hidden behind a library call. The "dense" vectors in topics 1 and 4 are simple word-frequency vectors, a legitimate but basic vector space model, standing in for a real learned embedding the same honest way Stage 1's toy embeddings did. Topics 2 and 4 call a live model and were not live-tested, same limitation as every stage so far, since this was built with no internet access.

## What you should be able to explain once you're done

- Why hybrid search beats either BM25 or dense retrieval alone, with a concrete example of each one's blind spot
- Why reranking is cheap despite being slower per-item, and the real numbers (5.7% to 1.9%) that justify using it
- A concrete example of a fact a fixed-size chunker would split that a sentence-aware chunker wouldn't
- Why a million-token context window doesn't remove the need for retrieval, connected directly to Stage 5's lost-in-the-middle finding

## Next

Stage 7 moves into tools, MCP, and computer use: tool schemas as the actual safety boundary, and the current state of the Model Context Protocol after its mid-2026 revision.
