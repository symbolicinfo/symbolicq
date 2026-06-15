# 저수준 클라이언트 API

`SymbolicQClient`는 API.md의 REST endpoint를 직접 호출하는 얇은 wrapper입니다. 고수준 실행은 `SymbolicQBackend`를 쓰고, 세밀한 제어가 필요하면 client를 직접 사용합니다.

## 생성

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

호출 endpoint:

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

CSV/ZIP 결과:

```python
client.get_result_csv("job-id")
client.get_result_zip("job-id")
```

## 범용 ZIP 응답

```python
zip_bytes = client.request_zip("GET", "/health")
```

`request_zip()`은 임의 endpoint에 `Accept: application/zip`과 `?zip=1`을 붙입니다.

## 오류 모델

네트워크 오류나 HTTP 오류는 `APIError`로 감쌉니다.

```python
from symbolicq import APIError

try:
    client.get_circuit("missing")
except APIError as exc:
    print(exc.status_code)
    print(exc.payload)
```

`GET /runs/{job_id}/result`가 HTTP 409를 반환하면 `JobNotCompleteError`가 발생합니다.

```python
from symbolicq import JobNotCompleteError

try:
    client.get_result("running-job")
except JobNotCompleteError:
    print("not completed")
```
