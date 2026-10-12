"""
Not everything that ends up in a model's context belongs there the same
way. Three different tiers, each with a different lifetime and a
different budget: permanent instructions that never change, content
retrieved on demand for one specific request, and short-term session
memory that fades once the conversation moves on. This runs fully
offline. Assembling a prompt from these tiers is plain Python, no
API call needed to demonstrate the structure.
"""


class ContextAssembler:
    """
    Builds a final prompt from three tiers, each with its own token
    budget, so adding more of one tier never silently crowds out another.
    This is the structural fix for the context-budgeting problem this
    project's Stage 1 first ran into, now with named, separate tiers
    instead of one undifferentiated block of text.
    """

    def __init__(self, permanent_budget: int, retrieved_budget: int, session_budget: int):
        self.permanent_budget = permanent_budget
        self.retrieved_budget = retrieved_budget
        self.session_budget = session_budget
        self.permanent_instructions = ""
        self.retrieved_chunks = []
        self.session_turns = []

    def set_permanent(self, text: str):
        """The system prompt, rules, persona. Loaded on every single call."""
        tokens = _estimate_tokens(text)
        if tokens > self.permanent_budget:
            raise ValueError(f"Permanent instructions use {tokens} tokens, over the {self.permanent_budget} budget.")
        self.permanent_instructions = text

    def add_retrieved(self, chunk: str):
        """Content fetched for this specific request, like a RAG result.
        Dropped once the budget fills, oldest additions pruned first."""
        self.retrieved_chunks.append(chunk)
        while _estimate_tokens(" ".join(self.retrieved_chunks)) > self.retrieved_budget and len(self.retrieved_chunks) > 1:
            self.retrieved_chunks.pop(0)

    def add_session_turn(self, role: str, content: str):
        """Recent conversation. Oldest turns drop first once the
        session budget fills, same mechanism as Stage 2's sliding window."""
        self.session_turns.append((role, content))
        while _estimate_tokens(" ".join(c for _, c in self.session_turns)) > self.session_budget and len(self.session_turns) > 1:
            self.session_turns.pop(0)

    def assemble(self) -> str:
        parts = [f"[PERMANENT]\n{self.permanent_instructions}"]
        if self.retrieved_chunks:
            parts.append("[RETRIEVED]\n" + "\n".join(self.retrieved_chunks))
        if self.session_turns:
            parts.append("[SESSION]\n" + "\n".join(f"{r}: {c}" for r, c in self.session_turns))
        return "\n\n".join(parts)

    def budget_report(self) -> dict:
        return {
            "permanent": (_estimate_tokens(self.permanent_instructions), self.permanent_budget),
            "retrieved": (_estimate_tokens(" ".join(self.retrieved_chunks)), self.retrieved_budget),
            "session": (_estimate_tokens(" ".join(c for _, c in self.session_turns)), self.session_budget),
        }


def _estimate_tokens(text: str) -> int:
    return max(0, len(text) // 4)


def main() -> None:
    assembler = ContextAssembler(permanent_budget=50, retrieved_budget=60, session_budget=40)

    assembler.set_permanent("You are a support assistant. Be concise. Never promise refunds without approval.")

    assembler.add_retrieved("Refund policy: approved within 30 days of purchase with a receipt.")
    assembler.add_retrieved("Shipping policy: standard shipping takes 5 to 7 business days.")
    assembler.add_retrieved("Return policy: items must be unused and in original packaging.")
    assembler.add_retrieved("Warranty policy: electronics are covered for one year from the purchase date.")

    assembler.add_session_turn("user", "I want a refund for an order from 3 weeks ago.")
    assembler.add_session_turn("assistant", "Do you have your receipt handy?")
    assembler.add_session_turn("user", "Yes, I do.")

    print("Budget report (used / budget, in estimated tokens):")
    for tier, (used, budget) in assembler.budget_report().items():
        status = "OVER, oldest entries dropped" if used >= budget else "within budget"
        print(f"  {tier:10s}: {used:3d} / {budget:3d}  ({status})")

    print("\nAssembled prompt:")
    print(assembler.assemble())

    print(
        "\nLook at which retrieved fact actually survived. The refund policy, "
        "the one fact that is actually relevant to this user's refund "
        "question, was the first one added and got evicted once a fourth "
        "chunk pushed the tier over budget. Shipping and warranty, both "
        "irrelevant to this conversation, stayed."
    )
    print(
        "\nThis eviction is plain first-in-first-out, with no idea which "
        "chunk matters more. That is the real risk a tiered budget does not "
        "solve by itself: each tier fails on its own terms, which is better "
        "than one undifferentiated block silently losing the system prompt, "
        "but eviction order still has to be relevance-aware, not just "
        "oldest-first, or exactly this kind of mistake keeps happening."
    )


if __name__ == "__main__":
    main()
