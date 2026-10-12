# Stage 14 — Safety, security, and guardrails

Four things to run, all pure Python, no external library beyond pytest. Every topic here is purely defensive: detection, scoping, and auditing. None of this builds or catalogs attack techniques.

**Confirmed current for this build**: OWASP published the 2026 edition of its Top 10 for LLM Applications on August 3-4, 2026, two months before this stage was built, the third revision since the list began in 2023. This stage uses that current list directly, not an older snapshot.

## What's actually in here

**topic_1_prompt_injection_defense** — three defensive layers against LLM01:2026, the top-ranked risk every edition of this list has had since 2023: structural content isolation, pattern flagging, and output validation. Uses only the single canonical injection example every OWASP and security source cites, not a catalog of attack phrasings.

**topic_2_excessive_agency_scoping** — real action scoping against LLM03:2026, the single biggest promotion in the 2026 rewrite. The same attempted $9,999 refund gets blocked two different, independently defensible ways by two different scopes, and a reasonable $45 refund correctly goes through.

**topic_3_lethal_trifecta_detector** — a real check for Simon Willison's lethal trifecta: private data access, untrusted content exposure, and external communication, all three at once. Only the one agent configuration genuinely having all three gets flagged.

**topic_4_owasp_coverage_audit** — the full current 2026 list, audited against one realistic hypothetical application's actual features, producing exactly the findings that application's own design genuinely exposes it to.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- Nothing else. No API key, no provider account, no internet connection.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running each topic

```bash
python src/topic_1_prompt_injection_defense/main.py
python src/topic_2_excessive_agency_scoping/main.py
python src/topic_3_lethal_trifecta_detector/main.py
python src/topic_4_owasp_coverage_audit/main.py
```

All four work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

15 tests, covering all four topics in full.

## A note on how this was built

This stage deliberately builds detection and mitigation code only. The one injection example used in topic 1 ("ignore all previous instructions") is the single most widely published illustrative example across every OWASP document, security blog, and news article on this topic, not a novel technique. No topic in this stage compiles a list of attack phrasings or builds anything resembling attack tooling.

## What you should be able to explain once you're done

- Why filtering alone is confirmed as insufficient defense against prompt injection, and what each of three defensive layers actually catches
- Why OWASP promoted excessive agency to third place in 2026, and how a scope check stays reliable without needing to tell legitimate instructions apart from injected ones
- The specific three-capability combination that makes an agent genuinely dangerous, with a concrete example of two-of-three being safe and three-of-three not
- How to audit a real application's actual features against the current OWASP list, rather than treating every risk as equally relevant to every app

## Next

Stage 15 is the final stage: staying current. A living habit, not a one-time reading list, covering the newsletters, blogs, and living GitHub indexes worth checking on an ongoing basis as this field keeps moving.
