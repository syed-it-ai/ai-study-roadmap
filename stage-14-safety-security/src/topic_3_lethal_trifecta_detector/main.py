"""
The lethal trifecta, named by Simon Willison and confirmed as directly
tied to OWASP's current LLM Top 10 coverage: an agent becomes
genuinely dangerous specifically when it has all three of these
capabilities at once, not any one or two alone: access to private
data, exposure to untrusted content, and a way to communicate
externally. Confirmed directly: filtering content for injection
attempts, this stage's topic 1, is not a reliable defense on its own.
The lethal trifecta framing is about removing the combination itself,
checking an agent's configuration for this pattern before it ever runs.
"""


class AgentCapabilityProfile:
    """
    Describes what one agent configuration can actually do, as three
    independent boolean capabilities. The lethal trifecta exists
    specifically in the intersection of all three, not in any single
    one, which is exactly why checking them independently and then
    combining the result catches a risk that inspecting any one
    capability alone would miss.
    """

    def __init__(self, name: str, has_private_data_access: bool,
                 exposed_to_untrusted_content: bool, has_external_communication: bool):
        self.name = name
        self.has_private_data_access = has_private_data_access
        self.exposed_to_untrusted_content = exposed_to_untrusted_content
        self.has_external_communication = has_external_communication

    def check_lethal_trifecta(self) -> dict:
        capabilities_present = [
            ("private data access", self.has_private_data_access),
            ("untrusted content exposure", self.exposed_to_untrusted_content),
            ("external communication", self.has_external_communication),
        ]
        present_count = sum(1 for _, present in capabilities_present if present)
        is_lethal_trifecta = present_count == 3
        missing = [name for name, present in capabilities_present if not present]
        return {
            "agent": self.name,
            "capabilities_present": present_count,
            "is_lethal_trifecta": is_lethal_trifecta,
            "missing_capability": missing[0] if len(missing) == 1 else (missing if missing else None),
        }


def main() -> None:
    agents = [
        AgentCapabilityProfile(
            "Internal knowledge base search bot",
            has_private_data_access=True, exposed_to_untrusted_content=False, has_external_communication=False,
        ),
        AgentCapabilityProfile(
            "Email-drafting assistant with calendar access",
            has_private_data_access=True, exposed_to_untrusted_content=True, has_external_communication=False,
        ),
        AgentCapabilityProfile(
            "Customer support agent reading tickets, with send-email tool and CRM access",
            has_private_data_access=True, exposed_to_untrusted_content=True, has_external_communication=True,
        ),
        AgentCapabilityProfile(
            "Public FAQ bot with no account access",
            has_private_data_access=False, exposed_to_untrusted_content=True, has_external_communication=True,
        ),
    ]

    for agent in agents:
        result = agent.check_lethal_trifecta()
        status = "LETHAL TRIFECTA" if result["is_lethal_trifecta"] else "safe combination"
        print(f"{agent.name}")
        print(f"  Capabilities present: {result['capabilities_present']}/3, status: {status}")
        if not result["is_lethal_trifecta"] and result["missing_capability"]:
            print(f"  Missing: {result['missing_capability']}")
        print()

    print(
        "Only the third agent, the customer support bot, has all three "
        "capabilities at once, and it's the only one flagged. The "
        "email-drafting assistant has two of three, private data and "
        "untrusted content, genuinely risky on its own, but without "
        "external communication an injection inside a calendar invite "
        "has nowhere to actually send stolen data."
    )
    print(
        "\nThe fix the lethal trifecta framing actually recommends, "
        "confirmed directly: remove one leg of the triangle rather than "
        "trying to perfectly filter the untrusted content. The support "
        "bot could keep its data access and its untrusted-content "
        "exposure if its external communication were scoped down, "
        "replies reviewed before sending, rather than sent autonomously, "
        "which breaks the combination without removing the bot's "
        "actual job."
    )


if __name__ == "__main__":
    main()
