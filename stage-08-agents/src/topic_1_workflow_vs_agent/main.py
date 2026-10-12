"""
A workflow runs a fixed sequence you hard-coded. An agent decides its
own next step at runtime from what it observed. Confirmed as the
current 2026 framing across multiple independent sources, unchanged
from when this distinction was first named: the difference is not
about intelligence, it's about who decides the control flow, the
programmer in advance or the model at runtime.

This runs the same order-lookup task as both a workflow and an agent,
on an input the workflow's fixed sequence was never built to handle.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
from src.shared.llm_client import LLMClient

load_dotenv()

ORDERS = {
    "ORD-1001": {"status": "shipped", "tracking": "1Z999AA1"},
    "ORD-1002": {"status": "processing"},
}


def workflow_lookup_order(order_id: str) -> str:
    """
    A fixed sequence, three steps, always run in this exact order,
    regardless of what's actually found at each step. This is a
    workflow: the programmer decided the control flow in advance.
    """
    # Step 1: look up the order
    order = ORDERS.get(order_id)
    if order is None:
        return "Step 1 failed: order not found. (The fixed sequence has no next step for this case.)"
    # Step 2: always check tracking, even if the order was never shipped
    tracking = order.get("tracking", "NO TRACKING AVAILABLE")
    # Step 3: always format the same response shape
    return f"Order {order_id}: {order['status']}, tracking: {tracking}"


def agent_lookup_order(client: LLMClient, order_id: str) -> str:
    """
    The same task, but the model decides what to do next based on what
    it observes at each step, rather than following a fixed sequence.
    """
    order = ORDERS.get(order_id)
    observation = f"Order lookup result: {order}" if order else "Order lookup result: not found in system"

    prompt = (
        f"You are helping a customer with order {order_id}. "
        f"{observation}\n\n"
        f"Decide what to tell the customer. If the order wasn't found, "
        f"suggest what they should check next, don't just report an error. "
        f"If it was found but has no tracking number, explain why rather "
        f"than displaying a placeholder. Keep it to two sentences."
    )
    response = client.chat(prompt=prompt, temperature=0.3, max_tokens=100)
    return response.text.strip()


def main() -> None:
    client = LLMClient()

    test_cases = ["ORD-1001", "ORD-1002", "ORD-9999"]

    for order_id in test_cases:
        print(f"--- Order {order_id} ---")
        print(f"Workflow (fixed steps): {workflow_lookup_order(order_id)}")
        agent_response = agent_lookup_order(client, order_id)
        print(f"Agent (decides at runtime): {agent_response}")
        print()

    print(
        "Watch ORD-9999 and ORD-1002 specifically. The workflow's fixed "
        "sequence has no step written for 'order not found gracefully' or "
        "'shipped but genuinely has no tracking yet', so it returns "
        "whatever its rigid steps produce, a placeholder or a bare "
        "failure message. The agent observes the same facts and decides "
        "a more useful response for each specific case, because nothing "
        "forces it through the same three steps regardless of what it finds."
    )
    print(
        "\nThis is not the agent being smarter in general. It's the "
        "difference between control flow fixed in advance and control "
        "flow decided at runtime from observation. Most production "
        "systems should default to the workflow, and only reach for agent "
        "autonomy where the input space is genuinely too varied to "
        "enumerate in advance."
    )


if __name__ == "__main__":
    main()
