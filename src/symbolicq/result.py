"""Result object returned by a completed job."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, Optional


class Result:
    """Wraps the ``result`` payload from GET /runs/{job_id}/result.

    Provides ``get_counts`` / ``get_probabilities`` accessors.
    """

    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload
        self.job_id = payload.get("job_id")
        self.status = payload.get("status")
        self._result = payload.get("result", {}) or {}

    def get_counts(self) -> Dict[str, int]:
        """Return the measurement counts as ``{bitstring: count}``.

        Bitstrings follow the API bit order: MSB-left ``c[n-1] ... c[0]``.
        """
        return dict(self._result.get("counts", {}))

    def get_probabilities(self) -> Dict[str, float]:
        """Return ``{bitstring: probability}``."""
        return dict(self._result.get("probabilities", {}))

    def probability(self, bitstring: str, default: float = 0.0) -> float:
        """Return the probability for one bitstring."""
        return float(self.get_probabilities().get(bitstring, default))

    def count(self, bitstring: str, default: int = 0) -> int:
        """Return the sampled count for one bitstring."""
        return int(self.get_counts().get(bitstring, default))

    def most_frequent(self) -> Optional[str]:
        """Return the bitstring with the largest count, or ``None`` if empty."""
        counts = self.get_counts()
        if not counts:
            return None
        return max(counts, key=counts.get)

    @property
    def shots(self) -> Optional[int]:
        return self._result.get("shots")

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._result.get("metadata", {}) or {}

    @property
    def backend_name(self) -> Optional[str]:
        return self.metadata.get("backend")

    def to_dict(self) -> Dict[str, Any]:
        return self._payload

    def to_csv(self) -> str:
        """Serialize counts/probabilities as API.md result CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["bitstring", "count", "probability"],
            lineterminator="\n",
        )
        writer.writeheader()
        counts = self.get_counts()
        probabilities = self.get_probabilities()
        for bitstring in sorted(set(counts) | set(probabilities)):
            writer.writerow(
                {
                    "bitstring": bitstring,
                    "count": counts.get(bitstring, ""),
                    "probability": probabilities.get(bitstring, ""),
                }
            )
        return output.getvalue()

    @classmethod
    def from_csv(
        cls,
        csv_text: str,
        job_id: Optional[str] = None,
        status: str = "completed",
    ) -> "Result":
        """Build a :class:`Result` from API.md result CSV text."""
        reader = csv.DictReader(io.StringIO(csv_text))
        counts: Dict[str, int] = {}
        probabilities: Dict[str, float] = {}
        for row in reader:
            bitstring = (row.get("bitstring") or "").strip()
            if not bitstring:
                continue
            count_text = (row.get("count") or "").strip()
            probability_text = (row.get("probability") or "").strip()
            if count_text:
                counts[bitstring] = int(count_text)
            if probability_text:
                probabilities[bitstring] = float(probability_text)
        shots = sum(counts.values()) if counts else None
        return cls(
            {
                "job_id": job_id,
                "status": status,
                "result": {
                    "counts": counts,
                    "probabilities": probabilities,
                    "shots": shots,
                    "metadata": {},
                },
            }
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Result(job_id={self.job_id!r}, status={self.status!r}, shots={self.shots})"
