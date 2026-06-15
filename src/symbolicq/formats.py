"""Helpers for API.md CSV and ZIP wire formats."""

from __future__ import annotations

import io
import json
import zipfile
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Union

from .circuit import QuantumCircuit


class ZipMember(NamedTuple):
    """A file contained in an API ZIP response or request body."""

    filename: str
    data: bytes

    def text(self, encoding: str = "utf-8") -> str:
        return self.data.decode(encoding)


CircuitBody = Union[QuantumCircuit, Dict[str, Any]]


def make_zip(filename: str, content: Union[str, bytes]) -> bytes:
    """Return ZIP bytes containing one file."""
    data = content.encode("utf-8") if isinstance(content, str) else bytes(content)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(filename, data)
    return buffer.getvalue()


def make_circuit_json_zip(
    circuit: CircuitBody, filename: str = "circuit.json"
) -> bytes:
    """Serialize a circuit body as JSON inside a ZIP archive."""
    body = circuit.to_dict() if isinstance(circuit, QuantumCircuit) else circuit
    return make_zip(filename, json.dumps(body))


def make_circuit_csv_zip(
    circuit: Union[QuantumCircuit, str], filename: str = "circuit.csv"
) -> bytes:
    """Serialize a circuit CSV body inside a ZIP archive."""
    csv_text = circuit.to_csv() if isinstance(circuit, QuantumCircuit) else circuit
    return make_zip(filename, csv_text)


def read_zip_members(zip_bytes: bytes) -> List[ZipMember]:
    """Read all non-directory ZIP members in archive order."""
    members: List[ZipMember] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            members.append(ZipMember(info.filename, archive.read(info)))
    return members


def read_first_zip_member(
    zip_bytes: bytes, preferred_extensions: Sequence[str] = (".json", ".csv")
) -> Optional[ZipMember]:
    """Return the first preferred member, or the first file if none match."""
    members = read_zip_members(zip_bytes)
    for extension in preferred_extensions:
        for member in members:
            if member.filename.lower().endswith(extension.lower()):
                return member
    return members[0] if members else None


def read_first_zip_text(
    zip_bytes: bytes,
    preferred_extensions: Sequence[str] = (".json", ".csv"),
    encoding: str = "utf-8",
) -> Optional[str]:
    """Return decoded text for the selected ZIP member."""
    member = read_first_zip_member(zip_bytes, preferred_extensions)
    return None if member is None else member.text(encoding)
