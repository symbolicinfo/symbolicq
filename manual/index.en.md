# symbolicq Manual

`symbolicq` is a Python SDK for the Symbolic Q cloud simulator REST API. It uses `https://q.symbolicinfo.com` by default and exposes the workflow `QuantumCircuit -> SymbolicQBackend.run() -> Job -> Result`.

## Documentation Map

- [Installation and configuration](configuration.en.md): install, environment variables, API key, base URL resolution
- [Circuit construction](circuits.en.md): `QuantumCircuit`, gate methods, serialization, validation rules
- [Jobs and results](jobs-and-results.en.md): `SymbolicQBackend`, `Job`, `Result`, polling, cancellation
- [CSV and ZIP formats](formats.en.md): API.md CSV/ZIP request and response helpers
- [Low-level client API](client-reference.en.md): endpoint-level `SymbolicQClient` methods
- [Troubleshooting](troubleshooting.en.md): common errors and checks

## Minimal Example

```python
from symbolicq import QuantumCircuit, SymbolicQBackend

backend = SymbolicQBackend()

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

job = backend.run(qc, shots=1024, seed=7)
result = job.result()

print(result.get_counts())
print(result.get_probabilities())
```

## Core Objects

| Object | Role |
|---|---|
| `QuantumCircuit` | Builds circuits and serializes them to API.md JSON/CSV operations |
| `SymbolicQBackend` | Uploads circuits, starts runs, and returns `Job` handles |
| `Job` | Reads status, polls, cancels, and retrieves results |
| `Result` | Exposes counts, probabilities, metadata, and CSV export/import |
| `SymbolicQClient` | Calls REST endpoints directly |

## Bit Order

Result bitstrings follow API.md: MSB-left, `c[n-1] ... c[0]`. Qubit/classical bit index `0` is the least-significant bit.
