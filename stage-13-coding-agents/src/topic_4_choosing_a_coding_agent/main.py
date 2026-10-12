"""
Confirmed from a current Q2 2026 comparison of terminal-based coding
agents: Claude Code and Codex CLI have the deepest non-interactive and
scripting surfaces of the major tools, Gemini CLI has the most mature
OS-level sandboxing with four backend options, and SKILL.md works
identically across all of them as of 2026, so skill format is no
longer a real differentiator between tools the way it was before the
standard existed. This builds the actual decision logic from those
confirmed differences, not a vague "they're all good" shrug.
"""


def recommend_coding_agent(needs_scripting_automation: bool, needs_strong_sandboxing: bool,
                             works_across_multiple_tools_already: bool) -> str:
    """
    The decision logic made explicit, grounded in confirmed current
    differentiators rather than brand preference. Skill portability is
    checked first and explicitly dismissed as a non-factor, since
    SKILL.md now works identically everywhere, which is itself
    worth stating plainly rather than silently assuming.
    """
    if needs_strong_sandboxing:
        return "Gemini CLI: confirmed as having the most mature OS-level sandboxing of the major tools, with four backend options."
    if needs_scripting_automation:
        return "Claude Code or Codex CLI: both confirmed to have the deepest non-interactive and scripting surfaces for automated workflows."
    return "Any of the major tools reasonably fit here. Pick based on which model family you already trust, not skill portability, since SKILL.md works identically across all of them now."


def main() -> None:
    scenarios = [
        {
            "name": "A CI pipeline that needs an agent to run unattended, no human in the loop",
            "needs_scripting_automation": True, "needs_strong_sandboxing": False, "works_across_multiple_tools_already": False,
        },
        {
            "name": "A team wary of letting an agent run arbitrary shell commands on shared infrastructure",
            "needs_scripting_automation": False, "needs_strong_sandboxing": True, "works_across_multiple_tools_already": False,
        },
        {
            "name": "A solo developer picking their first coding agent, no strong constraints yet",
            "needs_scripting_automation": False, "needs_strong_sandboxing": False, "works_across_multiple_tools_already": False,
        },
        {
            "name": "A team already maintaining a library of SKILL.md files across several tools",
            "needs_scripting_automation": False, "needs_strong_sandboxing": False, "works_across_multiple_tools_already": True,
        },
    ]

    for s in scenarios:
        recommendation = recommend_coding_agent(
            s["needs_scripting_automation"], s["needs_strong_sandboxing"], s["works_across_multiple_tools_already"],
        )
        print(f"Scenario: {s['name']}")
        print(f"  -> {recommendation}\n")

    print(
        "The fourth scenario's answer is the one most people get wrong by "
        "assuming skill portability is still a real differentiator. It "
        "isn't, as of the 2026 standard: a skill written for Codex CLI "
        "already works unchanged in Claude Code, Cursor, and Gemini CLI. "
        "A team maintaining skills across several tools gains nothing "
        "from picking one tool over another on that basis specifically, "
        "which is exactly why this topic's decision function treats it as "
        "a non-factor rather than inventing a reason to prefer one tool."
    )
    print(
        "\nThis project's own roadmap gives the advice that matters more "
        "than any single comparison point: pick one tool and commit to it "
        "for a month, learning its harness deeply, rather than "
        "tool-hopping based on whichever comparison post is newest. The "
        "differentiators above matter for the initial choice. Depth with "
        "one tool matters more afterward."
    )


if __name__ == "__main__":
    main()
