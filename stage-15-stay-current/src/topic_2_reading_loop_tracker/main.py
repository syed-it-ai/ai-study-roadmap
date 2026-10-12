"""
This project's own main roadmap names a specific loop as the one that
actually compounds: one conceptual article, one official docs page,
build a tiny version yourself, then reread the article once you have
scars from building it. Reading ten articles on one topic and building
nothing teaches less than running this loop once. This builds a real
tracker for that loop, since a habit that isn't tracked tends to quietly
stop at step one, article read, build never attempted.
"""

from enum import Enum, auto


class LoopStage(Enum):
    NOT_STARTED = auto()
    ARTICLE_READ = auto()
    DOCS_READ = auto()
    BUILT_SOMETHING = auto()
    REREAD_COMPLETE = auto()


class ReadingLoopTracker:
    """
    Tracks every topic's progress through the actual loop, not just
    whether an article was opened. The real value of this loop is
    specifically in the reread after building something, which is also
    the step most people skip once they feel like they already "get it"
    from the article alone.
    """

    def __init__(self):
        self.topics = {}

    def start_topic(self, topic: str):
        self.topics[topic] = LoopStage.NOT_STARTED

    def advance(self, topic: str, to_stage: LoopStage) -> dict:
        if topic not in self.topics:
            return {"success": False, "reason": f"'{topic}' was never started. Call start_topic first."}

        current = self.topics[topic]
        stage_order = list(LoopStage)
        if stage_order.index(to_stage) != stage_order.index(current) + 1:
            return {
                "success": False,
                "reason": f"Cannot jump from {current.name} to {to_stage.name}. "
                          f"The loop has to be run in order, no skipping the build step.",
            }
        self.topics[topic] = to_stage
        return {"success": True, "topic": topic, "new_stage": to_stage.name}

    def topics_stuck_before_building(self) -> list:
        """The specific failure mode this tracker exists to catch: a
        topic where the article was read but nothing was ever built."""
        return [t for t, stage in self.topics.items()
                if stage in (LoopStage.ARTICLE_READ, LoopStage.DOCS_READ)]

    def completion_rate(self) -> float:
        if not self.topics:
            return 0.0
        completed = sum(1 for s in self.topics.values() if s == LoopStage.REREAD_COMPLETE)
        return completed / len(self.topics)


def main() -> None:
    tracker = ReadingLoopTracker()

    for topic in ["RoPE extensions", "Continuous batching", "Agent harnesses", "GRPO"]:
        tracker.start_topic(topic)

    # Realistic, uneven progress: this is what actually happens.
    print("=== Realistic progress across four topics ===\n")
    tracker.advance("RoPE extensions", LoopStage.ARTICLE_READ)
    tracker.advance("RoPE extensions", LoopStage.DOCS_READ)
    tracker.advance("RoPE extensions", LoopStage.BUILT_SOMETHING)
    tracker.advance("RoPE extensions", LoopStage.REREAD_COMPLETE)
    print(f"RoPE extensions: {tracker.topics['RoPE extensions'].name}")

    tracker.advance("Continuous batching", LoopStage.ARTICLE_READ)
    print(f"Continuous batching: {tracker.topics['Continuous batching'].name}")

    tracker.advance("Agent harnesses", LoopStage.ARTICLE_READ)
    tracker.advance("Agent harnesses", LoopStage.DOCS_READ)
    print(f"Agent harnesses: {tracker.topics['Agent harnesses'].name}")

    print(f"GRPO: {tracker.topics['GRPO'].name}")

    print("\n=== Attempting to skip the build step ===\n")
    skip_attempt = tracker.advance("Continuous batching", LoopStage.REREAD_COMPLETE)
    print(skip_attempt)

    print(f"\nTopics stuck before ever building something: {tracker.topics_stuck_before_building()}")
    print(f"Overall completion rate: {tracker.completion_rate()*100:.0f}%")

    print(
        "\nTwo of four topics here are stuck exactly where the real "
        "failure mode happens: an article was read, maybe even the docs "
        "too, and nothing was ever actually built. The attempted skip "
        "from 'article read' straight to 'reread complete' was rejected, "
        "deliberately, because rereading an article without having built "
        "anything first produces none of the benefit this loop exists for."
    )


if __name__ == "__main__":
    main()
