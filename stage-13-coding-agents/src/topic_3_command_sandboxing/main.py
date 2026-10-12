"""
Confirmed as a real current differentiator between coding agent tools:
Gemini CLI has the most mature OS-level sandboxing of the major
terminal-based agents, with multiple backend options, while every tool
in this space implements some version of the same underlying idea,
restricting which commands and paths an agent can actually touch,
distinct from tool-schema design covered in this project's Stage 7.
This builds that restriction layer directly: a real allowlist and path
boundary a command either passes or doesn't.
"""

import re


class CommandSandbox:
    """
    Two independent checks, both have to pass: is this command on the
    allowed list at all, and does it only touch paths inside the
    permitted directory. A command can fail either check independently,
    and both get reported, not just whichever one happened to run first.
    """

    def __init__(self, allowed_commands: set, allowed_path_prefix: str):
        self.allowed_commands = allowed_commands
        self.allowed_path_prefix = allowed_path_prefix

    def check(self, command: str) -> dict:
        parts = command.strip().split()
        if not parts:
            return {"allowed": False, "reasons": ["empty command"]}

        base_command = parts[0]
        reasons = []

        if base_command not in self.allowed_commands:
            reasons.append(f"'{base_command}' is not in the allowed command list {sorted(self.allowed_commands)}")

        paths_in_command = [p for p in parts[1:] if "/" in p or p.startswith(".")]
        for path in paths_in_command:
            resolved = path if path.startswith("/") else f"{self.allowed_path_prefix}/{path}"
            if ".." in path:
                reasons.append(f"path '{path}' contains '..', could escape the sandboxed directory")
            elif not resolved.startswith(self.allowed_path_prefix):
                reasons.append(f"path '{path}' resolves outside the allowed directory {self.allowed_path_prefix}")

        return {"allowed": len(reasons) == 0, "reasons": reasons}


def main() -> None:
    sandbox = CommandSandbox(
        allowed_commands={"ls", "cat", "python3", "pytest", "git"},
        allowed_path_prefix="/home/user/project",
    )

    test_commands = [
        "ls /home/user/project/src",
        "python3 /home/user/project/src/main.py",
        "rm -rf /home/user/project",
        "cat /etc/passwd",
        "python3 /home/user/project/../../etc/shadow",
        "git log",
        "curl http://example.com/exfiltrate",
    ]

    for cmd in test_commands:
        result = sandbox.check(cmd)
        status = "ALLOWED" if result["allowed"] else "BLOCKED"
        print(f"{status:8s} | {cmd}")
        for reason in result["reasons"]:
            print(f"           - {reason}")

    print(
        "\nTwo genuinely different blocks happened above, for two "
        "different reasons. 'rm -rf' and 'curl' get blocked because the "
        "base command itself was never on the allowed list, regardless of "
        "what path it touches. The path-traversal attempt with '..' gets "
        "blocked even though 'python3' is an allowed command, because the "
        "path check is a separate, independent gate the command also has "
        "to pass."
    )
    print(
        "\nThis is the same two-layer idea as Stage 7's tool permission "
        "scoping, applied here to raw shell commands instead of named "
        "tools: which commands exist in a registry is one question, and "
        "which specific invocation is actually safe to run is a separate "
        "one that has to be checked every single time, not assumed from "
        "the command name alone."
    )


if __name__ == "__main__":
    main()
