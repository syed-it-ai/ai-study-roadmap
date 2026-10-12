# Stage 7 — Tools, MCP, and computer use

Four things to run. This stage covers tool safety and the Model Context Protocol's current state after its largest specification revision since launch, confirmed against the spec's own changelog, not an older snapshot.

## What's actually in here

**topic_1_tool_schema_safety** — the same ambiguous request sent against two versions of a cancel_subscription tool. The vague one lets the model guess at an account. The scoped one, with a required field and an explicit no-inference instruction, makes it ask instead.

**topic_2_mcp_stateless_protocol** — fully offline. The actual before-and-after message shapes from MCP's July 2026 spec revision: a three-message stateful handshake collapsing into one self-contained stateless request.

**topic_3_mcp_deprecated_primitives** — fully offline. Roots, Sampling, and Logging, all deprecated under SEP-2577, and the one replacement pattern (explicit arguments instead of a mid-call back-channel) that fixes all three.

**topic_4_tool_permission_scoping** — fully offline. The same dangerous tool, blocked for two scopes and reachable for a third, demonstrating that scoping and schema design are different, complementary safety mechanisms.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key. Only topic 1 needs it.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Running each topic

```bash
python src/topic_1_tool_schema_safety/main.py
python src/topic_2_mcp_stateless_protocol/main.py
python src/topic_3_mcp_deprecated_primitives/main.py
python src/topic_4_tool_permission_scoping/main.py
```

Topics 2, 3, and 4 work immediately with no key at all.

## Tests

```bash
pytest tests/
```

12 tests, the most of any stage so far, covering topics 2, 3, and 4 in full, since all three are fully offline.

## A note on how this was built

Topic 1's `tool_chat` method was confirmed against Groq's own tool-calling support and smoke-tested against a fake local server to verify the request shape and that a required field actually changes model behavior in the mock response. It has not been run against the real, live Groq API, since this was built with no internet access. The MCP protocol details in topics 2 and 3 (the stateless shift, the specific deprecated primitives, the SEP numbers) were checked directly against the spec's own 2026-07-28 changelog and cross-confirmed across multiple independent migration guides, not taken from a single source.

## What you should be able to explain once you're done

- Why a tool's required fields and description are the real safety boundary, not the system prompt around them
- What changed in MCP's July 2026 spec revision, and why statelessness matters for how a server scales
- Which three primitives are deprecated, why they share one root cause, and what replaces them
- The difference between tool schema safety and tool permission scoping, and why a system needs both

## Next

Stage 8 moves into agents and multi-agent systems: the workflow-vs-agent distinction, tool idempotency for anything with a real side effect, and the frameworks (LangGraph, CrewAI, PydanticAI) that structure all of this into something runnable.
