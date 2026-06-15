"""A lightweight quantum circuit builder.

This mirrors a useful subset of a conventional circuit builder API so that
users feel at home, while staying dependency-free. The circuit serializes
directly to the operation format described in API.md sections 2 and 11.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Optional, Sequence, Union

from .exceptions import CircuitValidationError
from .gates import get_spec

QubitArg = Union[int, Sequence[int]]

_MIN_QUBITS = {
    "reset": 1,
    "barrier": 0,
    "mcx": 2,
    "mcy": 2,
    "mcz": 1,
    "mcp": 1,
    "mcrx": 2,
    "mcry": 2,
    "mcrz": 2,
}


class Operation:
    """A single gate operation, matching the API.md operation object."""

    __slots__ = ("name", "qubits", "clbits", "params", "metadata")

    def __init__(
        self,
        name: str,
        qubits: Optional[List[int]] = None,
        clbits: Optional[List[int]] = None,
        params: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.qubits = list(qubits or [])
        self.clbits = list(clbits or [])
        self.params = list(params or [])
        self.metadata = dict(metadata or {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "qubits": self.qubits,
            "clbits": self.clbits,
            "params": self.params,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Operation":
        return cls(
            name=d["name"],
            qubits=d.get("qubits"),
            clbits=d.get("clbits"),
            params=d.get("params"),
            metadata=d.get("metadata"),
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"Operation(name={self.name!r}, qubits={self.qubits}, "
            f"clbits={self.clbits}, params={self.params})"
        )


def _as_int_list(value: QubitArg) -> List[int]:
    if isinstance(value, int):
        return [value]
    return [int(v) for v in value]


def _parse_list_cell(value: Optional[str], cast: Any) -> List[Any]:
    if value is None:
        return []
    text = value.strip()
    if not text:
        return []
    parts = text.replace(",", " ").split()
    return [cast(part) for part in parts]


def _format_list_cell(values: Sequence[Any]) -> str:
    return " ".join(str(value) for value in values)


def _optional_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    text = value.strip()
    return int(text) if text else None


class QuantumCircuit:
    """A quantum circuit builder with a familiar gate-method API.

    Example::

        from symbolicq import QuantumCircuit

        qc = QuantumCircuit(2, 2, name="bell")
        qc.h(0)
        qc.cx(0, 1)
        qc.measure(0, 0)
        qc.measure(1, 1)
    """

    def __init__(
        self,
        num_qubits: int,
        num_clbits: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        if num_qubits is None or int(num_qubits) < 0:
            raise CircuitValidationError("num_qubits must be a non-negative int")
        self.num_qubits = int(num_qubits)
        self.num_clbits = int(num_clbits) if num_clbits is not None else self.num_qubits
        self.name = name
        self.operations: List[Operation] = []

    # -- core append ---------------------------------------------------------
    def append(
        self,
        name: str,
        qubits: Optional[QubitArg] = None,
        clbits: Optional[QubitArg] = None,
        params: Optional[Sequence[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "QuantumCircuit":
        """Append a gate operation, validating against the supported gate set."""
        qlist = _as_int_list(qubits) if qubits is not None else []
        clist = _as_int_list(clbits) if clbits is not None else []
        plist = [float(p) for p in params] if params is not None else []

        self._validate(name, qlist, clist, plist)
        self.operations.append(Operation(name.lower(), qlist, clist, plist, metadata))
        return self

    def _validate(
        self, name: str, qubits: List[int], clbits: List[int], params: List[float]
    ) -> None:
        spec = get_spec(name)
        if spec is None:
            raise CircuitValidationError(
                f"unsupported gate: {name!r}. See symbolicq.gates.SUPPORTED_GATES"
            )
        if spec.qubits is not None and len(qubits) != spec.qubits:
            raise CircuitValidationError(
                f"gate {name!r} expects {spec.qubits} qubit(s), got {len(qubits)}"
            )
        minimum = _MIN_QUBITS.get(name.lower())
        if minimum is not None and len(qubits) < minimum:
            raise CircuitValidationError(
                f"gate {name!r} expects at least {minimum} qubit(s), got {len(qubits)}"
            )
        if spec.params is not None and len(params) != spec.params:
            raise CircuitValidationError(
                f"gate {name!r} expects {spec.params} param(s), got {len(params)}"
            )
        for q in qubits:
            if q < 0 or q >= self.num_qubits:
                raise CircuitValidationError(
                    f"qubit index {q} out of range [0, {self.num_qubits})"
                )
        for c in clbits:
            if c < 0 or c >= self.num_clbits:
                raise CircuitValidationError(
                    f"clbit index {c} out of range [0, {self.num_clbits})"
                )

    # -- gate convenience methods -------------------------------------------
    # single-qubit, no params
    def id(self, q: int) -> "QuantumCircuit": return self.append("id", q)
    def x(self, q: int) -> "QuantumCircuit": return self.append("x", q)
    def y(self, q: int) -> "QuantumCircuit": return self.append("y", q)
    def z(self, q: int) -> "QuantumCircuit": return self.append("z", q)
    def h(self, q: int) -> "QuantumCircuit": return self.append("h", q)
    def s(self, q: int) -> "QuantumCircuit": return self.append("s", q)
    def sdg(self, q: int) -> "QuantumCircuit": return self.append("sdg", q)
    def t(self, q: int) -> "QuantumCircuit": return self.append("t", q)
    def tdg(self, q: int) -> "QuantumCircuit": return self.append("tdg", q)
    def sx(self, q: int) -> "QuantumCircuit": return self.append("sx", q)
    def sxdg(self, q: int) -> "QuantumCircuit": return self.append("sxdg", q)

    # single-qubit, params
    def p(self, theta: float, q: int) -> "QuantumCircuit": return self.append("p", q, params=[theta])
    def phase(self, theta: float, q: int) -> "QuantumCircuit": return self.append("phase", q, params=[theta])
    def rx(self, theta: float, q: int) -> "QuantumCircuit": return self.append("rx", q, params=[theta])
    def ry(self, theta: float, q: int) -> "QuantumCircuit": return self.append("ry", q, params=[theta])
    def rz(self, theta: float, q: int) -> "QuantumCircuit": return self.append("rz", q, params=[theta])
    def u(self, theta: float, phi: float, lam: float, q: int) -> "QuantumCircuit":
        return self.append("u", q, params=[theta, phi, lam])
    def u1(self, lam: float, q: int) -> "QuantumCircuit": return self.append("u1", q, params=[lam])
    def u2(self, phi: float, lam: float, q: int) -> "QuantumCircuit":
        return self.append("u2", q, params=[phi, lam])
    def u3(self, theta: float, phi: float, lam: float, q: int) -> "QuantumCircuit":
        return self.append("u3", q, params=[theta, phi, lam])

    # two-qubit
    def cx(self, control: int, target: int) -> "QuantumCircuit": return self.append("cx", [control, target])
    def cnot(self, control: int, target: int) -> "QuantumCircuit": return self.append("cx", [control, target])
    def cy(self, control: int, target: int) -> "QuantumCircuit": return self.append("cy", [control, target])
    def cz(self, control: int, target: int) -> "QuantumCircuit": return self.append("cz", [control, target])
    def ch(self, control: int, target: int) -> "QuantumCircuit": return self.append("ch", [control, target])
    def csx(self, control: int, target: int) -> "QuantumCircuit": return self.append("csx", [control, target])
    def swap(self, a: int, b: int) -> "QuantumCircuit": return self.append("swap", [a, b])
    def iswap(self, a: int, b: int) -> "QuantumCircuit": return self.append("iswap", [a, b])
    def dcx(self, a: int, b: int) -> "QuantumCircuit": return self.append("dcx", [a, b])
    def ecr(self, a: int, b: int) -> "QuantumCircuit": return self.append("ecr", [a, b])
    def cp(self, theta: float, control: int, target: int) -> "QuantumCircuit":
        return self.append("cp", [control, target], params=[theta])
    def cu1(self, theta: float, control: int, target: int) -> "QuantumCircuit":
        return self.append("cu1", [control, target], params=[theta])
    def crx(self, theta: float, control: int, target: int) -> "QuantumCircuit":
        return self.append("crx", [control, target], params=[theta])
    def cry(self, theta: float, control: int, target: int) -> "QuantumCircuit":
        return self.append("cry", [control, target], params=[theta])
    def crz(self, theta: float, control: int, target: int) -> "QuantumCircuit":
        return self.append("crz", [control, target], params=[theta])
    def cu(
        self, theta: float, phi: float, lam: float, gamma: float, control: int, target: int
    ) -> "QuantumCircuit":
        return self.append("cu", [control, target], params=[theta, phi, lam, gamma])
    def cu3(
        self, theta: float, phi: float, lam: float, control: int, target: int
    ) -> "QuantumCircuit":
        return self.append("cu3", [control, target], params=[theta, phi, lam])
    def rxx(self, theta: float, a: int, b: int) -> "QuantumCircuit":
        return self.append("rxx", [a, b], params=[theta])
    def ryy(self, theta: float, a: int, b: int) -> "QuantumCircuit":
        return self.append("ryy", [a, b], params=[theta])
    def rzz(self, theta: float, a: int, b: int) -> "QuantumCircuit":
        return self.append("rzz", [a, b], params=[theta])
    def rzx(self, theta: float, a: int, b: int) -> "QuantumCircuit":
        return self.append("rzx", [a, b], params=[theta])

    # three-qubit
    def ccx(self, c1: int, c2: int, target: int) -> "QuantumCircuit":
        return self.append("ccx", [c1, c2, target])
    toffoli = ccx
    def ccz(self, c1: int, c2: int, target: int) -> "QuantumCircuit":
        return self.append("ccz", [c1, c2, target])
    def cswap(self, control: int, a: int, b: int) -> "QuantumCircuit":
        return self.append("cswap", [control, a, b])
    fredkin = cswap

    # multi-controlled
    def mcx(self, controls: Sequence[int], target: int) -> "QuantumCircuit":
        return self.append("mcx", list(controls) + [target])
    def mcy(self, controls: Sequence[int], target: int) -> "QuantumCircuit":
        return self.append("mcy", list(controls) + [target])
    def mcz(self, qubits: Sequence[int]) -> "QuantumCircuit":
        return self.append("mcz", list(qubits))
    def mcp(self, theta: float, qubits: Sequence[int]) -> "QuantumCircuit":
        return self.append("mcp", list(qubits), params=[theta])
    def mcrx(self, theta: float, controls: Sequence[int], target: int) -> "QuantumCircuit":
        return self.append("mcrx", list(controls) + [target], params=[theta])
    def mcry(self, theta: float, controls: Sequence[int], target: int) -> "QuantumCircuit":
        return self.append("mcry", list(controls) + [target], params=[theta])
    def mcrz(self, theta: float, controls: Sequence[int], target: int) -> "QuantumCircuit":
        return self.append("mcrz", list(controls) + [target], params=[theta])

    # special
    def measure(self, qubit: int, clbit: int) -> "QuantumCircuit":
        return self.append("measure", qubit, clbit)

    def measure_all(self) -> "QuantumCircuit":
        """Measure every qubit into the classical bit of the same index."""
        if self.num_clbits < self.num_qubits:
            raise CircuitValidationError(
                "measure_all requires num_clbits >= num_qubits"
            )
        for q in range(self.num_qubits):
            self.measure(q, q)
        return self

    def reset(self, qubits: QubitArg) -> "QuantumCircuit": return self.append("reset", qubits)

    def barrier(self, qubits: Optional[Sequence[int]] = None) -> "QuantumCircuit":
        targets = list(range(self.num_qubits)) if qubits is None else list(qubits)
        return self.append("barrier", targets)

    def delay(self, duration: float, q: int, unit: str = "dt") -> "QuantumCircuit":
        return self.append("delay", q, params=[duration], metadata={"unit": unit})

    def global_phase(self, theta: float) -> "QuantumCircuit":
        return self.append("global_phase", params=[theta])

    # -- serialization -------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to the JSON request body of POST /circuits."""
        body: Dict[str, Any] = {
            "num_qubits": self.num_qubits,
            "num_clbits": self.num_clbits,
            "operations": [op.to_dict() for op in self.operations],
        }
        if self.name is not None:
            body["name"] = self.name
        return body

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QuantumCircuit":
        """Build a circuit from a server circuit object (GET /circuits/{id})."""
        circuit = d.get("circuit", d)
        qc = cls(
            num_qubits=circuit["num_qubits"],
            num_clbits=circuit.get("num_clbits"),
            name=circuit.get("name"),
        )
        for op in circuit.get("operations", []):
            qc.operations.append(Operation.from_dict(op))
        return qc

    def to_csv(self, include_circuit_metadata: bool = True) -> str:
        """Serialize the circuit to the CSV format accepted by POST /circuits."""
        output = io.StringIO()
        fieldnames = [
            "name",
            "qubits",
            "clbits",
            "params",
            "metadata",
            "num_qubits",
            "num_clbits",
            "circuit_name",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for index, op in enumerate(self.operations):
            row = {
                "name": op.name,
                "qubits": _format_list_cell(op.qubits),
                "clbits": _format_list_cell(op.clbits),
                "params": _format_list_cell(op.params),
                "metadata": json.dumps(op.metadata) if op.metadata else "",
                "num_qubits": "",
                "num_clbits": "",
                "circuit_name": "",
            }
            if include_circuit_metadata and index == 0:
                row["num_qubits"] = str(self.num_qubits)
                row["num_clbits"] = str(self.num_clbits)
                row["circuit_name"] = self.name or ""
            writer.writerow(row)
        return output.getvalue()

    @classmethod
    def from_csv(cls, csv_text: str) -> "QuantumCircuit":
        """Build a circuit from the API.md CSV circuit format."""
        reader = csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames or "name" not in reader.fieldnames:
            raise CircuitValidationError("CSV circuit must include a name column")

        rows = list(reader)
        if not rows:
            raise CircuitValidationError("CSV circuit must include at least one row")

        first = rows[0]
        num_qubits = _optional_int(first.get("num_qubits"))
        num_clbits = _optional_int(first.get("num_clbits"))
        name = first.get("circuit_name") or None

        parsed_ops = []
        max_qubit = -1
        max_clbit = -1
        for row in rows:
            op_name = (row.get("name") or "").strip()
            if not op_name:
                raise CircuitValidationError("CSV operation row is missing name")
            qubits = _parse_list_cell(row.get("qubits"), int)
            clbits = _parse_list_cell(row.get("clbits"), int)
            params = _parse_list_cell(row.get("params"), float)
            metadata_text = (row.get("metadata") or "").strip()
            metadata = json.loads(metadata_text) if metadata_text else {}
            if not isinstance(metadata, dict):
                raise CircuitValidationError("CSV metadata must be a JSON object")
            max_qubit = max([max_qubit] + qubits)
            max_clbit = max([max_clbit] + clbits)
            parsed_ops.append((op_name, qubits, clbits, params, metadata))

        if num_qubits is None:
            if max_qubit < 0:
                raise CircuitValidationError(
                    "CSV circuit needs num_qubits when no qubit columns are present"
                )
            num_qubits = max_qubit + 1
        if num_clbits is None:
            num_clbits = max(num_qubits, max_clbit + 1)

        qc = cls(num_qubits=num_qubits, num_clbits=num_clbits, name=name)
        for op_name, qubits, clbits, params, metadata in parsed_ops:
            qc.append(op_name, qubits, clbits, params, metadata)
        return qc

    def __len__(self) -> int:
        return len(self.operations)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"QuantumCircuit(num_qubits={self.num_qubits}, "
            f"num_clbits={self.num_clbits}, name={self.name!r}, "
            f"ops={len(self.operations)})"
        )
