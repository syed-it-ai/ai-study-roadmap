"""
Attention on its own has no idea about word order. "The bank paid the
client" and "the client paid the bank" would look identical to it,
because attention only compares vectors, and nothing in the attention
formula itself says where a token sits in the sentence.

RoPE (Rotary Positional Embeddings) fixes this by rotating each token's
query and key vectors by an angle based on their position, before the
attention formula from topic_1 ever runs. This is the current standard
across essentially every frontier open model (Llama, Qwen, Mistral,
DeepSeek) as of 2026.
"""

import numpy as np


def rotate(vec: np.ndarray, angle: float) -> np.ndarray:
    """
    RoPE rotates pairs of dimensions, not the whole vector at once, but
    the mechanism is identical to a 2D rotation, just applied to each
    pair. This toy version uses one 2D pair so the rotation is visible.
    """
    cos, sin = np.cos(angle), np.sin(angle)
    rotation_matrix = np.array([[cos, -sin], [sin, cos]])
    return rotation_matrix @ vec


def main() -> None:
    # Same key vector, same token in meaning, appearing at two
    # different positions in two different sentences.
    key_vector = np.array([1.0, 0.0])

    theta = 0.5  # radians per position step, a stand-in for RoPE's base frequency

    print("Same word, same embedding, two different sentence positions:\n")
    for position in [1, 5]:
        angle = theta * position
        rotated = rotate(key_vector, angle)
        print(f"Position {position}: rotated by {np.degrees(angle):.1f} degrees -> {np.round(rotated, 3)}")

    print(
        "\nWithout any rotation, this key vector would be identical no matter "
        "where the word appears. After rotating by an angle tied to position, "
        "the same word produces a different vector depending on where it sits."
    )

    # The actual point of RoPE: what matters is not the absolute angle,
    # but the *difference* in angle between a query and a key, which
    # depends only on how far apart they are, not where they sit
    # absolutely in the sequence.
    print("\nNow the part that matters: two tokens always 3 positions apart,")
    print("once near the start of a sequence, once much later.\n")

    query_vector = np.array([1.0, 0.0])

    for query_pos, key_pos, label in [(2, 5, "near the start"), (97, 100, "much later in a long sequence")]:
        q_rotated = rotate(query_vector, theta * query_pos)
        k_rotated = rotate(key_vector, theta * key_pos)
        dot_product = q_rotated @ k_rotated
        print(f"{label}: query at {query_pos}, key at {key_pos}, gap of {key_pos - query_pos}")
        print(f"  dot product after rotation: {dot_product:.4f}")

    print(
        "\nBoth pairs are exactly 3 positions apart, and both produce the same "
        "dot product after rotation. The model sees relative distance, 3 apart, "
        "the same way whether that gap happens at the start of a sequence or "
        "deep inside a very long one. That consistency is what lets a model "
        "trained on shorter sequences still behave sensibly on much longer ones, "
        "which plain additive position encoding does not do nearly as well."
    )


if __name__ == "__main__":
    main()
