"""
Confirmed across multiple independent migration guides for this build:
the 2026-07-28 spec deprecates three primitives under SEP-2577, each
with a 12-month removal window, not an immediate break. Deprecated
servers still work today. New implementations should not adopt them.

Roots, Sampling, and Logging share a root cause: all three required
the server to send a request back to the client mid-call, which a
stateless protocol has no standing channel for. The replacement
pattern, used across all three, is the same idea: stop relying on an
implicit back-channel, pass what's needed explicitly instead.
"""


def old_sampling_pattern() -> dict:
    """Before: the server asks the client to run an LLM call on its
    behalf, mid-request. This requires a back-channel the stateless
    protocol doesn't have standing infrastructure for."""
    return {
        "step_1_server_to_client": {
            "method": "sampling/createMessage",
            "note": "Server pauses its own response, asks the client to run a completion.",
        },
        "step_2_client_to_server": {
            "note": "Client runs the LLM call, sends the result back before the server can finish.",
        },
        "problem": "Requires the server to hold the connection open waiting for a reply it didn't control.",
    }


def new_explicit_handle_pattern(task_description: str) -> dict:
    """After: the server does its own LLM call directly, using its own
    API key, and returns a result immediately. No mid-call back-channel
    needed at all."""
    # In a real server this would be a direct call to an LLM provider,
    # the same kind of call this project's own LLMClient makes.
    simulated_result = f"[Server's own LLM call result for: {task_description}]"
    return {
        "request": {"method": "tools/call", "params": {"task": task_description}},
        "response": {"result": simulated_result},
        "note": "One request, one response. The server made its own LLM call directly, no back-channel needed.",
    }


def old_roots_pattern() -> dict:
    """Before: the client tells the server which filesystem directories
    it's allowed to touch, as a standing, session-scoped declaration."""
    return {
        "method": "roots/list",
        "response": {"roots": [{"uri": "file:///home/user/project"}]},
        "note": "Declared once per session. The server remembers it for every later call.",
    }


def new_explicit_context_pattern(working_directory: str) -> dict:
    """After: pass the working context explicitly, as a normal tool
    argument, on the request that actually needs it."""
    return {
        "method": "tools/call",
        "params": {"name": "read_file", "arguments": {"path": "config.json", "working_directory": working_directory}},
        "note": "The working directory is a plain argument on this one request, not a standing session fact.",
    }


def main() -> None:
    print("=== Sampling: deprecated, replaced by a direct server-side LLM call ===\n")
    print("Old pattern:", old_sampling_pattern())
    print()
    print("New pattern:", new_explicit_handle_pattern("summarize this document"))

    print("\n=== Roots: deprecated, replaced by explicit context on each call ===\n")
    print("Old pattern:", old_roots_pattern())
    print()
    print("New pattern:", new_explicit_context_pattern("/home/user/project"))

    print(
        "\nThe pattern repeats across both: the old version relied on the "
        "server remembering something the client declared earlier in the "
        "session. The new version passes that same information explicitly, "
        "on the request that actually needs it, which works identically "
        "whether or not any session exists at all."
    )
    print(
        "\nLogging follows the same root cause from a different angle: "
        "logging/setLevel and the log-forwarding methods assumed a "
        "standing channel back to the client. The replacement is simpler "
        "than a protocol feature: write to stderr, or use OpenTelemetry, "
        "infrastructure that already exists outside the protocol."
    )
    print(
        "\nAll three are deprecated, not removed. A server using them "
        "today keeps working. The twelve-month window exists specifically "
        "so migration isn't forced overnight."
    )


if __name__ == "__main__":
    main()
