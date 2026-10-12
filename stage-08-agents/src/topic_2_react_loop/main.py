"""
ReAct (Reason + Act), from the 2022 paper that named it, is confirmed
as the default single-agent pattern as of 2026, the thing most people
mean when they say "agent" at all. The loop: the model reasons about
the current situation, picks an action, observes the result, and
reasons again, until it has enough to answer.

This implements the loop directly, no framework, so the actual control
flow is visible: a plain while loop with a step budget, not a black box.
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

# A tiny toy "world" the agent can act on. Real tools would call real
# APIs; these are simple functions so the loop itself stays visible.
def tool_check_inventory(item: str) -> str:
    inventory = {"widget": 42, "gadget": 0, "gizmo": 7}
    return f"{item}: {inventory.get(item, 'unknown item')} units in stock"


def tool_check_price(item: str) -> str:
    prices = {"widget": 9.99, "gadget": 24.99, "gizmo": 14.99}
    return f"{item}: ${prices.get(item, 'unknown')}"


TOOLS = {"check_inventory": tool_check_inventory, "check_price": tool_check_price}

SYSTEM_INSTRUCTIONS = """You are solving a task using a reason-act loop. At each step, respond in exactly this format:

Thought: <your reasoning about what to do next>
Action: <tool_name>(<argument>)

Available tools: check_inventory(item), check_price(item)

Once you have enough information to answer, respond instead with:
Thought: <final reasoning>
Final Answer: <your answer to the user>

One step at a time. Wait for the Observation before continuing."""


def parse_action(text: str):
    match = re.search(r"Action:\s*(\w+)\((.*?)\)", text)
    if match:
        return match.group(1), match.group(2).strip("'\" ")
    return None, None


def run_react_loop(client: LLMClient, task: str, max_steps: int = 5) -> str:
    history = f"{SYSTEM_INSTRUCTIONS}\n\nTask: {task}\n"

    for step in range(1, max_steps + 1):
        response = client.chat(prompt=history, temperature=0.0, max_tokens=150)
        step_text = response.text.strip()
        print(f"--- Step {step} ---")
        print(step_text)

        if "Final Answer:" in step_text:
            return step_text.split("Final Answer:")[-1].strip()

        tool_name, arg = parse_action(step_text)
        if tool_name and tool_name in TOOLS:
            observation = TOOLS[tool_name](arg)
        elif tool_name:
            observation = f"Error: unknown tool '{tool_name}'"
        else:
            observation = "Error: no valid Action found in that response."

        print(f"Observation: {observation}\n")
        history += f"{step_text}\nObservation: {observation}\n"

    return "Reached the step budget without a final answer. Stopping rather than looping indefinitely."


def main() -> None:
    client = LLMClient()
    task = "A customer wants to know if we can fulfill an order of 10 gadgets right now. Can we?"

    print(f"Task: {task}\n")
    answer = run_react_loop(client, task)
    print(f"\nFinal answer: {answer}")

    print(
        "\nThe step budget (max_steps=5) is not decoration. Without it, a "
        "model that gets stuck repeating the same action, or never quite "
        "reaching a confident answer, loops indefinitely. Stage 10's agent "
        "cost control topic in this project's main roadmap covers exactly "
        "this failure mode: a real documented incident involved an agent "
        "looping for 11 days before anyone noticed."
    )


if __name__ == "__main__":
    main()
