"""
Orchestrator-Workers, confirmed as one of the small set of named
multi-agent patterns that actually carry production systems in 2026:
a lead agent breaks a task into subtasks and delegates each one to a
specialized worker, then combines the results. Frameworks like
LangGraph implement this as an explicit graph. This builds the same
pattern directly, with plain Python and this project's own LLMClient,
so the actual coordination logic is visible rather than hidden behind
a framework's abstraction.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()


def worker_research(client: LLMClient, topic: str) -> str:
    """A specialized worker: only does research-style summarizing."""
    prompt = f"In two sentences, summarize the key considerations for: {topic}"
    return client.chat(prompt=prompt, temperature=0.3, max_tokens=100).text.strip()


def worker_risk_check(client: LLMClient, topic: str) -> str:
    """A different specialized worker: only looks for risks."""
    prompt = f"In one sentence, name the single biggest risk of: {topic}"
    return client.chat(prompt=prompt, temperature=0.3, max_tokens=60).text.strip()


def orchestrator(client: LLMClient, task: str) -> dict:
    """
    The lead agent. Its only job is breaking the task into subtasks and
    deciding which worker handles each one, then combining results.
    It never does the research or risk analysis itself.
    """
    plan_prompt = (
        f"Task: {task}\n\n"
        f"Break this into exactly two subtasks: one for a research "
        f"worker, one for a risk-analysis worker. Reply in this format:\n"
        f"RESEARCH: <subtask for the research worker>\n"
        f"RISK: <subtask for the risk worker>"
    )
    plan = client.chat(prompt=plan_prompt, temperature=0.2, max_tokens=150).text.strip()

    research_subtask = plan.split("RESEARCH:")[1].split("RISK:")[0].strip() if "RESEARCH:" in plan else task
    risk_subtask = plan.split("RISK:")[1].strip() if "RISK:" in plan else task

    research_result = worker_research(client, research_subtask)
    risk_result = worker_risk_check(client, risk_subtask)

    return {
        "plan": plan,
        "research_subtask": research_subtask,
        "risk_subtask": risk_subtask,
        "research_result": research_result,
        "risk_result": risk_result,
    }


def main() -> None:
    client = LLMClient()
    task = "whether a small team should self-host an open-weight model instead of using an API"

    print(f"Task given to the orchestrator: {task}\n")
    result = orchestrator(client, task)

    print("Orchestrator's plan:")
    print(result["plan"])
    print()
    print(f"Delegated to research worker: {result['research_subtask']}")
    print(f"Research worker's result: {result['research_result']}")
    print()
    print(f"Delegated to risk worker: {result['risk_subtask']}")
    print(f"Risk worker's result: {result['risk_result']}")

    print(
        "\nThe orchestrator never did the research or the risk analysis "
        "itself. Its entire job was deciding how to split the task and "
        "which specialized worker should handle each piece. This is the "
        "structural difference from a single ReAct agent handling "
        "everything in one loop: each worker here only ever sees its own "
        "narrow subtask, never the full context, which keeps each one's "
        "prompt focused and its failure modes easier to isolate."
    )
    print(
        "\nLangGraph is confirmed as the dominant 2026 framework "
        "implementing this exact pattern as an explicit graph: "
        "add_node for each worker, add_conditional_edges for the "
        "orchestrator's routing decision. What's built here by hand is "
        "the same coordination logic a framework would wrap in more "
        "structure, useful once a system has enough workers and routing "
        "logic that hand-rolled coordination stops scaling."
    )


if __name__ == "__main__":
    main()
