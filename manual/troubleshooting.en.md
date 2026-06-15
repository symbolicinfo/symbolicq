# Troubleshooting

## Check the Default Server

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend()
print(backend.client.base_url)
```

Expected default:

```text
https://q.symbolicinfo.com
```

If another value appears, check your environment variables.

Bash:

```bash
echo $API_URL
echo $SYMBOLICQ_API_URL
```

PowerShell:

```powershell
$env:API_URL
$env:SYMBOLICQ_API_URL
```

## Check API Key Handling

```python
from symbolicq import SymbolicQClient

client = SymbolicQClient(api_key="secret")
print(client.session.headers["Authorization"])
```

Expected:

```text
Bearer secret
```

## Circuit Validation Errors

`CircuitValidationError` happens before a request is sent. Common causes:

- Unsupported gate name
- Wrong qubit count, for example `cx` with one qubit
- Missing parameters, for example `rx` without theta
- Qubit or clbit index outside the register range
- Calling `measure_all()` when `num_clbits < num_qubits`

Example:

```python
from symbolicq import CircuitValidationError, QuantumCircuit

qc = QuantumCircuit(2)

try:
    qc.cx(0, 2)
except CircuitValidationError as exc:
    print(exc)
```

## Job Result Is Not Ready

`client.get_result()` and `job.refresh_result()` can raise `JobNotCompleteError` when a job is still running.

```python
from symbolicq import JobNotCompleteError

try:
    result = job.refresh_result()
except JobNotCompleteError:
    result = job.result()
```

## Timeout Handling

```python
try:
    result = job.result(timeout=300.0, poll_interval=2.0)
except TimeoutError:
    print(job.status())
```

## CSV Metadata Parsing

The `metadata` column must contain a JSON object string.

Correct:

```text
delay,0,,5.0,"{""unit"": ""ns""}",,,
```

Incorrect:

```text
delay,0,,5.0,unit=ns,,,
```

## Inspect ZIP Responses

```python
from symbolicq import read_zip_members

members = read_zip_members(zip_bytes)
for member in members:
    print(member.filename)
    print(member.text())
```

## Local Verification Commands

```bash
python -m pytest -q
python -m py_compile src/symbolicq/*.py examples/*.py
python -m build
```
