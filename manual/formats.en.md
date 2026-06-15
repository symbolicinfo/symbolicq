# CSV and ZIP Formats

In addition to JSON, the Symbolic Q API supports CSV and ZIP requests and responses. `symbolicq` wraps the format rules from API.md with Python helpers.

## Circuit CSV

```python
from symbolicq import QuantumCircuit

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

csv_text = qc.to_csv()
qc2 = QuantumCircuit.from_csv(csv_text)
```

Upload CSV directly and run it:

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend()
job = backend.run_csv(csv_text, shots=1024, seed=7)
```

You can also use the low-level client.

```python
created = backend.client.create_circuit_csv(csv_text)
```

## Creating ZIP Files

Create a ZIP from a single file:

```python
from symbolicq import make_zip

zip_bytes = make_zip("circuit.csv", csv_text)
```

Create a ZIP from circuit JSON:

```python
from symbolicq import make_circuit_json_zip

zip_bytes = make_circuit_json_zip(qc)
```

Create a ZIP from circuit CSV:

```python
from symbolicq import make_circuit_csv_zip

zip_bytes = make_circuit_csv_zip(qc)
```

Upload and run a ZIP:

```python
job = backend.run_zip(zip_bytes, shots=1024, seed=7)
```

Low-level client:

```python
client.create_circuit_zip(zip_bytes)
client.create_circuit_json_zip(qc.to_dict())
client.create_circuit_csv_zip(qc.to_csv())
```

## Reading ZIP Files

```python
from symbolicq import read_zip_members, read_first_zip_text

members = read_zip_members(zip_bytes)
for member in members:
    print(member.filename, member.text())

text = read_first_zip_text(zip_bytes)
```

`read_first_zip_text()` prefers `.json` and `.csv` files. If none exist, it reads the first file.

## Requesting ZIP Responses

Specific helpers:

```python
zip_bytes = client.get_circuit_zip("circuit-id")
zip_bytes = client.get_result_zip("job-id")
```

Generic helper for any endpoint:

```python
zip_bytes = client.request_zip("GET", "/health")
```

This method automatically adds `Accept: application/zip` and `?zip=1`.

## CSV Result Responses

```python
csv_text = client.get_result_csv("job-id")
result = Result.from_csv(csv_text, job_id="job-id")
```

Retrieve circuit CSV:

```python
csv_text = client.get_circuit_csv("circuit-id")
qc = QuantumCircuit.from_csv(csv_text)
```
