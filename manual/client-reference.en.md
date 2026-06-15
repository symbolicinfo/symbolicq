# Low-Level Client API

`SymbolicQClient` is a thin wrapper that directly calls the REST endpoints from API.md. Use `SymbolicQBackend` for high-level execution, and use the client directly when you need finer control.

## Creation

```python
from symbolicq import SymbolicQClient

client = SymbolicQClient(
    base_url="https://q.symbolicinfo.com",
    api_key=None,
    timeout=30.0,
)
```

## Health

```python
client.health()
```

Called endpoint:

```text
GET /health
```

## Circuits

```python
created = client.create_circuit(qc.to_dict())
circuit = client.get_circuit(created["circuit_id"])
circuits = client.list_circuits()
deleted = client.delete_circuit(created["circuit_id"])
```

CSV/ZIP:

```python
client.create_circuit_csv(qc.to_csv())
client.create_circuit_zip(zip_bytes)
client.create_circuit_json_zip(qc.to_dict())
client.create_circuit_csv_zip(qc.to_csv())
client.get_circuit_csv("circuit-id")
client.get_circuit_zip("circuit-id")
```

## Runs

```python
run = client.create_run(
    circuit_id="circuit-id",
    shots=1024,
    seed=7,
    simulator_options={
        "measurement_uses_density": True,
        "settle_after_instruction": True,
    },
)

status = client.get_status(run["job_id"], counts_limit=16)
result = client.get_result(run["job_id"])
cancelled = client.cancel_run(run["job_id"])
runs = client.list_runs()
```

CSV/ZIP results:

```python
client.get_result_csv("job-id")
client.get_result_zip("job-id")
```

## Generic ZIP Responses

```python
zip_bytes = client.request_zip("GET", "/health")
```

`request_zip()` adds `Accept: application/zip` and `?zip=1` to any endpoint.

## Error Model

Network errors and HTTP errors are wrapped as `APIError`.

```python
from symbolicq import APIError

try:
    client.get_circuit("missing")
except APIError as exc:
    print(exc.status_code)
    print(exc.payload)
```

If `GET /runs/{job_id}/result` returns HTTP 409, `JobNotCompleteError` is raised.

```python
from symbolicq import JobNotCompleteError

try:
    client.get_result("running-job")
except JobNotCompleteError:
    print("not completed")
```
