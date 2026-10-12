# Stage 13 — AI coding agents

Four things to run, all pure Python, no external library beyond pytest. The fifth fully-offline stage in this project: skill discovery, safety harnesses, command sandboxing, and tool selection are all verifiable without a live model call.

## What's actually in here

**topic_1_skill_loader** — a real SKILL.md discovery and matching system, genuinely meta since this exact project has been using the same pattern (`stage-build-patterns.md`) throughout its own build. Proves, not just claims, that project-priority skills correctly override user-priority ones on conflict.

**topic_2_diff_approval_harness** — the real propose-diff-approve-apply pattern. A rejected change leaves zero trace in the applied history, and there's no code path from a proposed change to a real file write that skips the approval gate.

**topic_3_command_sandboxing** — two genuinely independent safety gates: an allowed-commands check and a path-boundary check. `cat /etc/passwd` proves the point directly, passing the command check and still getting blocked by the path check.

**topic_4_choosing_a_coding_agent** — a decision function grounded in confirmed current differentiators (Gemini CLI's sandboxing, Claude Code/Codex CLI's scripting depth), including the deliberately counterintuitive case where skill portability is correctly treated as no longer a real factor.

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
python src/topic_1_skill_loader/main.py
python src/topic_2_diff_approval_harness/main.py
python src/topic_3_command_sandboxing/main.py
python src/topic_4_choosing_a_coding_agent/main.py
```

All four work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

15 tests, covering all four topics in full.

## A note on how this was built

Topic 1's first version had two skills both marked `project` priority, which meant the priority-resolution logic never actually got exercised, only asserted to work in the surrounding text. Fixed by making one skill genuinely user-priority and the other project-priority, so the conflict the code claims to resolve is a real conflict the test suite actually tests, not a coincidence of two identical priorities never clashing.

## What you should be able to explain once you're done

- How SKILL.md's priority-based conflict resolution actually works, with a concrete example of a real conflict it resolves correctly
- Why a safety harness needs a structural guarantee, not just a convention, that no change reaches a real file without approval
- Why command sandboxing needs two independent checks, with a concrete example of a command that passes one and fails the other
- Which confirmed current differences actually distinguish coding agent tools, and which commonly-cited difference (skill portability) no longer applies

## Next

Stage 14 moves into safety, security, and guardrails: the OWASP Top 10 for LLM applications, and the lethal trifecta pattern (private data, untrusted content, external communication) worth recognizing before shipping any agent.
