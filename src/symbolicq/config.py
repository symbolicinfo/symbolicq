"""Configuration resolution for the Symbolic Q client.

Settings are resolved in this order (first non-empty wins):

1. Explicit argument passed to the client/backend.
2. Namespaced environment variable: ``SYMBOLICQ_API_URL`` / ``SYMBOLICQ_API_KEY``.
3. Generic environment variable: ``API_URL`` / ``API_KEY``.
4. Built-in default (URL only).
"""

from __future__ import annotations

import os
from typing import Optional

# Built-in fallback used only when no env var / argument provides a URL.
FALLBACK_BASE_URL = "https://q.symbolicinfo.com"


def _env(*names: str) -> Optional[str]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def resolve_base_url(explicit: Optional[str] = None) -> str:
    """Resolve the API base URL (argument > env > fallback)."""
    if explicit:
        return explicit
    return _env("SYMBOLICQ_API_URL", "API_URL") or FALLBACK_BASE_URL


def resolve_api_key(explicit: Optional[str] = None) -> Optional[str]:
    """Resolve the API key (argument > env). May be ``None``."""
    if explicit:
        return explicit
    return _env("SYMBOLICQ_API_KEY", "API_KEY")
