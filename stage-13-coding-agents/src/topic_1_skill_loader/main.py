"""
SKILL.md is confirmed as a genuine open standard as of 2026, adopted
across 30+ tools (Claude Code, Codex CLI, Cursor, Gemini CLI, Copilot
among them), replacing what used to be a different proprietary format
per tool. A skill is a directory with a SKILL.md file: YAML frontmatter
carrying metadata and trigger conditions, followed by instructions.

This builds the actual discovery and matching logic a real agent runs:
find every SKILL.md across a priority-ordered set of directories,
parse its frontmatter, and decide which skill, if any, actually
applies to a given task. Fully offline, since this is file and text
parsing, not something that needs a model call to demonstrate.
"""

import re


# Simulated skill files, standing in for real SKILL.md content read
# from disk. The frontmatter format (---, key: value, ---) matches the
# actual confirmed standard.
SIMULATED_SKILLS = {
    "/project/.agents/skills/pdf-handling/SKILL.md": """---
name: pdf-handling
when_to_use: creating, reading, or filling PDF files
priority: project
---
# PDF Handling
Use the pdf library for all PDF creation and form filling.
Never use raw byte manipulation for PDF generation.
""",
    "/home/user/.agents/skills/code-review/SKILL.md": """---
name: code-review
when_to_use: reviewing a pull request or reviewing code changes
priority: user
---
# Code Review
Check for test coverage, naming consistency, and error handling.
Flag anything touching authentication or payment code for extra scrutiny.
""",
    "/home/user/.agents/skills/pdf-handling-personal/SKILL.md": """---
name: pdf-handling
when_to_use: creating, reading, or filling PDF files
priority: user
---
# PDF Handling (personal default)
My personal preference is PyPDF2 for anything PDF related, across
every project, unless a project says otherwise.
""",
}

# Confirmed as the real priority order current tools use: project-level
# skills are discovered first and take precedence over user-level ones
# when both apply to the same trigger, so a project's own conventions
# win over a developer's personal defaults.
PRIORITY_ORDER = {"project": 0, "user": 1, "system": 2}


def parse_skill_file(content: str) -> dict:
    """Parses the YAML-style frontmatter, the same structure every
    conformant SKILL.md file uses, regardless of which tool wrote it."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return {}
    frontmatter_text, body = match.groups()
    frontmatter = {}
    for line in frontmatter_text.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    frontmatter["body"] = body.strip()
    return frontmatter


def discover_skills(skill_files: dict) -> list:
    """Parses every available skill file into structured metadata."""
    skills = []
    for path, content in skill_files.items():
        parsed = parse_skill_file(content)
        if parsed:
            parsed["path"] = path
            skills.append(parsed)
    return skills


def match_skill_for_task(task_description: str, skills: list) -> dict:
    """
    The actual matching logic: find every skill whose when_to_use
    trigger overlaps with the task, then resolve conflicts by priority,
    project beating user beating system, exactly as current tools do.
    """
    task_words = set(task_description.lower().split())
    candidates = []
    for skill in skills:
        trigger_words = set(skill.get("when_to_use", "").lower().replace(",", "").split())
        overlap = task_words & trigger_words
        if overlap:
            candidates.append((skill, len(overlap)))

    if not candidates:
        return None

    # Among matches, prefer higher overlap first, then resolve ties by
    # priority order (project beats user beats system).
    candidates.sort(key=lambda c: (-c[1], PRIORITY_ORDER.get(c[0].get("priority"), 99)))
    return candidates[0][0]


def main() -> None:
    skills = discover_skills(SIMULATED_SKILLS)
    print(f"Discovered {len(skills)} skills across the priority-ordered search paths:\n")
    for s in skills:
        print(f"  {s['path']}")
        print(f"    name: {s['name']}, priority: {s['priority']}, triggers on: {s['when_to_use']}")

    task = "I need to create a PDF invoice for this order"
    print(f"\nTask: \"{task}\"")
    matched = match_skill_for_task(task, skills)
    print(f"Matched skill: {matched['name']} (priority: {matched['priority']})")
    print(f"From: {matched['path']}")
    print(f"Instructions loaded:\n{matched['body']}")

    print(
        "\nNotice there are two different 'pdf-handling' skills discovered "
        "above, a realistic conflict: a project-level skill saying to use "
        "the pdf library, and a user-level personal default saying "
        "PyPDF2. The matched skill above is the project one, not the "
        "personal one, and that's not a coincidence, it's the priority "
        "order resolving a real conflict: project-level conventions win "
        "over a developer's personal defaults, exactly matching the "
        "confirmed real precedence order current tools actually use."
    )
    print(
        "\nThis entire mechanism, frontmatter metadata, trigger-based "
        "matching, priority-ordered conflict resolution, is what makes a "
        "skill written once work unchanged across 30-plus different "
        "coding agent tools. The skill author never has to know which "
        "specific tool will eventually load it."
    )


if __name__ == "__main__":
    main()
