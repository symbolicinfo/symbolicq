# CSV와 ZIP 포맷

Symbolic Q API는 JSON 외에도 CSV와 ZIP 요청/응답을 지원합니다. `symbolicq`는 API.md의 포맷 규칙을 Python helper로 감쌉니다.

## 회로 CSV

```python
from symbolicq import QuantumCircuit

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

csv_text = qc.to_csv()
qc2 = QuantumCircuit.from_csv(csv_text)
```

CSV를 직접 업로드하고 실행:

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend()
job = backend.run_csv(csv_text, shots=1024, seed=7)
```

저수준 client를 사용할 수도 있습니다.

```python
created = backend.client.create_circuit_csv(csv_text)
```

## ZIP 생성

단일 파일을 ZIP으로 만들 때:

```python
from symbolicq import make_zip

zip_bytes = make_zip("circuit.csv", csv_text)
```

회로 JSON을 ZIP으로 만들 때:

```python
from symbolicq import make_circuit_json_zip

zip_bytes = make_circuit_json_zip(qc)
```

회로 CSV를 ZIP으로 만들 때:

```python
from symbolicq import make_circuit_csv_zip

zip_bytes = make_circuit_csv_zip(qc)
```

ZIP을 업로드하고 실행:

```python
job = backend.run_zip(zip_bytes, shots=1024, seed=7)
```

저수준 client:

```python
client.create_circuit_zip(zip_bytes)
client.create_circuit_json_zip(qc.to_dict())
client.create_circuit_csv_zip(qc.to_csv())
```

## ZIP 읽기

```python
from symbolicq import read_zip_members, read_first_zip_text

members = read_zip_members(zip_bytes)
for member in members:
    print(member.filename, member.text())

text = read_first_zip_text(zip_bytes)
```

`read_first_zip_text()`는 `.json`, `.csv` 파일을 우선으로 고르고, 없으면 첫 번째 파일을 읽습니다.

## ZIP 응답 요청

특정 helper:

```python
zip_bytes = client.get_circuit_zip("circuit-id")
zip_bytes = client.get_result_zip("job-id")
```

모든 엔드포인트에 대한 범용 helper:

```python
zip_bytes = client.request_zip("GET", "/health")
```

이 메서드는 `Accept: application/zip`과 `?zip=1`을 자동으로 붙입니다.

## CSV 결과 응답

```python
csv_text = client.get_result_csv("job-id")
result = Result.from_csv(csv_text, job_id="job-id")
```

회로 CSV 조회:

```python
csv_text = client.get_circuit_csv("circuit-id")
qc = QuantumCircuit.from_csv(csv_text)
```
