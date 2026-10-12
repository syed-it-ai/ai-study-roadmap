"""
Every number in a model's weights got to its current value because of
this loop, run billions of times: make a prediction, measure how wrong
it was with cross-entropy, compute the gradient (which direction makes
it less wrong), nudge every weight slightly in that direction, repeat.

This shows the whole loop on one weight, small enough to watch it
actually learn across a few steps.
"""

import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def cross_entropy(probs: np.ndarray, true_index: int) -> float:
    """The loss: negative log of the probability assigned to the correct answer."""
    return -np.log(probs[true_index] + 1e-12)


def main() -> None:
    # A tiny model: one input feature, three possible output classes,
    # a 1x3 weight matrix is the model's entire parameter set.
    true_class = 2  # the correct answer is always class index 2
    x = 1.0         # the one input feature, fixed for this toy example
    weights = np.array([0.1, 0.1, 0.1])  # starts with no real preference
    learning_rate = 0.5

    print(f"Training to predict class {true_class}, starting from equal weights {weights}\n")

    for step in range(6):
        logits = weights * x
        probs = softmax(logits)
        loss = cross_entropy(probs, true_class)

        # The gradient of cross-entropy plus softmax, worked out, is this
        # clean expression: predicted probabilities minus a one-hot vector
        # of the true class, scaled by the input. This is not an
        # approximation, it is the exact derivative for this setup.
        target = np.zeros(3)
        target[true_class] = 1.0
        gradient = (probs - target) * x

        print(f"Step {step}: probs = {np.round(probs, 3)}, loss = {loss:.4f}")

        weights = weights - learning_rate * gradient

    print(f"\nFinal weights: {np.round(weights, 3)}")
    print(
        f"\nThe weight for class {true_class} grew, and the other two shrank, "
        f"purely because the gradient at every step pointed that direction. "
        f"Nothing was hand-tuned. The loss went down because the gradient is, "
        f"by construction, the direction that decreases it fastest."
    )
    print(
        "\nThis exact loop, forward pass, cross-entropy, gradient, weight update, "
        "run across billions of parameters and trillions of tokens, is the "
        "entire mechanism behind how a model's weights get to their final values."
    )


if __name__ == "__main__":
    main()
