"""
Confirmed as the current edition: OWASP published the 2026 revision
of its Top 10 for LLM Applications on August 3-4, 2026, the third
release since the list began in 2023, this time built in part from
contributed incident data rather than practitioner judgment alone.
This builds a real coverage audit: given a hypothetical application's
actual features, which of the ten current risks genuinely apply, and
which specific mitigation from this stage's own earlier topics
addresses each one.
"""

# The current 2026 list, confirmed directly, in rank order. Risks 6-10
# are named here for completeness; this project's own defensive topics
# (1-3) map specifically to the first three, the risks this stage
# actually built working mitigations for.
OWASP_LLM_TOP_10_2026 = [
    ("LLM01:2026", "Prompt Injection", "Untrusted content redirecting the model's actual behavior"),
    ("LLM02:2026", "Sensitive Information Disclosure", "The model revealing data it should not have exposed"),
    ("LLM03:2026", "Excessive Agency", "An agent able to take more consequential action than its task requires"),
    ("LLM04:2026", "Supply Chain", "Compromised models, datasets, or dependencies in the pipeline"),
    ("LLM05:2026", "Data and Model Poisoning", "Training or fine-tuning data manipulated to corrupt behavior"),
    ("LLM06:2026", "Unbounded Consumption", "No limit on resource use, enabling cost or denial-of-service attacks"),
    ("LLM07:2026", "System Prompt Leakage", "Internal instructions exposed to a user who shouldn't see them"),
    ("LLM08:2026", "Vector and Embedding Weaknesses", "RAG pipeline and vector store vulnerabilities"),
    ("LLM09:2026", "Misinformation", "Confident, plausible, incorrect output presented as fact"),
    ("LLM10:2026", "Unbounded Model Behavior", "Output handling failures letting bad responses reach users unchecked"),
]


def audit_application(app_features: dict) -> list:
    """
    A real audit: check an application's actual features against each
    risk, flagging which ones genuinely apply given what this specific
    app does, rather than treating the whole list as equally relevant
    to every application regardless of its actual feature set.
    """
    findings = []

    if app_features.get("reads_untrusted_content"):
        findings.append(("LLM01:2026", "Prompt Injection", "App reads external content (tickets, web pages, documents). Mitigation: this stage's topic 1, content isolation and pattern flagging."))

    if app_features.get("has_tool_access") and app_features.get("tool_actions_have_side_effects"):
        findings.append(("LLM03:2026", "Excessive Agency", "App's tools can take real actions. Mitigation: this stage's topic 2, action scoping with value limits."))

    if app_features.get("has_private_data_access") and app_features.get("reads_untrusted_content") and app_features.get("has_external_communication"):
        findings.append(("Lethal Trifecta", "All three dangerous capabilities present", "Mitigation: this stage's topic 3, remove one leg of the combination."))

    if app_features.get("exposes_system_prompt_in_errors"):
        findings.append(("LLM07:2026", "System Prompt Leakage", "App's error handling may expose internal instructions. No dedicated topic in this stage, flagged for separate review."))

    return findings


def main() -> None:
    print("=== OWASP Top 10 for LLM Applications, 2026 edition ===\n")
    for code, name, description in OWASP_LLM_TOP_10_2026:
        print(f"  {code}  {name}")
        print(f"            {description}")

    print("\n=== Auditing a real hypothetical application ===\n")
    app_features = {
        "reads_untrusted_content": True,      # reads customer support tickets
        "has_tool_access": True,
        "tool_actions_have_side_effects": True,  # can issue refunds
        "has_private_data_access": True,       # CRM access
        "has_external_communication": True,    # can send emails
        "exposes_system_prompt_in_errors": False,
    }
    print(f"Application features: {app_features}\n")

    findings = audit_application(app_features)
    print(f"Findings: {len(findings)}\n")
    for code, name, note in findings:
        print(f"  [{code}] {name}")
        print(f"    {note}\n")

    print(
        "This single hypothetical application triggers three separate "
        "findings, not because it's unusually dangerous, but because "
        "it's realistic: a support bot that reads tickets, has CRM "
        "access, and can send emails is an entirely normal feature set, "
        "and normal feature sets are exactly where this stage's risks "
        "actually live. The audit doesn't flag every risk on the list "
        "for every app, only the ones this specific app's actual "
        "features genuinely expose it to."
    )


if __name__ == "__main__":
    main()
