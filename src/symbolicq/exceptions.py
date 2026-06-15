"""Exception types raised by the symbolicq client."""

from __future__ import annotations

from typing import Optional


class SymbolicQError(Exception):
    """Base class for all symbolicq errors."""


class APIError(SymbolicQError):
    """Raised when the Symbolic Q API returns an error response.

    Attributes:
        status_code: HTTP status code returned by the server (if any).
        payload: Parsed JSON body of the error response (if any).
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        payload: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class JobNotCompleteError(APIError):
    """Raised when a result is requested for a job that is not completed (HTTP 409)."""


class CircuitValidationError(SymbolicQError):
    """Raised when a circuit fails local validation before being sent."""
