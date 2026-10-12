"""
The shared client is tested against a tiny fake HTTP server on localhost,
so this file needs no API key and no internet. It checks the two things
that actually matter here: that the client builds the request correctly
(URL, auth header, model name, prompt, settings) and that it reads the
response correctly (text plus the token counts).
"""

import sys
import os
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.shared.llm_client import LLMClient


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    """Pretends to be an OpenAI-compatible chat endpoint (Groq's shape)."""

    received = None

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        FakeOpenAIHandler.received = {
            "path": self.path,
            "auth": self.headers.get("Authorization"),
            "body": json.loads(self.rfile.read(length)),
        }
        payload = json.dumps({
            "choices": [{"message": {"content": "hello from the fake server"}}],
            "usage": {"prompt_tokens": 8, "completion_tokens": 5},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture()
def fake_server_url():
    server = HTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def make_client():
    os.environ["LLM_API_KEY"] = "test-key-not-real"
    return LLMClient(provider="groq")


def test_request_shape(fake_server_url):
    client = make_client()
    client._chat_openai_compatible(
        url=fake_server_url + "/v1/chat/completions",
        prompt="say hi",
        temperature=0.1,
        max_tokens=10,
    )
    got = FakeOpenAIHandler.received
    assert got["path"] == "/v1/chat/completions"
    assert got["auth"] == "Bearer test-key-not-real"
    assert got["body"]["model"] == "openai/gpt-oss-20b"
    assert got["body"]["messages"] == [{"role": "user", "content": "say hi"}]
    assert got["body"]["temperature"] == 0.1
    assert got["body"]["max_tokens"] == 10


def test_response_parsing(fake_server_url):
    client = make_client()
    response = client._chat_openai_compatible(
        url=fake_server_url + "/v1/chat/completions",
        prompt="say hi",
        temperature=0.1,
        max_tokens=10,
    )
    assert response.text == "hello from the fake server"
    assert response.prompt_tokens == 8
    assert response.completion_tokens == 5


def test_missing_key_raises_helpful_error(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ValueError, match="No API key found"):
        LLMClient(provider="groq")


def test_ollama_needs_no_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    client = LLMClient(provider="ollama")
    assert client.model == "qwen2.5:7b"


def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "x")
    with pytest.raises(ValueError, match="Unknown provider"):
        LLMClient(provider="definitely-not-a-provider")
