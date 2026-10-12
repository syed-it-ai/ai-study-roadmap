"""
A tool schema alone does not decide which tools an agent should have
access to in a given context. That's a separate, structural question:
least-privilege scoping, the same principle as giving a person only
the system access their specific job requires, applied to an agent's
tool list instead of a human's account permissions. Fully offline, no
model call needed to demonstrate this.
"""


class ToolPermissionGate:
    """
    Wraps a set of available tools behind a scope check. An agent
    running in a given context only sees the tools that context's
    scope explicitly allows, regardless of what the full tool registry
    contains.
    """

    def __init__(self, full_registry: dict):
        self.full_registry = full_registry
        self.scopes = {
            "read_only_support": {"search_knowledge_base", "look_up_order_status"},
            "support_with_refunds": {"search_knowledge_base", "look_up_order_status", "issue_refund"},
            "admin": set(full_registry.keys()),
        }

    def available_tools(self, scope: str) -> dict:
        allowed_names = self.scopes.get(scope, set())
        return {name: tool for name, tool in self.full_registry.items() if name in allowed_names}

    def attempt_call(self, scope: str, tool_name: str, arguments: dict) -> dict:
        available = self.available_tools(scope)
        if tool_name not in available:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' is not in the '{scope}' scope's allowed list.",
            }
        return {"allowed": True, "result": available[tool_name](**arguments)}


# A full registry of tools, including some genuinely dangerous ones.
# Which of these an agent can actually reach depends entirely on scope,
# never on the registry itself.
FULL_REGISTRY = {
    "search_knowledge_base": lambda query: f"Search results for: {query}",
    "look_up_order_status": lambda order_id: f"Order {order_id}: shipped",
    "issue_refund": lambda order_id, amount: f"Refunded ${amount} for order {order_id}",
    "delete_customer_account": lambda account_id: f"DELETED account {account_id}",
    "modify_billing_settings": lambda account_id, settings: f"Billing updated for {account_id}",
}


def main() -> None:
    gate = ToolPermissionGate(FULL_REGISTRY)

    print("Full tool registry:", list(FULL_REGISTRY.keys()), "\n")

    for scope in ["read_only_support", "support_with_refunds", "admin"]:
        tools = gate.available_tools(scope)
        print(f"Scope '{scope}' can see: {list(tools.keys())}")

    print("\nAttempting the same risky call under three different scopes:\n")
    for scope in ["read_only_support", "support_with_refunds", "admin"]:
        result = gate.attempt_call(scope, "delete_customer_account", {"account_id": "acct_4471"})
        print(f"  Scope '{scope}': {result}")

    print(
        "\nThe tool itself, delete_customer_account, exists in the registry "
        "the entire time. Whether a given agent session can actually reach "
        "it depends only on which scope that session was granted, decided "
        "once, outside the conversation, not something the agent can "
        "negotiate its way into mid-conversation no matter how it's "
        "prompted."
    )
    print(
        "\nThis is the same idea as Stage 8's tool idempotency topic from a "
        "different angle: idempotency limits the damage from a tool being "
        "called twice. Scoping limits which tools a given context can call "
        "at all. A support chatbot scoped to read_only_support structurally "
        "cannot delete an account, regardless of what any single message "
        "in the conversation asks for."
    )


if __name__ == "__main__":
    main()
