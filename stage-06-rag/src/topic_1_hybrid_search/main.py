"""
Confirmed as the 2026 production default across every current source
checked for this build: hybrid search, running lexical (BM25) and
semantic (dense vector) retrieval in parallel and fusing the two
ranked lists with Reciprocal Rank Fusion. Pure dense search misses
exact terms, names, and IDs. Pure BM25 misses paraphrases and synonyms.
Hybrid wins because the two fail in different, complementary ways.

Both scorers are implemented from scratch here, no library standing
in for the mechanism. The "dense" vectors are plain word-frequency
vectors, a legitimate but simple vector space model, standing in for
a real learned embedding the same way Stage 1's toy embeddings did.
"""

import math
from collections import Counter


DOCUMENTS = [
    "Error code E4471 means the payment gateway timed out during checkout.",
    "To resolve a failed transaction, check your internet connection and retry.",
    "The refund process typically takes 5 to 7 business days to complete.",
    "Payment declined usually means insufficient funds or an expired card.",
    "Our support team can look up any order using the order confirmation number.",
    "E4471 has also been reported when the customer's bank blocks international charges.",
]


def tokenize(text: str) -> list:
    return text.lower().replace(".", "").replace(",", "").split()


# --- BM25, implemented from the actual formula, not a library ---

def bm25_scores(query: str, documents: list, k1: float = 1.5, b: float = 0.75) -> list:
    tokenized_docs = [tokenize(d) for d in documents]
    doc_lengths = [len(d) for d in tokenized_docs]
    avg_len = sum(doc_lengths) / len(doc_lengths)
    n_docs = len(documents)

    doc_freq = Counter()
    for doc in tokenized_docs:
        for term in set(doc):
            doc_freq[term] += 1

    query_terms = tokenize(query)
    scores = []
    for doc, length in zip(tokenized_docs, doc_lengths):
        term_counts = Counter(doc)
        score = 0.0
        for term in query_terms:
            if term not in term_counts:
                continue
            df = doc_freq.get(term, 0)
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)
            tf = term_counts[term]
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * length / avg_len)
            score += idf * numerator / denominator
        scores.append(score)
    return scores


# --- "dense" scoring: term-frequency vectors, cosine similarity ---
# A real system would use learned embeddings. This is a legitimate but
# simple vector space model, built from scratch to show the mechanism,
# the same honest stand-in approach Stage 1 used for toy embeddings.

def to_vector(text: str, vocabulary: list) -> list:
    counts = Counter(tokenize(text))
    return [counts.get(term, 0) for term in vocabulary]


def cosine_similarity(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def dense_scores(query: str, documents: list) -> list:
    vocabulary = sorted(set(tokenize(query) + [t for d in documents for t in tokenize(d)]))
    query_vec = to_vector(query, vocabulary)
    return [cosine_similarity(query_vec, to_vector(doc, vocabulary)) for doc in documents]


# --- Reciprocal Rank Fusion ---

def reciprocal_rank_fusion(score_lists: list, k: int = 60) -> list:
    """Standard RRF: rank each list separately, then score each item by
    the sum of 1/(k + rank) across every list it appears in. Items that
    rank well in multiple lists win, even if neither list alone scored
    them highest."""
    n_items = len(score_lists[0])
    fused = [0.0] * n_items
    for scores in score_lists:
        ranking = sorted(range(n_items), key=lambda i: scores[i], reverse=True)
        for rank, idx in enumerate(ranking):
            fused[idx] += 1.0 / (k + rank + 1)
    return fused


def main() -> None:
    query = "E4471 error during payment"

    bm25 = bm25_scores(query, DOCUMENTS)
    dense = dense_scores(query, DOCUMENTS)
    fused = reciprocal_rank_fusion([bm25, dense])

    print(f'Query: "{query}"\n')
    print(f"{'Document':<65s} {'BM25':>7s} {'Dense':>7s} {'Fused':>7s}")
    order = sorted(range(len(DOCUMENTS)), key=lambda i: fused[i], reverse=True)
    for i in order:
        doc_short = DOCUMENTS[i][:62] + ("..." if len(DOCUMENTS[i]) > 62 else "")
        print(f"{doc_short:<65s} {bm25[i]:>7.3f} {dense[i]:>7.3f} {fused[i]:>7.4f}")

    print(
        "\nNotice the exact error code 'E4471' matches lexically on two "
        "documents, which BM25 weights heavily since it's a rare, specific "
        "term. A pure dense search, with no concept of exact-match rarity, "
        "would not necessarily rank those two as highly. Fusing both signals "
        "is what lets an exact code and a paraphrased concept both surface "
        "near the top, instead of one search method missing what the other "
        "would have caught."
    )


if __name__ == "__main__":
    main()
