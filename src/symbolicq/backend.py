"""Backend that runs circuits against the Symbolic Q cloud simulator."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from .circuit import QuantumCircuit
from .client import SymbolicQClient
from .job import Job

CircuitLike = Union[QuantumCircuit, Dict[str, Any]]


class SymbolicQBackend:
    """A backend with a ``run(circuit) -> job -> result`` interface.

    ``base_url`` and ``api_key`` default to values resolved from the environment
    (``SYMBOLICQ_API_URL`` / ``API_URL`` and
    ``SYMBOLICQ_API_KEY`` / ``API_KEY``). See :mod:`symbolicq.config`.

    Example::

        from symbolicq import QuantumCircuit, SymbolicQBackend

        backend = SymbolicQBackend()        # reads API_URL / API_KEY from env
        qc = QuantumCircuit(2, 2, name="bell")
        qc.h(0); qc.cx(0, 1); qc.measure_all()

        job = backend.run(qc, shots=1024, seed=7)
        print(job.result().get_counts())
    """

    name = "symbolic_q_simulator"

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        client: Optional[SymbolicQClient] = None,
        **client_kwargs: Any,
    ) -> None:
        self._client = client or SymbolicQClient(
            base_url=base_url, api_key=api_key, **client_kwargs
        )

    @property
    def client(self) -> SymbolicQClient:
        return self._client

    def status(self) -> Dict[str, Any]:
        """Backend availability, derived from the /health endpoint."""
        return self._client.health()

    def upload_circuit(self, circuit: CircuitLike, verbose: bool = False) -> str:
        """Upload a JSON circuit body and return its server circuit id."""
        body = circuit.to_dict() if isinstance(circuit, QuantumCircuit) else circuit
        return self._client.create_circuit(body, verbose=verbose)["circuit_id"]

    def upload_circuit_csv(self, csv_text: str) -> str:
        """Upload a CSV circuit body and return its server circuit id."""
        return self._client.create_circuit_csv(csv_text)["circuit_id"]

    def upload_circuit_zip(
        self, zip_bytes: bytes, inner_content_type: Optional[str] = None
    ) -> str:
        """Upload a ZIP circuit body and return its server circuit id."""
        return self._client.create_circuit_zip(zip_bytes, inner_content_type)[
            "circuit_id"
        ]

    def run(
        self,
        circuit: CircuitLike,
        shots: int = 1024,
        seed: Optional[int] = None,
        seed_simulator: Optional[int] = None,
        simulator_options: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
    ) -> Job:
        """Upload ``circuit`` and start a run, returning a :class:`Job`.

        Args:
            circuit: a :class:`QuantumCircuit` or a circuit dict (API.md body).
            shots: number of shots (default 1024).
            seed: random seed.
            seed_simulator: simulator seed.
            simulator_options: e.g.
                ``{"measurement_uses_density": True, "settle_after_instruction": True}``.
            verbose: if true, print JSON circuit upload progress to stderr.
        """
        circuit_id = self.upload_circuit(circuit, verbose=verbose)

        run = self._client.create_run(
            circuit_id,
            shots=shots,
            seed=seed,
            seed_simulator=seed_simulator,
            simulator_options=simulator_options,
        )
        return Job(self._client, run["job_id"], circuit_id=circuit_id)

    def run_circuit_id(
        self, circuit_id: str, shots: int = 1024, **run_kwargs: Any
    ) -> Job:
        """Start a run for an already-uploaded circuit id."""
        run = self._client.create_run(circuit_id, shots=shots, **run_kwargs)
        return Job(self._client, run["job_id"], circuit_id=circuit_id)

    def run_csv(
        self, csv_text: str, shots: int = 1024, **run_kwargs: Any
    ) -> Job:
        """Upload a CSV circuit body, start a run, and return a job."""
        circuit_id = self.upload_circuit_csv(csv_text)
        return self.run_circuit_id(circuit_id, shots=shots, **run_kwargs)

    def run_zip(
        self,
        zip_bytes: bytes,
        shots: int = 1024,
        inner_content_type: Optional[str] = None,
        **run_kwargs: Any,
    ) -> Job:
        """Upload a ZIP circuit body, start a run, and return a job."""
        circuit_id = self.upload_circuit_zip(zip_bytes, inner_content_type)
        return self.run_circuit_id(circuit_id, shots=shots, **run_kwargs)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"SymbolicQBackend(base_url={self._client.base_url!r})"
