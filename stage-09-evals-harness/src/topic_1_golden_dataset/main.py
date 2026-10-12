"""
A golden dataset built from twenty easy, invented questions proves
almost nothing about real-world performance. The confirmed current
practice: pull from actual logged production failures, especially ones
that previously went wrong, and treat the set as living, versioned,
and growing, never frozen on day one. Fully offline, no model call
needed to demonstrate the structure.
"""

import json
from datetime import datetime


class GoldenDataset:
    """
    A versioned, append-only eval set. Every entry traces back to a
    real event, not an invented example, and the dataset records when
    and why each entry was added.
    """

    def __init__(self):
        self.entries = []
        self.version = 0

    def add_from_production_failure(self, input_text: str, expected_behavior: str, source_incident: str):
        """The confirmed current practice: pull from a real failure,
        not from imagination. source_incident ties every entry back to
        something that actually happened."""
        self.entries.append({
            "input": input_text,
            "expected_behavior": expected_behavior,
            "source": source_incident,
            "added": datetime.now().isoformat(timespec="seconds"),
            "added_in_version": self.version + 1,
        })
        self.version += 1

    def summary(self) -> dict:
        return {
            "version": self.version,
            "total_entries": len(self.entries),
            "sources": [e["source"] for e in self.entries],
        }

    def export(self) -> str:
        return json.dumps(self.entries, indent=2)


def main() -> None:
    dataset = GoldenDataset()

    # Each entry below is modeled on a real kind of production failure,
    # the honest version of how a golden set actually grows: not
    # written in one afternoon, but accumulated from real incidents.
    dataset.add_from_production_failure(
        input_text="Can I get a refund, I'm not happy",
        expected_behavior="Should ask for an order number before processing anything, never assume",
        source_incident="2026-01: bot processed a refund with no order reference, wrong account charged",
    )
    dataset.add_from_production_failure(
        input_text="my emial is john@compnay.com typo above",
        expected_behavior="Should recognize the correction and use the corrected email, not the typo",
        source_incident="2026-02: bot sent confirmation to the misspelled address from the first message",
    )
    dataset.add_from_production_failure(
        input_text="cancel order 4471 and also order 4472",
        expected_behavior="Should confirm both order numbers explicitly before cancelling either",
        source_incident="2026-03: bot cancelled only the first order, user assumed both were done",
    )

    print(f"Golden dataset after 3 real incidents:\n{dataset.export()}\n")
    print("Summary:", dataset.summary())

    print(
        "\nNone of these three entries were invented to be easy. Each one "
        "is modeled on a specific way the system actually failed in "
        "production. A dataset like this is harder to build than twenty "
        "clean invented questions, and it tests exactly the failure modes "
        "that matter, because it is made of them."
    )
    print(
        "\nThe version number is not decoration. It's how a team tracks "
        "that this set is still growing. A golden dataset that stops "
        "growing is testing against a version of production traffic that "
        "stopped existing the day it was frozen."
    )


if __name__ == "__main__":
    main()
