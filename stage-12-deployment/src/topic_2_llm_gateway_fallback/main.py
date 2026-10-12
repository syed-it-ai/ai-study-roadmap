"""
Confirmed as a current, real pattern: an LLM gateway (LiteLLM is the
specific tool named in current sources) sits between an application
and its backend providers, so traffic can be redirected between
OpenAI, Anthropic, a local vLLM instance, or a fallback provider
without touching any application code. This builds the actual routing
and fallback logic directly, with injectable fake providers so the
failure and recovery paths are both genuinely exercised, not just
described.
"""

import time


class ProviderError(Exception):
    pass


class LLMGateway:
    """
    The core of what a gateway like LiteLLM actually does: try
    providers in priority order, catch failures, fall back to the next
    one, and track which provider actually served each request. Real
    gateways add cost tracking and load balancing on top of this same
    core loop.
    """

    def __init__(self, providers: list):
        """providers: list of (name, callable) tuples, tried in order."""
        self.providers = providers
        self.call_log = []

    def chat(self, prompt: str, max_retries_per_provider: int = 1) -> dict:
        last_error = None
        for name, provider_fn in self.providers:
            for attempt in range(max_retries_per_provider):
                try:
                    result = provider_fn(prompt)
                    self.call_log.append({"provider": name, "attempt": attempt + 1, "status": "success"})
                    return {"text": result, "served_by": name, "attempts_before_success": len(self.call_log)}
                except ProviderError as e:
                    self.call_log.append({"provider": name, "attempt": attempt + 1, "status": f"failed: {e}"})
                    last_error = e
        raise ProviderError(f"All providers exhausted. Last error: {last_error}")


# Fake providers standing in for real API calls, with controllable
# failure behavior so the fallback path is genuinely exercised in this
# demo, not just claimed to work.

def make_always_fails_provider(name: str):
    def provider(prompt: str):
        raise ProviderError(f"{name} is down (simulated)")
    return provider


def make_working_provider(name: str, response_prefix: str):
    def provider(prompt: str):
        return f"[{response_prefix}] response to: {prompt}"
    return provider


def main() -> None:
    print("=== Scenario 1: primary provider works, no fallback needed ===\n")
    gateway1 = LLMGateway([
        ("groq-primary", make_working_provider("groq-primary", "Groq")),
        ("openrouter-backup", make_working_provider("openrouter-backup", "OpenRouter")),
    ])
    result1 = gateway1.chat("What's our refund policy?")
    print(f"Served by: {result1['served_by']}")
    print(f"Response: {result1['text']}")
    for entry in gateway1.call_log:
        print(f"  {entry}")

    print("\n=== Scenario 2: primary is down, gateway falls back automatically ===\n")
    gateway2 = LLMGateway([
        ("groq-primary", make_always_fails_provider("groq-primary")),
        ("openrouter-backup", make_working_provider("openrouter-backup", "OpenRouter")),
    ])
    result2 = gateway2.chat("What's our refund policy?")
    print(f"Served by: {result2['served_by']}")
    print(f"Response: {result2['text']}")
    for entry in gateway2.call_log:
        print(f"  {entry}")

    print("\n=== Scenario 3: every provider is down, the gateway correctly gives up ===\n")
    gateway3 = LLMGateway([
        ("groq-primary", make_always_fails_provider("groq-primary")),
        ("openrouter-backup", make_always_fails_provider("openrouter-backup")),
    ])
    try:
        gateway3.chat("What's our refund policy?")
    except ProviderError as e:
        print(f"Correctly raised after exhausting all providers: {e}")
    for entry in gateway3.call_log:
        print(f"  {entry}")

    print(
        "\nThe application code calling gateway.chat() never changes across "
        "all three scenarios. It has no idea whether Groq or OpenRouter "
        "actually served the request, or that a provider failed at all. "
        "That's the actual value a gateway provides: redirecting traffic "
        "between providers without touching the code that calls it, "
        "confirmed directly as how current tools like LiteLLM operate."
    )


if __name__ == "__main__":
    main()
