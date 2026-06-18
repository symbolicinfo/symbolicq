# Jobs and Results

## Running with Backend

The most common execution path is `SymbolicQBackend.run()`.

```python
from symbolicq import QuantumCircuit, SymbolicQBackend

backend = SymbolicQBackend()

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

job = backend.run(qc, shots=1024, seed=7)
```

For large circuits, pass `verbose=True` to print JSON circuit upload progress while `run()` sends the request.

```python
job = backend.run(qc, shots=1024, seed=7, verbose=True)
```

Internally, `run()` calls the API in this order.

1. `POST /circuits`
2. `POST /circuits/{circuit_id}/runs`
3. Return a `Job` object

If you already have an uploaded circuit ID, use `run_circuit_id()`.

```python
job = backend.run_circuit_id("circuit-id", shots=1024, seed=7)
```

## Checking Job Status

```python
status = job.status()
print(status["status"])
```

Convenience methods:

```python
job.status_text()       # "queued", "running", "completed", ...
job.progress()          # API progress object
job.progress_ratio()    # float or None
job.done()              # whether this is a terminal state
```

You can also limit the number of partial counts returned with the status.

```python
status = job.status(counts_limit=8)
```

## Waiting for Results

```python
result = job.result(timeout=120.0, poll_interval=1.0)
```

`result()` polls until a terminal state. If the job did not complete successfully, it raises `APIError`. To fetch the result of a job that is already complete:

```python
result = job.refresh_result()
```

## Cancellation

```python
payload = job.cancel()
print(payload)
```

According to API.md, queued jobs may be canceled immediately, while running jobs may be marked with `cancel_requested=true`.

## Using Result

```python
counts = result.get_counts()
probabilities = result.get_probabilities()

print(result.count("00"))
print(result.probability("00"))
print(result.most_frequent())
print(result.shots)
print(result.backend_name)
print(result.metadata)
```

If you need the full original payload:

```python
payload = result.to_dict()
```

## Result CSV

```python
csv_text = result.to_csv()
result2 = Result.from_csv(csv_text)
```

CSV shape:

```text
bitstring,count,probability
00,511,0.4990234375
11,513,0.5009765625
```

## Error Handling

```python
from symbolicq import APIError, JobNotCompleteError

try:
    result = job.refresh_result()
except JobNotCompleteError:
    print("job is not completed yet")
except APIError as exc:
    print(exc.status_code, exc.payload)
```
