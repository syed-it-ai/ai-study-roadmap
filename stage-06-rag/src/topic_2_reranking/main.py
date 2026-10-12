"""
Hybrid search is fast and cheap, run across an entire corpus. Reranking
is slower and more expensive, run only on the handful of candidates
hybrid search already narrowed things down to. The research number
worth knowing: Anthropic's own Contextual Retrieval work found that
combining contextual embeddings with BM25 got the top-20 retrieval
failure rate down to 5.7%, and adding a reranking stage on top of that
cut it further to 1.9%, a 67% reduction. Without any reranking, the
same setup's failure rate was 49%.

This uses the live model itself as the reranker, asking it to score
relevance directly, a real and current pattern, not a toy substitute.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "topic_1_hybrid_search"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient
from src.topic_1_hybrid_search.main import DOCUMENTS, bm25_scores, dense_scores, reciprocal_rank_fusion

load_dotenv()


def llm_rerank(client: LLMClient, query: str, candidates: list) -> list:
    """Ask the model to score each candidate's relevance directly, 0 to
    10. This is slower and costs real tokens, which is exactly why it
    only runs on the handful of candidates hybrid search already
    narrowed down, never the whole corpus."""
    scored = []
    for doc in candidates:
        prompt = (
            f'Query: "{query}"\n'
            f'Passage: "{doc}"\n\n'
            f"On a scale of 0 to 10, how directly does this passage answer "
            f"the query? Reply with only the number."
        )
        response = client.chat(prompt=prompt, temperature=0.0, max_tokens=5)
        try:
            score = float(response.text.strip())
        except ValueError:
            score = 0.0
        scored.append((doc, score))
    return sorted(scored, key=lambda x: x[1], reverse=True)


def main() -> None:
    client = LLMClient()
    query = "how long does a refund take"

    bm25 = bm25_scores(query, DOCUMENTS)
    dense = dense_scores(query, DOCUMENTS)
    fused = reciprocal_rank_fusion([bm25, dense])

    top_candidates_idx = sorted(range(len(DOCUMENTS)), key=lambda i: fused[i], reverse=True)[:4]
    top_candidates = [DOCUMENTS[i] for i in top_candidates_idx]

    print(f'Query: "{query}"\n')
    print("Top 4 from hybrid search, before reranking:")
    for i, doc in enumerate(top_candidates, 1):
        print(f"  {i}. {doc}")

    print("\nReranking these 4 with the model itself as the scorer:\n")
    reranked = llm_rerank(client, query, top_candidates)
    for i, (doc, score) in enumerate(reranked, 1):
        print(f"  {i}. [{score:.0f}/10] {doc}")

    print(
        "\nIf the order changed, that's reranking doing its job: hybrid "
        "search is good at finding plausible candidates fast, but a direct "
        "relevance judgment on each one, slower and only run on a handful, "
        "catches ordering mistakes hybrid search's cheaper signals miss."
    )
    print(
        "\nAnthropic's own measured numbers put this in perspective: adding "
        "reranking on top of an already-good hybrid setup cut retrieval "
        "failures from 5.7% to 1.9%. The gap without any reranking at all "
        "was far larger, a 49% failure rate on the same benchmark."
    )


if __name__ == "__main__":
    main()
