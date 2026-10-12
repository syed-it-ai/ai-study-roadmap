"""
Topics 2, 3, and 4 are all fully offline, pure logic, no API call.
Topic 1 calls a live model to demonstrate its point and is meant to
be run and read, same honest limitation as every stage so far.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_2_mcp_stateless_protocol.main import old_stateful_handshake, new_stateless_request
from src.topic_3_mcp_deprecated_primitives.main import (
    old_sampling_pattern, new_explicit_handle_pattern, old_roots_pattern, new_explicit_context_pattern,
)
from src.topic_4_tool_permission_scoping.main import ToolPermissionGate, FULL_REGISTRY


# --- topic 2: MCP protocol shapes ---

def test_old_handshake_requires_multiple_messages():
    messages = old_stateful_handshake()
    assert len(messages) >= 3  # initialize, initialized, then the real request


def test_old_handshake_establishes_a_session_id():
    messages = old_stateful_handshake()
    session_messages = [m for m in messages if "header_set" in m]
    assert len(session_messages) == 1
    assert "Mcp-Session-Id" in session_messages[0]["header_set"]


def test_new_stateless_request_is_a_single_message():
    messages = new_stateless_request()
    assert len(messages) == 1


def test_new_stateless_request_carries_its_own_protocol_version():
    messages = new_stateless_request()
    assert "MCP-Protocol-Version" in messages[0]["header_required"]


# --- topic 3: deprecated primitives ---

def test_old_sampling_requires_a_back_channel():
    pattern = old_sampling_pattern()
    assert "server_to_client" in str(pattern) or "server_to_client" in list(pattern.keys())[0]


def test_new_handle_pattern_is_request_response_only():
    pattern = new_explicit_handle_pattern("test task")
    assert "request" in pattern and "response" in pattern
    assert "test task" in pattern["response"]["result"]


def test_new_context_pattern_passes_directory_explicitly():
    pattern = new_explicit_context_pattern("/some/path")
    assert pattern["params"]["arguments"]["working_directory"] == "/some/path"


# --- topic 4: tool permission scoping ---

def test_read_only_scope_cannot_see_refund_tool():
    gate = ToolPermissionGate(FULL_REGISTRY)
    tools = gate.available_tools("read_only_support")
    assert "issue_refund" not in tools


def test_support_with_refunds_scope_can_see_refund_tool():
    gate = ToolPermissionGate(FULL_REGISTRY)
    tools = gate.available_tools("support_with_refunds")
    assert "issue_refund" in tools


def test_dangerous_tool_blocked_for_non_admin_scope():
    gate = ToolPermissionGate(FULL_REGISTRY)
    result = gate.attempt_call("read_only_support", "delete_customer_account", {"account_id": "x"})
    assert result["allowed"] is False


def test_dangerous_tool_allowed_for_admin_scope():
    gate = ToolPermissionGate(FULL_REGISTRY)
    result = gate.attempt_call("admin", "delete_customer_account", {"account_id": "x"})
    assert result["allowed"] is True


def test_scoping_is_independent_of_registry_contents():
    # Even though the registry contains the dangerous tool, scope alone
    # determines reachability, not anything about the tool itself.
    gate = ToolPermissionGate(FULL_REGISTRY)
    assert "delete_customer_account" in FULL_REGISTRY
    assert "delete_customer_account" not in gate.available_tools("read_only_support")
