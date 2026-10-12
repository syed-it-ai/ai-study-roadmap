# Stage 8 — Agents and multi-agent systems

Four things to run. This is the agentic AI stage: the workflow-vs-agent distinction, the ReAct pattern (the default definition of "agent" in 2026), tool idempotency, and the Orchestrator-Workers multi-agent pattern, all built from scratch rather than through a framework.

## What's actually in here

**topic_1_workflow_vs_agent** — the same order-lookup task handled by a fixed three-step workflow and by a model deciding its response from what it observes. Tested against an order that doesn't exist, where the workflow's rigid steps have no good answer and the agent's runtime decision does.

**topic_2_react_loop** — the actual Thought-Action-Observation loop, implemented directly with a step budget, no framework. A mock-scripted test confirms the exact control flow: the model calls a tool, the observation feeds back in, the loop terminates on a final answer.

**topic_3_tool_idempotency** — fully offline. The same retry pattern against a naive and an idempotent payment tool. One triples a customer's charge. The other doesn't.

**topic_4_orchestrator_workers** — a lead agent splitting one task into two subtasks for two specialized workers, never doing the work itself. The same coordination pattern LangGraph implements as an explicit graph, built here with plain Python to make the mechanism visible.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key. Topics 1, 2, and 4 need it. Topic 3 needs nothing at all.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Running each topic

```bash
python src/topic_1_workflow_vs_agent/main.py
python src/topic_2_react_loop/main.py
python src/topic_3_tool_idempotency/main.py
python src/topic_4_orchestrator_workers/main.py
```

Topic 3 works immediately with no key.

## Tests

```bash
pytest tests/
```

10 tests, covering the deterministic workflow half of topic 1, topic 2's action-parsing logic, and all of topic 3.

## A note on how this was built

Topic 2's control flow was verified with a scripted mock before being trusted: a fake two-step trace confirmed the loop calls the right tool, feeds the observation back correctly, and terminates exactly on the final answer, not one step early or late. Topics 1, 2, and 4 call a live model and were not live-tested against the real Groq API, since this was built with no internet access. No multi-agent framework (LangGraph, CrewAI) could be installed offline, so topic 4's coordination logic is built directly, which also means the actual mechanism is visible rather than hidden behind a framework's abstraction.

## What you should be able to explain once you're done

- The real difference between a workflow and an agent, and why most production systems should default to the former
- The ReAct loop's three stages, why a step budget is not optional, and what its known long-horizon failure mode looks like
- A concrete example of a tool that needs idempotency and one that doesn't, with a real number showing the cost of skipping it
- What an orchestrator's job actually is, and why it should never do the work its workers were delegated to do

## Next

Stage 9 moves into evals, observability, and harnesses: building a golden dataset from real production failures, and the layer of tooling, retries, checkpoints, state, that separates a working agent from a fragile demo.
