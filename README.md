# Symbolic Q API Wrapper

A dependency-light Python client for the **Symbolic Q** cloud simulator REST API
(`https://q.symbolicinfo.com`). It exposes a familiar
`backend.run(circuit) -> job -> result.get_counts()` workflow while talking to the
HTTP API documented in [`API.md`](API.md).

- Build circuits with a concise gate-method API (`qc.h(0)`, `qc.cx(0, 1)`, ...)
- Submit and poll runs asynchronously (`job.result()`, `job.status()`, `job.cancel()`)
- Local validation against the full supported-gate set (API.md section 12)
- JSON, CSV, and ZIP request/response helpers for the documented API formats
- Runtime dependency: `requests`

An API key is required for normal use. Create one at `https://q.symbolicinfo.com`
and provide it with `api_key=...` or the `SYMBOLICQ_API_KEY` / `API_KEY`
environment variable.

## Install

```bash
pip install symbolicq
```

From source:

```bash
pip install -e .[dev]
```

## Quick Start

```python
from symbolicq import QuantumCircuit, SymbolicQBackend

backend = SymbolicQBackend(api_key="your-api-key")

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

job = backend.run(qc, shots=1024, seed=7)
result = job.result()                  # blocks until the job completes

print(result.get_counts())             # {'00': 511, '11': 513}
print(result.get_probabilities())      # {'00': 0.5, '11': 0.5}
print(result.most_frequent())          # '11'
```

## Manual

Start with [manual/index.md](manual/index.md) for the full documentation.

- [Installation and configuration](manual/configuration.md)
- [Circuit construction](manual/circuits.md)
- [Jobs and results](manual/jobs-and-results.md)
- [CSV and ZIP formats](manual/formats.md)
- [Low-level client API](manual/client-reference.md)
- [Troubleshooting](manual/troubleshooting.md)

### Bit Order

Bitstrings follow the API convention: MSB-left `c[n-1] ... c[0]`, where qubit/clbit
index `0` is the least-significant bit. See API.md "Bit Order".

## Configuration

Get an API key from `https://q.symbolicinfo.com` before running jobs.

`base_url` and `api_key` are resolved in this order, first non-empty value wins:

1. Explicit argument
2. `SYMBOLICQ_API_URL` / `SYMBOLICQ_API_KEY` from environment variables
3. `API_URL` / `API_KEY` from environment variables
4. Built-in default URL (`https://q.symbolicinfo.com`) for `base_url`

The API key is required and is sent on every request as
`Authorization: Bearer {API_KEY}`.

### Environment Variables

```bash
export API_URL=https://q.symbolicinfo.com
export API_KEY=your-api-key
```

PowerShell:

```powershell
$env:API_URL = "https://q.symbolicinfo.com"
$env:API_KEY = "your-api-key"
```

```python
backend = SymbolicQBackend()   # picks up API_URL / API_KEY from env
```

### Explicit Override

```python
backend = SymbolicQBackend(
    base_url="https://q.symbolicinfo.com",
    api_key="your-api-key",
    timeout=60.0,
)
```

## Lower-Level Client

Every JSON REST endpoint is available directly on `SymbolicQClient`:

```python
from symbolicq import SymbolicQClient

client = SymbolicQClient()
client.health()
created = client.create_circuit(qc.to_dict())
run = client.create_run(created["circuit_id"], shots=1024, seed=7)
client.get_status(run["job_id"])
client.get_result(run["job_id"])
client.list_circuits()
client.list_runs()
```

`Job` exposes raw API payloads plus small convenience helpers:

```python
job.status()            # raw GET /runs/{job_id}/status payload
job.status_text()       # e.g. "queued", "running", "completed"
job.progress()          # progress object when the server reports it
job.progress_ratio()    # float or None
job.refresh_result()    # immediate GET /runs/{job_id}/result
```

CSV and ZIP helpers are also available for API.md's alternate wire formats:

```python
client.create_circuit_csv(qc.to_csv())
client.get_circuit_csv("circuit-id")
client.get_result_csv("job-id")

client.create_circuit_json_zip(qc.to_dict())
client.create_circuit_csv_zip(qc.to_csv())
client.create_circuit_zip(zip_bytes, inner_content_type="application/json")
client.get_circuit_zip("circuit-id")
client.get_result_zip("job-id")
client.request_zip("GET", "/health")  # generic ZIP response helper
```

Circuits can be round-tripped through the documented CSV circuit format:

```python
csv_text = qc.to_csv()
qc2 = QuantumCircuit.from_csv(csv_text)
```

CSV or ZIP circuit payloads can also be submitted through the backend:

```python
job = backend.run_csv(qc.to_csv(), shots=1024)
job = backend.run_zip(make_circuit_json_zip(qc), shots=1024)
```

Completed results can be exported as the documented result CSV:

```python
from symbolicq import Result

csv_text = result.to_csv()
result2 = Result.from_csv(csv_text)
```

ZIP utilities are exported for local packing and unpacking:

```python
from symbolicq import make_circuit_json_zip, read_first_zip_text

zip_bytes = make_circuit_json_zip(qc)
text = read_first_zip_text(zip_bytes)
```

## Simulator Options

```python
backend.run(
    qc,
    shots=1024,
    seed=7,
    simulator_options={
        "measurement_uses_density": True,
        "settle_after_instruction": True,
    },
)
```

## Supported Gates

`symbolicq.SUPPORTED_GATES` mirrors API.md section 12: single-qubit,
two-qubit/controlled, multi-controlled, and special gates such as `measure`,
`reset`, `barrier`, `delay`, and `global_phase`.

All supported gates can be emitted through either convenience methods or
`QuantumCircuit.append(...)`. Unsupported gates and invalid qubit, clbit, or
parameter counts are rejected locally before the request is sent.

## Development

```bash
pip install -e .[dev]
pytest
```

Examples:

```bash
python examples/bell.py
python examples/csv_and_zip.py
```

## License

MIT
