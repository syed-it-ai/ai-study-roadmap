"""
Knowledge distillation trains a smaller student model to mimic a
larger teacher's full probability distribution over possible answers,
not just the teacher's single final answer. This is the fourth
technique belonging alongside quantization, confirmed directly in this
project's main roadmap as the way a team gets most of a large model's
quality into something small enough to deploy cheaply. Fully offline:
both the teacher's and student's outputs are plain probability
distributions, no API call needed to show the mechanism.
"""

import numpy as np


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    scaled = logits / temperature
    exp = np.exp(scaled - np.max(scaled))
    return exp / exp.sum()


def hard_label_loss(student_probs: np.ndarray, true_class: int) -> float:
    """Standard training: only the single correct class matters. This
    is what training from scratch on labeled data alone looks like."""
    return -np.log(student_probs[true_class] + 1e-12)


def soft_label_loss(student_probs: np.ndarray, teacher_probs: np.ndarray) -> float:
    """Distillation: the student is trained to match the teacher's
    entire distribution, not just its top answer. Cross-entropy against
    the teacher's full probability vector, not a single one-hot label."""
    return -np.sum(teacher_probs * np.log(student_probs + 1e-12))


def main() -> None:
    classes = ["billing", "technical", "account", "other"]
    true_class_idx = 0  # the genuinely correct answer is "billing"

    # The teacher, large and well-trained, is confident but not
    # absolutely certain, correctly reflecting real uncertainty: this
    # ticket is mostly about billing, with a little technical overlap.
    teacher_logits = np.array([4.0, 1.5, 0.5, 0.2])
    teacher_probs = softmax(teacher_logits, temperature=2.0)  # a higher temperature softens the distribution for distillation

    print(f"Teacher's full distribution over {classes}:")
    for c, p in zip(classes, teacher_probs):
        print(f"  {c:10s}: {p:.3f}")

    # A small, undertrained student, early in training, still fairly
    # uncertain and not yet matching the teacher.
    student_logits = np.array([1.0, 0.8, 0.5, 0.3])
    student_probs = softmax(student_logits, temperature=2.0)

    print(f"\nStudent's current distribution:")
    for c, p in zip(classes, student_probs):
        print(f"  {c:10s}: {p:.3f}")

    hard_loss = hard_label_loss(student_probs, true_class_idx)
    soft_loss = soft_label_loss(student_probs, teacher_probs)

    print(f"\nHard-label loss (only cares about 'billing' being right): {hard_loss:.4f}")
    print(f"Soft-label distillation loss (matching the teacher's full distribution): {soft_loss:.4f}")

    print(
        "\nThe hard-label loss only ever sees one number: how confident is "
        "the student in the single correct class. It has no way to know "
        "the teacher also saw a little technical overlap in this example, "
        "information that's actually useful, a signal about which other "
        "classes are plausible near-misses. The soft-label loss carries "
        "that entire shape of the teacher's belief into the student's "
        "training signal, not just its final answer."
    )
    print(
        "\nThe real limitation, confirmed directly in this project's main "
        "roadmap: a distilled model inherits the teacher's blind spots and "
        "genuinely cannot exceed what the teacher itself knows. Distillation "
        "shrinks a model. It does not improve on the source it's learning "
        "from."
    )


if __name__ == "__main__":
    main()
