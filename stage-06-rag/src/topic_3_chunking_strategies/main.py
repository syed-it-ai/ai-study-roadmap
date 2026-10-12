"""
Before anything gets embedded or indexed, a document has to be cut
into chunks. Where you cut matters as much as how you search
afterward: a chunk boundary that lands in the middle of a sentence can
split a fact in half, so that neither resulting chunk contains the
whole answer. Fully offline, no API call needed to see this.
"""

DOCUMENT = (
    "Our standard shipping takes 5 to 7 business days. Express shipping, "
    "available at checkout for an additional fee, delivers within 2 "
    "business days. International orders may take 10 to 14 business days "
    "depending on customs processing. Orders over $50 qualify for free "
    "standard shipping automatically applied at checkout."
)


def fixed_size_chunks(text: str, chunk_size: int) -> list:
    """The naive approach: cut every N characters, no awareness of
    sentence or word boundaries at all."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def sentence_aware_chunks(text: str, max_chunk_size: int) -> list:
    """Split on sentence boundaries first, then group sentences together
    up to the size limit, never splitting a sentence itself."""
    raw_sentences = [s.strip() for s in text.split(". ") if s.strip()]
    sentences = [s if s.endswith(".") else s + "." for s in raw_sentences]

    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_chunk_size:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def contains_complete_fact(chunk: str, fact_keywords: list) -> bool:
    """A crude but honest check: does this one chunk contain every
    keyword needed to answer a specific question, or did the fact get
    split across a chunk boundary?"""
    return all(kw.lower() in chunk.lower() for kw in fact_keywords)


def main() -> None:
    print(f"Original document ({len(DOCUMENT)} characters):\n{DOCUMENT}\n")

    chunk_size = 80

    print(f"=== Fixed-size chunking, {chunk_size} characters per chunk ===")
    fixed = fixed_size_chunks(DOCUMENT, chunk_size)
    for i, chunk in enumerate(fixed, 1):
        print(f"  Chunk {i}: {chunk!r}")

    print(f"\n=== Sentence-aware chunking, up to {chunk_size} characters ===")
    aware = sentence_aware_chunks(DOCUMENT, chunk_size)
    for i, chunk in enumerate(aware, 1):
        print(f"  Chunk {i}: {chunk!r}")

    # Check whether the "express shipping takes 2 business days" fact
    # survives intact in at least one chunk under each strategy.
    fact_keywords = ["express", "2 business days"]

    fixed_intact = any(contains_complete_fact(c, fact_keywords) for c in fixed)
    aware_intact = any(contains_complete_fact(c, fact_keywords) for c in aware)

    print(f"\nDoes any single chunk contain the complete 'express shipping, 2 business days' fact?")
    print(f"  Fixed-size chunking:    {'yes' if fixed_intact else 'no, split across chunks'}")
    print(f"  Sentence-aware chunking: {'yes' if aware_intact else 'no, split across chunks'}")

    print(
        "\nA fixed-size cutoff has no idea it's about to slice a fact in "
        "half. When that happens, a search can retrieve the exact right "
        "chunk and still not contain a complete answer, because the other "
        "half of the sentence landed in the next chunk over, which may not "
        "even get retrieved."
    )


if __name__ == "__main__":
    main()
