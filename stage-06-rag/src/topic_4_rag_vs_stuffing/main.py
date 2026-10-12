"""
Frontier models now ship million-token context windows, which raises
a real question: why retrieve at all, why not just paste the whole
knowledge base into context every time? The current 2026 consensus,
confirmed across every production RAG source checked for this build,
is "RAG retrieves, long context refines": use retrieval to narrow a
large corpus down to the genuinely relevant handful of passages, then
let the model's larger context window work with that narrowed, clean
set, rather than skipping retrieval and stuffing everything in raw.

This connects directly to Stage 5's lost-in-the-middle finding. A
long, unfiltered context has more middle for a fact to get lost in.
A short, retrieved context has less room for that failure to even
occur.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient
from src.topic_1_hybrid_search.main import DOCUMENTS, bm25_scores, dense_scores, reciprocal_rank_fusion

load_dotenv()

# A larger, noisier "corpus" standing in for a real knowledge base,
# padded with distractor documents the query has nothing to do with.
DISTRACTOR_DOCS = [
    "Our office hours are 9am to 6pm, Monday through Friday.",
    "The company was founded in 2015 and has grown to 200 employees.",
    "New product announcements are posted to our blog every quarter.",
    "Employee parking is available in the garage on Fifth Street.",
    "Our annual conference takes place in the fall each year.",
    "Customer feedback surveys are sent out after every support ticket.",
    "The mobile app is available on both iOS and Android platforms.",
    "Team meetings are held every Monday morning at 10am.",
]

FULL_CORPUS = DOCUMENTS + DISTRACTOR_DOCS
QUESTION = "What is error code E4471?"


def naive_stuffing(client: LLMClient, question: str, corpus: list) -> str:
    """Skip retrieval entirely. Paste the whole corpus into context and
    hope the model finds the relevant part on its own."""
    context = "\n".join(corpus)
    prompt = f"{context}\n\nQuestion: {question}\nAnswer in one sentence."
    response = client.chat(prompt=prompt, temperature=0.0, max_tokens=60)
    return response.text.strip()


def retrieve_then_answer(client: LLMClient, question: str, corpus: list, top_k: int = 2) -> str:
    """Retrieve first, narrow the corpus down to the genuinely relevant
    handful, then let the model answer from just that."""
    bm25 = bm25_scores(question, corpus)
    dense = dense_scores(question, corpus)
    fused = reciprocal_rank_fusion([bm25, dense])
    top_idx = sorted(range(len(corpus)), key=lambda i: fused[i], reverse=True)[:top_k]
    narrowed_context = "\n".join(corpus[i] for i in top_idx)
    prompt = f"{narrowed_context}\n\nQuestion: {question}\nAnswer in one sentence."
    response = client.chat(prompt=prompt, temperature=0.0, max_tokens=60)
    return response.text.strip(), [corpus[i] for i in top_idx]


def main() -> None:
    client = LLMClient()

    print(f"Full corpus: {len(FULL_CORPUS)} documents, only 1 of which actually answers the question.")
    print(f"Question: {QUESTION}\n")

    print("Approach 1: naive stuffing, the entire corpus pasted into context")
    stuffed_answer = naive_stuffing(client, QUESTION, FULL_CORPUS)
    print(f"  Answer: {stuffed_answer}\n")

    print("Approach 2: retrieve first, narrow to the top 2 relevant documents, then answer")
    narrowed_answer, retrieved = retrieve_then_answer(client, QUESTION, FULL_CORPUS, top_k=2)
    print("  Retrieved:")
    for doc in retrieved:
        print(f"    - {doc}")
    print(f"  Answer: {narrowed_answer}")

    print(
        "\nBoth approaches had access to the same underlying fact somewhere "
        "in the full corpus. The difference is how much irrelevant material "
        "sat between the model and that fact. Stage 5 showed position "
        "within a long context affects reliability. This topic shows the "
        "other half of the same idea: cutting the irrelevant material "
        "entirely, with retrieval, removes the risk before position ever "
        "becomes a factor."
    )


if __name__ == "__main__":
    main()
