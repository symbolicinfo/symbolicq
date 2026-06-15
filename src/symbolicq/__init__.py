"""symbolicq: a Python client for the Symbolic Q cloud simulator.

Quick start::

    from symbolicq import QuantumCircuit, SymbolicQBackend

    backend = SymbolicQBackend()
    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    job = backend.run(qc, shots=1024, seed=7)
    print(job.result().get_counts())
"""

from __future__ import annotations

from .backend import SymbolicQBackend
from .circuit import Operation, QuantumCircuit
from .client import DEFAULT_BASE_URL, SymbolicQClient
from .config import (
    FALLBACK_BASE_URL,
    resolve_api_key,
    resolve_base_url,
)
from .exceptions import (
    APIError,
    CircuitValidationError,
    JobNotCompleteError,
    SymbolicQError,
)
from .formats import (
    ZipMember,
    make_circuit_csv_zip,
    make_circuit_json_zip,
    make_zip,
    read_first_zip_member,
    read_first_zip_text,
    read_zip_members,
)
from .gates import SUPPORTED_GATES, GateSpec, get_spec
from .job import Job
from .result import Result

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "QuantumCircuit",
    "Operation",
    "SymbolicQBackend",
    "SymbolicQClient",
    "DEFAULT_BASE_URL",
    "FALLBACK_BASE_URL",
    "resolve_base_url",
    "resolve_api_key",
    "Job",
    "Result",
    "ZipMember",
    "make_zip",
    "make_circuit_json_zip",
    "make_circuit_csv_zip",
    "read_zip_members",
    "read_first_zip_member",
    "read_first_zip_text",
    "SUPPORTED_GATES",
    "GateSpec",
    "get_spec",
    "SymbolicQError",
    "APIError",
    "JobNotCompleteError",
    "CircuitValidationError",
]
