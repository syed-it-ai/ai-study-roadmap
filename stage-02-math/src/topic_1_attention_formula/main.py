"""
Stage 1 showed the rough shape of attention: compare, weight, blend.
This is the actual formula that shape was standing in for:

    Attention(Q, K, V) = softmax( Q K^T / sqrt(d_k) ) V

In a real model, every token's embedding gets multiplied by three
separate learned weight matrices to produce its own Q, K, and V. The
projection step itself is just matrix multiplication, nothing new
after Stage 1's matrix multiply topic. What's new here is seeing what
happens once you have Q, K, and V: the compare, scale, and blend
steps, worked all the way through on real numbers.
"""

import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def main() -> None:
    d_k = 3

    # Q, K, V for three tokens, hand-picked so the result is easy to
    # read. In a real model these come from projecting an embedding
    # through three learned matrices, a plain matrix multiply, the
    # same operation covered in Stage 1's matrix multiplication topic.
    Q = {"cat": np.array([1.0, 0.8, 0.1])}
    K = {
        "The": np.array([0.1, 0.0, 0.2]),
        "cat": np.array([0.9, 0.7, 0.0]),
        "sat": np.array([1.0, 0.9, 0.1]),
    }
    V = {
        "The": np.array([0.0, 0.1, 0.0]),
        "cat": np.array([0.4, 0.3, 0.1]),
        "sat": np.array([0.8, 0.7, 0.2]),
    }

    print(f"d_k (key dimension) = {d_k}, so the scaling divisor is sqrt({d_k}) = {np.sqrt(d_k):.3f}\n")

    query_word = "cat"
    q = Q[query_word]
    keys = list(K.keys())
    K_matrix = np.array([K[w] for w in keys])
    V_matrix = np.array([V[w] for w in keys])

    raw_scores = K_matrix @ q
    print(f'Raw scores (Q . K^T) for "{query_word}" against every token:')
    for w, s in zip(keys, raw_scores):
        print(f"  {w:5s}: {s:.3f}")

    scaled_scores = raw_scores / np.sqrt(d_k)
    print(f"\nAfter dividing by sqrt(d_k):")
    for w, s in zip(keys, scaled_scores):
        print(f"  {w:5s}: {s:.3f}")

    weights = softmax(scaled_scores)
    print(f"\nAfter softmax, the actual attention weights:")
    for w, p in zip(keys, weights):
        print(f"  {w:5s}: {p:.3f}")

    output = weights @ V_matrix
    print(f"\nFinal output for \"{query_word}\" (weighted sum of all value vectors): {np.round(output, 3)}")

    winner = keys[int(np.argmax(weights))]
    print(
        f"\n\"{query_word}\" ends up attending most to \"{winner}\", because its key "
        f"was closest to \"{query_word}\"'s query. The output vector pulls mostly "
        f"from \"{winner}\"'s value as a result. This is the full formula, not a "
        f"simplification. A real model runs this exact sequence, compare, scale, "
        f"softmax, blend, for every token against every other token, across many "
        f"heads at once."
    )


if __name__ == "__main__":
    main()
