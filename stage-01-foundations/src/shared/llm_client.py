"""
A tiny, provider-agnostic client for talking to a free LLM API.

Built on plain `requests` instead of each provider's own SDK on purpose.
Seeing the actual HTTP request and response teaches you more about what
an LLM API call really is than a wrapped SDK call does. Once this makes
sense, using an SDK later is just a convenience, not a mystery.

Supported providers, all free at the time this was written:
  - groq    : fast, no card required, OpenAI-compatible endpoint
  - gemini  : Google AI Studio, generous free tier on Flash models
  - ollama  : runs fully on your own machine, no network call, no limit

Switch providers by changing one environment variable. Nothing else
in your code needs to know which provider is actually answering.
"""

import os
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """What came back from the model, plus the token accounting."""
    text: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    raw: dict


class LLMClient:
    """
    One object, one provider, one job: send a prompt, get a response.

    Configuration comes from environment variables so your API key
    never ends up hardcoded in a file you might accidentally commit.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "groq")).lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", self._default_model())

        if self.provider != "ollama" and not self.api_key:
            raise ValueError(
                f"No API key found. Set LLM_API_KEY in your .env file "
                f"for provider '{self.provider}'."
            )

    def _default_model(self) -> str:
        defaults = {
            # Groq rotates its free model list. openai/gpt-oss-20b is the
            # small/fast default; gpt-oss-120b, qwen3.6-27b and qwen3.8-27b
            # are the other free text models at the time of writing.
            # (llama-3.1-8b-instant and llama-3.3-70b-versatile left the
            # free tier on 2026-08-16.) If calls start failing, check
            # console.groq.com/docs/rate-limits for the current list.
            "groq": "openai/gpt-oss-20b",
            "gemini": "gemini-2.5-flash",
            "ollama": "qwen2.5:7b",
        }
        if self.provider not in defaults:
            raise ValueError(
                f"Unknown provider '{self.provider}'. "
                f"Pick one of: {', '.join(defaults)}"
            )
        return defaults[self.provider]

    def chat(self, prompt: str, temperature: float = 0.7, max_tokens: int = 300) -> LLMResponse:
        """Send one prompt, get one response. No conversation history here on purpose,
        that belongs to a later stage once you've seen a single call work cleanly."""
        if self.provider == "groq":
            return self._chat_openai_compatible(
                url="https://api.groq.com/openai/v1/chat/completions",
                prompt=prompt, temperature=temperature, max_tokens=max_tokens,
            )
        if self.provider == "gemini":
            return self._chat_gemini(prompt, temperature, max_tokens)
        if self.provider == "ollama":
            return self._chat_ollama(prompt, temperature, max_tokens)
        raise ValueError(f"Unhandled provider '{self.provider}'")

    def _chat_openai_compatible(self, url: str, prompt: str, temperature: float, max_tokens: int) -> LLMResponse:
        """Groq speaks the OpenAI-style chat format, and most other providers
        copy it, so this one method quietly covers more providers than it names."""
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        usage = data.get("usage", {})
        return LLMResponse(
            text=data["choices"][0]["message"]["content"],
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            raw=data,
        )

    def _chat_gemini(self, prompt: str, temperature: float, max_tokens: int) -> LLMResponse:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        response = requests.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        usage = data.get("usageMetadata", {})
        return LLMResponse(
            text=data["candidates"][0]["content"]["parts"][0]["text"],
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            raw=data,
        )

    def _chat_ollama(self, prompt: str, temperature: float, max_tokens: int) -> LLMResponse:
        """No API key, no internet. Ollama has to already be running locally
        (`ollama serve`) with the model pulled (`ollama pull qwen2.5:7b`)."""
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            text=data["message"]["content"],
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
            raw=data,
        )
