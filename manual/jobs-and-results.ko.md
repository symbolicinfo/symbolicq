# 실행과 결과

## Backend로 실행

가장 일반적인 실행 경로는 `SymbolicQBackend.run()`입니다.

```python
from symbolicq import QuantumCircuit, SymbolicQBackend

backend = SymbolicQBackend()

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

job = backend.run(qc, shots=1024, seed=7)
```

큰 회로를 보낼 때는 `verbose=True`를 넘기면 `run()`이 JSON 회로 요청을 전송하는 동안 업로드 진행률을 stderr에 출력합니다.

```python
job = backend.run(qc, shots=1024, seed=7, verbose=True)
```

`run()`은 내부에서 다음 순서로 API를 호출합니다.

1. `POST /circuits`
2. `POST /circuits/{circuit_id}/runs`
3. `Job` 객체 반환

이미 업로드된 회로 ID가 있으면 `run_circuit_id()`를 사용할 수 있습니다.

```python
job = backend.run_circuit_id("circuit-id", shots=1024, seed=7)
```

## Job 상태 조회

```python
status = job.status()
print(status["status"])
```

편의 메서드:

```python
job.status_text()       # "queued", "running", "completed", ...
job.progress()          # API progress object
job.progress_ratio()    # float or None
job.done()              # terminal state 여부
```

partial counts 개수를 제한해서 상태를 조회할 수도 있습니다.

```python
status = job.status(counts_limit=8)
```

## 결과 기다리기

```python
result = job.result(timeout=120.0, poll_interval=1.0)
```

`result()`는 terminal state까지 polling합니다. 완료 상태가 아니면 `APIError`를 발생시킵니다. 이미 완료된 job의 결과를 즉시 가져오고 싶으면:

```python
result = job.refresh_result()
```

## 취소

```python
payload = job.cancel()
print(payload)
```

API.md에 따라 queued job은 즉시 cancel될 수 있고, running job은 `cancel_requested=true`로 표시될 수 있습니다.

## Result 사용

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

전체 원본 payload가 필요하면:

```python
payload = result.to_dict()
```

## Result CSV

```python
csv_text = result.to_csv()
result2 = Result.from_csv(csv_text)
```

CSV 형태:

```text
bitstring,count,probability
00,511,0.4990234375
11,513,0.5009765625
```

## 오류 처리

```python
from symbolicq import APIError, JobNotCompleteError

try:
    result = job.refresh_result()
except JobNotCompleteError:
    print("job is not completed yet")
except APIError as exc:
    print(exc.status_code, exc.payload)
```
