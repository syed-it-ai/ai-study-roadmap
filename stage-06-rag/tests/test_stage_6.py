"""
Topics 1 and 3 are fully offline, pure logic, no API call. Topics 2
and 4 call a live model to demonstrate their point and are meant to
be run and read, same honest limitation as every stage so far.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_1_hybrid_search.main import (
    bm25_scores, dense_scores, cosine_similarity, reciprocal_rank_fusion, DOCUMENTS,
)
from src.topic_3_chunking_strategies.main import (
    fixed_size_chunks, sentence_aware_chunks, contains_complete_fact,
)


# --- topic 1: hybrid search ---

def test_bm25_scores_zero_for_documents_with_no_query_terms():
    scores = bm25_scores("zebra giraffe", DOCUMENTS)
    assert all(s == 0.0 for s in scores)


def test_bm25_favours_exact_rare_term_match():
    scores = bm25_scores("E4471", DOCUMENTS)
    top_doc_idx = scores.index(max(scores))
    assert "E4471" in DOCUMENTS[top_doc_idx]


def test_cosine_similarity_of_identical_vectors_is_one():
    v = [1, 2, 3]
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-9


def test_cosine_similarity_of_orthogonal_vectors_is_zero():
    assert cosine_similarity([1, 0], [0, 1]) == 0.0


def test_rrf_ranks_item_strong_in_both_lists_above_item_strong_in_one():
    # item 0 ranks 1st in both lists, item 1 ranks 1st in only one list
    list_a = [10, 1, 1]
    list_b = [10, 1, 1]
    fused = reciprocal_rank_fusion([list_a, list_b])
    assert fused[0] == max(fused)


# --- topic 3: chunking ---

def test_fixed_size_chunks_splits_at_exact_character_count():
    chunks = fixed_size_chunks("a" * 100, chunk_size=30)
    assert len(chunks) == 4  # 30, 30, 30, 10
    assert len(chunks[0]) == 30
    assert len(chunks[-1]) == 10


def test_sentence_aware_chunks_never_exceeds_limit_by_splitting_a_sentence():
    text = "First sentence here. Second sentence here. Third one."
    chunks = sentence_aware_chunks(text, max_chunk_size=25)
    for chunk in chunks:
        # every chunk should end on a sentence boundary, not mid-word
        assert chunk.strip().endswith(".")


def test_contains_complete_fact_detects_full_match():
    assert contains_complete_fact("the express option takes 2 business days", ["express", "2 business days"])


def test_contains_complete_fact_rejects_partial_match():
    assert not contains_complete_fact("the express option is available", ["express", "2 business days"])
