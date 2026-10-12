"""
Every topic in Stage 13 is pure logic with no API call, consistent
with Stages 2, 10, 11, and 12, since skill discovery, diff generation,
command sandboxing, and tool selection are all things verifiable
without a live model call.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_1_skill_loader.main import parse_skill_file, discover_skills, match_skill_for_task, SIMULATED_SKILLS
from src.topic_2_diff_approval_harness.main import FileEditHarness
from src.topic_3_command_sandboxing.main import CommandSandbox
from src.topic_4_choosing_a_coding_agent.main import recommend_coding_agent


# --- topic 1: skill loader ---

def test_parse_skill_file_extracts_frontmatter():
    content = "---\nname: test\nwhen_to_use: testing things\n---\nBody text here."
    parsed = parse_skill_file(content)
    assert parsed["name"] == "test"
    assert parsed["when_to_use"] == "testing things"
    assert parsed["body"] == "Body text here."


def test_discover_skills_parses_every_file():
    skills = discover_skills(SIMULATED_SKILLS)
    assert len(skills) == len(SIMULATED_SKILLS)


def test_project_priority_wins_over_user_priority_on_conflict():
    skills = discover_skills(SIMULATED_SKILLS)
    matched = match_skill_for_task("create a PDF invoice", skills)
    assert matched["priority"] == "project"


def test_no_match_returns_none():
    skills = discover_skills(SIMULATED_SKILLS)
    matched = match_skill_for_task("deploy the application to production", skills)
    assert matched is None


# --- topic 2: diff approval harness ---

def test_propose_change_creates_pending_change_not_applied():
    harness = FileEditHarness()
    harness.propose_change("f.py", "a\n", "b\n")
    assert harness.pending_change is not None
    assert len(harness.applied_changes) == 0


def test_rejecting_clears_pending_without_applying():
    harness = FileEditHarness()
    harness.propose_change("f.py", "a\n", "b\n")
    harness.reject()
    assert harness.pending_change is None
    assert len(harness.applied_changes) == 0


def test_approving_moves_change_to_applied():
    harness = FileEditHarness()
    harness.propose_change("f.py", "a\n", "b\n")
    harness.approve_and_apply()
    assert len(harness.applied_changes) == 1
    assert harness.pending_change is None


def test_approving_with_no_pending_change_raises():
    harness = FileEditHarness()
    try:
        harness.approve_and_apply()
        assert False, "should have raised ValueError"
    except ValueError:
        pass


# --- topic 3: command sandboxing ---

def test_allowed_command_in_allowed_path_passes():
    sandbox = CommandSandbox({"ls"}, "/home/user/project")
    result = sandbox.check("ls /home/user/project/src")
    assert result["allowed"] is True


def test_disallowed_command_is_blocked():
    sandbox = CommandSandbox({"ls"}, "/home/user/project")
    result = sandbox.check("rm -rf /home/user/project")
    assert result["allowed"] is False


def test_path_traversal_is_blocked_even_with_allowed_command():
    sandbox = CommandSandbox({"python3"}, "/home/user/project")
    result = sandbox.check("python3 /home/user/project/../../etc/shadow")
    assert result["allowed"] is False
    assert any(".." in r for r in result["reasons"])


def test_allowed_command_outside_allowed_path_is_blocked():
    sandbox = CommandSandbox({"cat"}, "/home/user/project")
    result = sandbox.check("cat /etc/passwd")
    assert result["allowed"] is False


# --- topic 4: choosing a coding agent ---

def test_sandboxing_need_routes_to_gemini_cli():
    result = recommend_coding_agent(False, True, False)
    assert "Gemini CLI" in result


def test_automation_need_routes_to_claude_code_or_codex():
    result = recommend_coding_agent(True, False, False)
    assert "Claude Code" in result or "Codex CLI" in result


def test_multi_tool_skill_use_is_treated_as_non_factor():
    result = recommend_coding_agent(False, False, True)
    assert "SKILL.md works identically" in result
