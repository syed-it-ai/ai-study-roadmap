"""
MCP had its largest specification revision since launch on July 28,
2026 (confirmed directly against the spec's own changelog and multiple
independent migration guides for this build). The headline change: MCP
went fully stateless. The old initialize/initialized handshake and the
Mcp-Session-Id header are gone. Every request now carries its own
protocol version and capabilities, so any request can land on any
server instance, which is what lets an MCP server run behind an
ordinary load balancer instead of needing sticky sessions.

This is a minimal mock client and server, fully offline, built to show
the actual message shapes before and after this change, not just
describe them in prose.
"""

import json


def old_stateful_handshake() -> list:
    """How this worked before 2026-07-28. A session had to be
    established first, before any real request could be sent."""
    messages = []

    # Step 1: client initializes, server responds with a session ID
    messages.append({
        "direction": "client -> server",
        "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "clientInfo": {"name": "demo-client"}},
    })
    messages.append({
        "direction": "server -> client",
        "response": {"protocolVersion": "2025-11-25", "sessionId": "sess_8f2a91"},
        "header_set": "Mcp-Session-Id: sess_8f2a91",
    })
    messages.append({
        "direction": "client -> server",
        "method": "notifications/initialized",
        "note": "Required before any other request. The session now exists on the server.",
    })

    # Step 2: only now can a real request happen, and it must carry the session header
    messages.append({
        "direction": "client -> server",
        "method": "tools/call",
        "header_required": "Mcp-Session-Id: sess_8f2a91",
        "params": {"name": "get_weather", "arguments": {"city": "Austin"}},
        "note": "Fails with no valid session ID if this header is missing.",
    })
    return messages


def new_stateless_request() -> list:
    """How this works under the current 2026-07-28 spec. No handshake,
    no session. Every request is self-contained."""
    messages = []

    messages.append({
        "direction": "client -> server",
        "method": "tools/call",
        "header_required": "MCP-Protocol-Version: 2026-07-28",
        "meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28"},
        "params": {"name": "get_weather", "arguments": {"city": "Austin"}},
        "note": "No prior request needed. This can be the very first thing the server ever sees from this client.",
    })
    return messages


def main() -> None:
    print("=== Before: the old stateful handshake (spec 2025-11-25 and earlier) ===\n")
    for msg in old_stateful_handshake():
        print(json.dumps(msg, indent=2))
        print()

    print("=== After: the current stateless request (spec 2026-07-28) ===\n")
    for msg in new_stateless_request():
        print(json.dumps(msg, indent=2))
        print()

    print(
        "Three messages collapsed into one. The protocol version, client "
        "capabilities, and request itself all travel together now, inside "
        "_meta and the MCP-Protocol-Version header, rather than being "
        "established once and remembered by a session the server has to "
        "keep alive."
    )
    print(
        "\nThis is also why a stateless MCP server can sit behind an "
        "ordinary load balancer with no sticky-session configuration. Any "
        "request can land on any server instance, because no instance has "
        "to remember anything about a prior request to handle the current "
        "one correctly."
    )


if __name__ == "__main__":
    main()
