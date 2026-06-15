"""Asynchronous job handle (``job.result()``, ``job.status()``, ``job.cancel()``)."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, Optional

from .exceptions import APIError, JobNotCompleteError
from .result import Result

if TYPE_CHECKING:  # pragma: no cover
    from .client import SymbolicQClient

TERMINAL_STATES = {"completed", "failed", "cancelled"}


class Job:
    """Handle to a run created via :meth:`SymbolicQBackend.run`.

    Example::

        job = backend.run(qc, shots=1024)
        result = job.result()        # blocks until completion
        print(result.get_counts())
    """

    def __init__(
        self, client: "SymbolicQClient", job_id: str, circuit_id: Optional[str] = None
    ) -> None:
        self._client = client
        self.job_id = job_id
        self.circuit_id = circuit_id

    def status(self, counts_limit: Optional[int] = None) -> Dict[str, Any]:
        """Return the raw status payload (GET /runs/{job_id}/status)."""
        return self._client.get_status(self.job_id, counts_limit=counts_limit)

    def status_text(self) -> Optional[str]:
        """Return the current job status string."""
        return self.status().get("status")

    def progress(self) -> Dict[str, Any]:
        """Return the API progress object, or an empty dict when absent."""
        return self.status().get("progress", {}) or {}

    def progress_ratio(self) -> Optional[float]:
        """Return progress.ratio when the server reports it."""
        ratio = self.progress().get("ratio")
        return None if ratio is None else float(ratio)

    def done(self) -> bool:
        """True if the job has reached a terminal state."""
        return self.status().get("status") in TERMINAL_STATES

    def cancel(self) -> Dict[str, Any]:
        """Request cancellation (POST /runs/{job_id}/cancel)."""
        return self._client.cancel_run(self.job_id)

    def wait_for_final_state(
        self, timeout: Optional[float] = None, poll_interval: float = 1.0
    ) -> Dict[str, Any]:
        """Block until the job reaches a terminal state.

        Args:
            timeout: max seconds to wait; ``None`` means wait indefinitely.
            poll_interval: seconds between status polls.

        Returns:
            The final status payload.

        Raises:
            TimeoutError: if ``timeout`` elapses before completion.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            status = self.status()
            if status.get("status") in TERMINAL_STATES:
                return status
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(
                    f"job {self.job_id} did not finish within {timeout}s"
                )
            time.sleep(poll_interval)

    def result(
        self, timeout: Optional[float] = None, poll_interval: float = 1.0
    ) -> Result:
        """Block until completion and return the :class:`Result`.

        Raises:
            APIError: if the job finished in ``failed`` or ``cancelled`` state.
        """
        final = self.wait_for_final_state(timeout=timeout, poll_interval=poll_interval)
        state = final.get("status")
        if state != "completed":
            raise APIError(
                f"job {self.job_id} ended in state {state!r}; no result available",
                payload=final,
            )
        try:
            payload = self._client.get_result(self.job_id)
        except JobNotCompleteError as exc:  # pragma: no cover - race guard
            raise APIError(
                f"job {self.job_id} reported completed but result is not ready",
                payload=exc.payload,
            ) from exc
        return Result(payload)

    def refresh_result(self) -> Result:
        """Return the result immediately, raising if the job is not completed."""
        return Result(self._client.get_result(self.job_id))

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Job(job_id={self.job_id!r}, circuit_id={self.circuit_id!r})"
