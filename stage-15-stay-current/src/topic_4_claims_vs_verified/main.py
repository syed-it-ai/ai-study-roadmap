"""
The single most repeated lesson across every one of the 14 stages
built before this one, confirmed directly by reviewing this project's
own stage-build-patterns.md: a claim that code "would catch" something,
or that a number "lands in the confirmed range," is worth nothing until
it's actually demonstrated. Real examples from this exact build: Stage
1's attention diagram used random embeddings that produced a
meaningless near-uniform result until hand-picked values proved the
mechanism. Stage 12's self-host calculator computed a 1.4x multiplier
while its own comments claimed a confirmed 3-5x figure, caught only by
actually running it. Stage 13's skill-priority conflict was never
actually a conflict until two genuinely different priorities were used.

This builds a real, generic scanner for exactly this pattern: claims in
code comments or documentation that assert something was verified,
cross-checked against whether a corresponding test or printed output
actually exists to back that claim up.
"""

import re


def extract_claims(text: str) -> list:
    """
    Finds sentences making a verification-flavored claim: confirmed,
    verified, proven, demonstrated, tested. These are exactly the words
    this project's own code comments use throughout, and exactly the
    words worth checking aren't doing more work than the evidence
    actually supports.
    """
    claim_patterns = r"\b(confirmed|verified|proven|demonstrated|tested)\b"
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if re.search(claim_patterns, s, re.IGNORECASE)]


def check_claim_has_backing(claim: str, available_evidence: list) -> dict:
    """
    A real, if simple, cross-check: does any piece of actual evidence
    (a test name, a printed output, a specific number) share enough
    vocabulary with the claim to plausibly back it up, or is the claim
    floating entirely on its own with nothing behind it.
    """
    claim_words = set(w.lower() for w in re.findall(r"[a-zA-Z]{4,}", claim))
    best_overlap = 0
    best_match = None
    for evidence in available_evidence:
        evidence_words = set(w.lower() for w in re.findall(r"[a-zA-Z]{4,}", evidence))
        overlap = len(claim_words & evidence_words)
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = evidence
    return {"has_backing": best_overlap >= 2, "best_match": best_match, "overlap": best_overlap}


def main() -> None:
    # A realistic docstring, the exact kind this project writes constantly,
    # containing one well-backed claim and one unbacked one.
    docstring = (
        "The real cost multiplier is confirmed as 4.0x in this build, "
        "matching the documented real-world range. "
        "This approach is proven to scale to production workloads of any size."
    )

    # The actual evidence available for this specific module: a test
    # name and a printed result, the kind of thing a real test suite
    # or script output would contain.
    available_evidence = [
        "test_real_multiplier_lands_in_confirmed_range asserts multiplier is 4.0",
        "printed output: Real cost multiplier: 4.0x the naive estimate",
    ]

    claims = extract_claims(docstring)
    print(f"Found {len(claims)} verification-flavored claims:\n")

    for claim in claims:
        result = check_claim_has_backing(claim, available_evidence)
        status = "BACKED" if result["has_backing"] else "UNBACKED, worth a second look"
        print(f"Claim: \"{claim}\"")
        print(f"  Status: {status}")
        if result["has_backing"]:
            print(f"  Matches: {result['best_match']}")
        print()

    print(
        "The multiplier claim is backed, a real test and a real printed "
        "output both support it directly, matching exactly how Stage 12's "
        "bug actually got caught in this project. The 'proven to scale to "
        "production workloads of any size' claim has nothing behind it in "
        "the available evidence, which is exactly the kind of sentence "
        "that reads confidently and means nothing, the thing this entire "
        "project has spent 14 stages trying not to write."
    )
    print(
        "\nThis scanner is deliberately simple, word-overlap is a weak "
        "signal, a real system would need something sturdier. What it "
        "gets right regardless: forcing the question 'what evidence "
        "actually backs this sentence' onto every confident-sounding "
        "claim, rather than trusting confident phrasing as its own proof."
    )


if __name__ == "__main__":
    main()
