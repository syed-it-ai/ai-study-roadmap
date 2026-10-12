"""
What this shows you: the rough shape of attention, not the full formula.
The real formula (with query/key/value projections and the scaling term)
is deliberately saved for Stage 2's math work. Here, the goal is just to
see the core idea once, with numbers small enough to read by eye.

No API call needed for this one. It runs fully offline.
"""

import numpy as np


def attention_scores(query: np.ndarray, keys: np.ndarray) -> np.ndarray:
    """
    The core idea in one line: compare the query against every key with a
    dot product, then turn those comparison scores into weights that sum
    to one with softmax. Bigger dot product means "more related."
    """
    raw_scores = keys @ query
    exp_scores = np.exp(raw_scores - np.max(raw_scores))  # numerically stable softmax
    return exp_scores / exp_scores.sum()


def main() -> None:
    # A toy sentence, each word given a hand-picked tiny vector standing in
    # for a real learned embedding. The numbers are made up on purpose,
    # just large/small enough in the right places to make a point.
    words = ["The", "trophy", "didn't", "fit", "in", "the", "suitcase", "because", "it", "was", "too", "big"]

    # Hand-picked toy embeddings. "trophy" and "it" are built to be similar
    # (same first two numbers), "suitcase" is built to be dissimilar to "it".
    # Real embeddings are learned from data, never written by hand like this,
    # this is purely to make the mechanism visible.
    embeddings = {
        "trophy":   np.array([0.9, 0.8, 0.1]),
        "suitcase": np.array([0.1, 0.2, 0.9]),
        "it":       np.array([0.85, 0.75, 0.15]),
    }

    query = embeddings["it"]
    keys = np.array([embeddings["trophy"], embeddings["suitcase"]])
    key_labels = ["trophy", "suitcase"]

    weights = attention_scores(query, keys)

    print('Toy sentence: "The trophy didn\'t fit in the suitcase because it was too big"')
    print('Question this toy example is built to answer: what does "it" refer to?\n')
    for label, weight in zip(key_labels, weights):
        bar = "#" * int(weight * 40)
        print(f"  attention from 'it' -> '{label}':  {weight:.2f}  {bar}")

    winner = key_labels[int(np.argmax(weights))]
    print(f"\nHighest weight goes to '{winner}', because its toy embedding was built to be closest to 'it'.")
    print(
        "This is the rough shape of attention: compare a query against every "
        "available key, turn the comparisons into weights, use the weights to "
        "decide what to pay the most attention to. The real formula, including "
        "the query/key/value projections and the scaling term, is Stage 2."
    )


if __name__ == "__main__":
    main()
