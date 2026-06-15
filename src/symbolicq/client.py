"""Low-level HTTP client for the Symbolic Q REST API.

This maps one method per endpoint in API.md. Higher-level wrappers
(:class:`~symbolicq.backend.SymbolicQBackend`) build on top of it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .config import FALLBACK_BASE_URL, resolve_api_key, resolve_base_url
from .exceptions import APIError, JobNotCompleteError
from .formats import make_circuit_csv_zip, make_circuit_json_zip

# Kept for backwards compatibility; the effective default is resolved from the
# environment at construction time via :func:`resolve_base_url`.
DEFAULT_BASE_URL = FALLBACK_BASE_URL


class SymbolicQClient:
    """Thin requests-based wrapper over the Symbolic Q REST API.

    Args:
        base_url: API base URL. If ``None``, resolved from ``SYMBOLICQ_API_URL``
            / ``API_URL`` environment variables, falling back to
            ``https://q.symbolicinfo.com``.
        api_key: Bearer token. If ``None``, resolved from ``SYMBOLICQ_API_KEY``
            / ``API_KEY`` environment variables. When present it is sent as
            ``Authorization: Bearer {api_key}`` on every request.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = resolve_base_url(base_url).rstrip("/")
        self.api_key = resolve_api_key(api_key)
        self.timeout = timeout
        self.session = session or requests.Session()
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    # -- internals -----------------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        try:
            resp = self.session.request(method, self._url(path), **kwargs)
        except requests.RequestException as exc:  # network-level failure
            raise APIError(f"request to {path} failed: {exc}") from exc
        return resp

    def request_zip(self, method: str, path: str, **kwargs: Any) -> bytes:
        """Request any endpoint with ``Accept: application/zip``.

        This is the escape hatch for API.md's rule that normal JSON/CSV
        responses can be wrapped as ZIP via ``Accept`` or ``?zip=1``.
        """
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("Accept", "application/zip")
        params = dict(kwargs.pop("params", {}) or {})
        params.setdefault("zip", "1")
        return self._parse_bytes(
            self._request(method, path, headers=headers, params=params, **kwargs)
        )

    @staticmethod
    def _parse(resp: requests.Response) -> Dict[str, Any]:
        payload = SymbolicQClient._json_or_empty(resp)

        if resp.ok:
            return payload

        SymbolicQClient._raise_for_error(resp, payload)
        return payload

    @staticmethod
    def _json_or_empty(resp: requests.Response) -> Dict[str, Any]:
        try:
            payload = resp.json()
        except ValueError:
            return {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _raise_for_error(
        resp: requests.Response, payload: Optional[Dict[str, Any]] = None
    ) -> None:
        payload = payload if payload is not None else SymbolicQClient._json_or_empty(resp)
        message = payload.get("error") if isinstance(payload, dict) else None
        message = message or f"HTTP {resp.status_code}"
        if resp.status_code == 409:
            raise JobNotCompleteError(message, resp.status_code, payload)
        raise APIError(message, resp.status_code, payload)

    @staticmethod
    def _parse_text(resp: requests.Response) -> str:
        if resp.ok:
            return resp.text
        SymbolicQClient._raise_for_error(resp)
        return resp.text

    @staticmethod
    def _parse_bytes(resp: requests.Response) -> bytes:
        if resp.ok:
            return resp.content
        SymbolicQClient._raise_for_error(resp)
        return resp.content

    # -- health --------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """GET /health"""
        return self._parse(self._request("GET", "/health"))

    # -- circuits ------------------------------------------------------------
    def create_circuit(self, circuit_body: Dict[str, Any]) -> Dict[str, Any]:
        """POST /circuits (JSON). Returns ``{"circuit_id", "circuit"}``."""
        return self._parse(self._request("POST", "/circuits", json=circuit_body))

    def create_circuit_csv(self, csv_text: str) -> Dict[str, Any]:
        """POST /circuits with a ``text/csv`` body."""
        headers = {"Content-Type": "text/csv"}
        return self._parse(
            self._request("POST", "/circuits", data=csv_text.encode("utf-8"), headers=headers)
        )

    def create_circuit_zip(
        self, zip_bytes: bytes, inner_content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """POST /circuits with an ``application/zip`` body.

        ``inner_content_type`` is sent as ``X-Zip-Content-Type`` for archives
        whose member names do not carry a ``.json`` or ``.csv`` extension.
        """
        headers = {"Content-Type": "application/zip"}
        if inner_content_type:
            headers["X-Zip-Content-Type"] = inner_content_type
        return self._parse(
            self._request("POST", "/circuits", data=zip_bytes, headers=headers)
        )

    def create_circuit_json_zip(
        self, circuit_body: Dict[str, Any], filename: str = "circuit.json"
    ) -> Dict[str, Any]:
        """POST /circuits with a JSON circuit packed into ZIP bytes."""
        return self.create_circuit_zip(make_circuit_json_zip(circuit_body, filename))

    def create_circuit_csv_zip(
        self, csv_text: str, filename: str = "circuit.csv"
    ) -> Dict[str, Any]:
        """POST /circuits with a CSV circuit packed into ZIP bytes."""
        return self.create_circuit_zip(make_circuit_csv_zip(csv_text, filename))

    def get_circuit(self, circuit_id: str) -> Dict[str, Any]:
        """GET /circuits/{circuit_id}"""
        return self._parse(self._request("GET", f"/circuits/{circuit_id}"))

    def get_circuit_csv(self, circuit_id: str) -> str:
        """GET /circuits/{circuit_id}?format=csv as CSV text."""
        return self._parse_text(
            self._request(
                "GET",
                f"/circuits/{circuit_id}",
                params={"format": "csv"},
                headers={"Accept": "text/csv"},
            )
        )

    def get_circuit_zip(self, circuit_id: str) -> bytes:
        """GET /circuits/{circuit_id}?zip=1 as ZIP bytes."""
        return self.request_zip("GET", f"/circuits/{circuit_id}")

    def delete_circuit(self, circuit_id: str) -> Dict[str, Any]:
        """DELETE /circuits/{circuit_id}"""
        return self._parse(self._request("DELETE", f"/circuits/{circuit_id}"))

    def list_circuits(self) -> List[Dict[str, Any]]:
        """GET /circuits"""
        return self._parse(self._request("GET", "/circuits")).get("circuits", [])

    # -- runs ----------------------------------------------------------------
    def create_run(
        self,
        circuit_id: str,
        shots: int = 1024,
        seed: Optional[int] = None,
        seed_simulator: Optional[int] = None,
        simulator_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST /circuits/{circuit_id}/runs. Returns ``{"job_id", "status"}``."""
        body: Dict[str, Any] = {"shots": shots}
        if seed is not None:
            body["seed"] = seed
        if seed_simulator is not None:
            body["seed_simulator"] = seed_simulator
        if simulator_options:
            body["simulator_options"] = simulator_options
        return self._parse(
            self._request("POST", f"/circuits/{circuit_id}/runs", json=body)
        )

    def get_status(
        self, job_id: str, counts_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """GET /runs/{job_id}/status"""
        params = {"counts_limit": counts_limit} if counts_limit is not None else None
        return self._parse(
            self._request("GET", f"/runs/{job_id}/status", params=params)
        )

    def get_result(self, job_id: str) -> Dict[str, Any]:
        """GET /runs/{job_id}/result. Raises JobNotCompleteError on HTTP 409."""
        return self._parse(self._request("GET", f"/runs/{job_id}/result"))

    def get_result_csv(self, job_id: str) -> str:
        """GET /runs/{job_id}/result?format=csv as CSV text."""
        return self._parse_text(
            self._request(
                "GET",
                f"/runs/{job_id}/result",
                params={"format": "csv"},
                headers={"Accept": "text/csv"},
            )
        )

    def get_result_zip(self, job_id: str) -> bytes:
        """GET /runs/{job_id}/result?zip=1 as ZIP bytes."""
        return self.request_zip("GET", f"/runs/{job_id}/result")

    def cancel_run(self, job_id: str) -> Dict[str, Any]:
        """POST /runs/{job_id}/cancel"""
        return self._parse(self._request("POST", f"/runs/{job_id}/cancel"))

    def list_runs(self) -> List[Dict[str, Any]]:
        """GET /runs"""
        return self._parse(self._request("GET", "/runs")).get("runs", [])
