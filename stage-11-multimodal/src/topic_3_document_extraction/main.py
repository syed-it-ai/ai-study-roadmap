"""
A real document-extraction pipeline has a vision model or an OCR tool
like Docling turn a scanned invoice into raw text first. This project's
sandbox has no vision model access and no image files, so the raw text
below is explicitly a simulated OCR result, labeled as such, standing
in for what a real vision call would have already produced. The part
this topic actually demonstrates, structuring and validating that raw
text into clean fields, is identical regardless of which tool produced
the text in the first place, and it's where most of the real
engineering effort in a document pipeline goes anyway.
"""

import re


# Explicitly simulated: this is what Docling or a vision model's OCR
# output would look like after reading a scanned invoice, not a real
# extraction, since no vision model or image file is available here.
SIMULATED_OCR_OUTPUT = """
INVOICE #INV-88214
Date: 2026-09-15
Bill To: Acme Logistics
Amount Due: $1,247.50
Due Date: 2026-10-15
"""


def extract_fields(raw_text: str) -> dict:
    """
    The structuring step: turning loosely-formatted OCR text into a
    strict schema. This is the same schema-first pattern from Stage 3,
    applied here to document fields instead of a chat response.
    """
    patterns = {
        "invoice_number": r"INVOICE #(\S+)",
        "date": r"Date:\s*(\d{4}-\d{2}-\d{2})",
        "bill_to": r"Bill To:\s*(.+)",
        "amount_due": r"Amount Due:\s*\$([\d,]+\.\d{2})",
        "due_date": r"Due Date:\s*(\d{4}-\d{2}-\d{2})",
    }
    fields = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, raw_text)
        fields[name] = match.group(1).strip() if match else None
    return fields


def semantic_validate(fields: dict) -> list:
    """
    The validation layer from Stage 3's schema-vs-semantic distinction,
    applied here: the fields can be perfectly well-formed and still be
    wrong in a way only a content check catches.
    """
    warnings = []

    if fields.get("amount_due"):
        amount = float(fields["amount_due"].replace(",", ""))
        if amount > 10_000:
            warnings.append(f"Amount due (${amount:,.2f}) is unusually large, worth a second look before processing.")
        if amount <= 0:
            warnings.append(f"Amount due (${amount:,.2f}) is zero or negative, likely an extraction error.")

    if fields.get("date") and fields.get("due_date"):
        if fields["due_date"] < fields["date"]:
            warnings.append("Due date is earlier than the invoice date, which is not physically possible.")

    missing = [k for k, v in fields.items() if v is None]
    if missing:
        warnings.append(f"Fields the extraction couldn't find at all: {missing}")

    return warnings


def main() -> None:
    print("Simulated OCR output (explicitly not a real vision call, no image or vision model available here):")
    print(SIMULATED_OCR_OUTPUT)

    fields = extract_fields(SIMULATED_OCR_OUTPUT)
    print("Extracted fields:")
    for k, v in fields.items():
        print(f"  {k}: {v}")

    warnings = semantic_validate(fields)
    print(f"\nSemantic validation: {'no issues found' if not warnings else 'issues found'}")
    for w in warnings:
        print(f"  - {w}")

    print(
        "\nEvery field extracted cleanly here, and the amount, roughly "
        "$1,247, is unremarkable, so validation found nothing. That's the "
        "clean case. Here's one that isn't:"
    )

    problem_ocr = """
INVOICE #INV-99001
Date: 2026-09-15
Bill To: Acme Logistics
Amount Due: $124,750.00
Due Date: 2026-09-01
"""
    print(f"\nA second simulated OCR result, with two real problems planted in it:{problem_ocr}")
    problem_fields = extract_fields(problem_ocr)
    print("Extracted fields:")
    for k, v in problem_fields.items():
        print(f"  {k}: {v}")
    problem_warnings = semantic_validate(problem_fields)
    print(f"\nSemantic validation: {'no issues found' if not problem_warnings else 'issues found'}")
    for w in problem_warnings:
        print(f"  - {w}")

    print(
        "\nBoth fields extracted perfectly cleanly, exactly matching the "
        "schema, a decimal amount and two valid dates. The extraction step "
        "alone would have approved both. Only the semantic check, looking "
        "at what the numbers actually mean together, catches that the due "
        "date comes before the invoice date and that $124,750 is an "
        "unusually large amount worth a second look before this gets "
        "processed automatically."
    )
    print(
        "\nThis is the same schema-then-semantics pattern from Stage 3, "
        "applied to a different kind of input. The vision or OCR call "
        "that would produce real text from a real scanned document is "
        "the part this sandbox cannot run. Everything after that call, "
        "which is most of the actual engineering work in a document "
        "pipeline, is identical regardless of which tool produced the text."
    )


if __name__ == "__main__":
    main()
