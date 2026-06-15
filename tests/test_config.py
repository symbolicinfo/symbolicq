from symbolicq import SymbolicQClient
from symbolicq.config import (
    FALLBACK_BASE_URL,
    resolve_api_key,
    resolve_base_url,
)


def _clear_env(monkeypatch):
    # Prevent the real environment from leaking into these tests.
    for name in ("SYMBOLICQ_API_URL", "API_URL", "SYMBOLICQ_API_KEY", "API_KEY"):
        monkeypatch.delenv(name, raising=False)


def test_explicit_argument_wins(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_URL", "https://env.example")
    assert resolve_base_url("https://explicit.example") == "https://explicit.example"


def test_namespaced_env_beats_generic(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_URL", "https://generic.example")
    monkeypatch.setenv("SYMBOLICQ_API_URL", "https://namespaced.example")
    assert resolve_base_url() == "https://namespaced.example"


def test_generic_env_used(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_URL", "https://generic.example")
    assert resolve_base_url() == "https://generic.example"


def test_fallback_when_no_env(monkeypatch):
    _clear_env(monkeypatch)
    assert resolve_base_url() == FALLBACK_BASE_URL


def test_api_key_resolution(monkeypatch):
    _clear_env(monkeypatch)
    assert resolve_api_key() is None
    monkeypatch.setenv("API_KEY", "k1")
    assert resolve_api_key() == "k1"
    monkeypatch.setenv("SYMBOLICQ_API_KEY", "k2")
    assert resolve_api_key() == "k2"
    assert resolve_api_key("explicit") == "explicit"


def test_client_sets_bearer_header(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_KEY", "secret-token")
    monkeypatch.setenv("API_URL", "https://configured.example")
    client = SymbolicQClient()
    assert client.base_url == "https://configured.example"
    assert client.session.headers["Authorization"] == "Bearer secret-token"


def test_client_no_header_without_key(monkeypatch):
    _clear_env(monkeypatch)
    client = SymbolicQClient()
    assert "Authorization" not in client.session.headers
    assert client.base_url == FALLBACK_BASE_URL
