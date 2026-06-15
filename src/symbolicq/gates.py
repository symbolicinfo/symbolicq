"""Supported gate metadata, mirroring API.md section 12.

Each entry describes the expected number of qubits and params for a gate so the
:class:`~symbolicq.circuit.QuantumCircuit` builder can validate operations
locally before sending them to the server.

``qubits``/``params`` use ``None`` to mean "variable" (e.g. multi-controlled
gates, ``reset``, ``barrier``).
"""

from __future__ import annotations

from typing import Dict, NamedTuple, Optional


class GateSpec(NamedTuple):
    qubits: Optional[int]  # required qubit count, None == variable
    params: Optional[int]  # required param count, None == variable
    note: str = ""


# --- 12.1 single-qubit gates ------------------------------------------------
_SINGLE = {
    "id": GateSpec(1, 0, "identity"),
    "i": GateSpec(1, 0, "id alias"),
    "x": GateSpec(1, 0, "Pauli-X"),
    "y": GateSpec(1, 0, "Pauli-Y"),
    "z": GateSpec(1, 0, "Pauli-Z"),
    "h": GateSpec(1, 0, "Hadamard"),
    "s": GateSpec(1, 0, "S"),
    "sdg": GateSpec(1, 0, "S dagger"),
    "t": GateSpec(1, 0, "T"),
    "tdg": GateSpec(1, 0, "T dagger"),
    "sx": GateSpec(1, 0, "sqrt-X"),
    "sxdg": GateSpec(1, 0, "sqrt-X dagger"),
    "p": GateSpec(1, 1, "phase(theta)"),
    "phase": GateSpec(1, 1, "p alias"),
    "rx": GateSpec(1, 1, "rx(theta)"),
    "ry": GateSpec(1, 1, "ry(theta)"),
    "rz": GateSpec(1, 1, "rz(theta)"),
    "u": GateSpec(1, 3, "u(theta, phi, lam)"),
    "u1": GateSpec(1, 1, "p(lam) alias"),
    "u2": GateSpec(1, 2, "u2(phi, lam)"),
    "u3": GateSpec(1, 3, "u alias"),
}

# --- 12.2 two-qubit / controlled gates --------------------------------------
_TWO = {
    "cx": GateSpec(2, 0, "CNOT"),
    "cnot": GateSpec(2, 0, "cx alias"),
    "cy": GateSpec(2, 0, "controlled-Y"),
    "cz": GateSpec(2, 0, "controlled-Z"),
    "ch": GateSpec(2, 0, "controlled-H"),
    "csx": GateSpec(2, 0, "controlled-sqrt-X"),
    "cp": GateSpec(2, 1, "cp(theta)"),
    "cu1": GateSpec(2, 1, "cp alias"),
    "crx": GateSpec(2, 1, "crx(theta)"),
    "cry": GateSpec(2, 1, "cry(theta)"),
    "crz": GateSpec(2, 1, "crz(theta)"),
    "cu": GateSpec(2, 4, "cu(theta, phi, lam, gamma)"),
    "cu3": GateSpec(2, 3, "cu3(theta, phi, lam)"),
    "swap": GateSpec(2, 0, "SWAP"),
    "iswap": GateSpec(2, 0, "iSWAP"),
    "dcx": GateSpec(2, 0, "double-CX"),
    "ecr": GateSpec(2, 0, "echoed cross-resonance"),
    "rxx": GateSpec(2, 1, "rxx(theta)"),
    "ryy": GateSpec(2, 1, "ryy(theta)"),
    "rzz": GateSpec(2, 1, "rzz(theta)"),
    "rzx": GateSpec(2, 1, "rzx(theta)"),
}

# --- 12.3 multi-controlled gates --------------------------------------------
_MULTI = {
    "ccx": GateSpec(3, 0, "Toffoli"),
    "toffoli": GateSpec(3, 0, "ccx alias"),
    "ccz": GateSpec(3, 0, "3-qubit controlled-Z"),
    "cswap": GateSpec(3, 0, "controlled-SWAP"),
    "fredkin": GateSpec(3, 0, "cswap alias"),
    "mcx": GateSpec(None, 0, "controls..., target"),
    "mcy": GateSpec(None, 0, "controls..., target"),
    "mcz": GateSpec(None, 0, "phase participants"),
    "mcp": GateSpec(None, 1, "params=[theta]"),
    "mcrx": GateSpec(None, 1, "controls..., target"),
    "mcry": GateSpec(None, 1, "controls..., target"),
    "mcrz": GateSpec(None, 1, "controls..., target"),
}

# --- 12.4 layer / special gates ---------------------------------------------
_SPECIAL = {
    "measure": GateSpec(1, 0, "qubits=[q], clbits=[c]"),
    "reset": GateSpec(None, 0, "reset"),
    "barrier": GateSpec(None, 0, "no-op style"),
    "delay": GateSpec(1, 1, "params=[duration]"),
    "global_phase": GateSpec(0, 1, "params=[theta]"),
}

SUPPORTED_GATES: Dict[str, GateSpec] = {
    **_SINGLE,
    **_TWO,
    **_MULTI,
    **_SPECIAL,
}


def get_spec(name: str) -> Optional[GateSpec]:
    """Return the :class:`GateSpec` for ``name`` or ``None`` if unsupported."""
    return SUPPORTED_GATES.get(name.lower())
