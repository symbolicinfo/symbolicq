# 문제 해결

## 기본 서버 확인

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend()
print(backend.client.base_url)
```

예상 기본값:

```text
https://q.symbolicinfo.com
```

다른 값이 보이면 환경 변수를 확인하세요.

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

## API Key 처리 확인

```python
from symbolicq import SymbolicQClient

client = SymbolicQClient(api_key="secret")
print(client.session.headers["Authorization"])
```

예상값:

```text
Bearer secret
```

## 회로 검증 오류

`CircuitValidationError`는 request가 전송되기 전에 발생합니다. 흔한 원인:

- 지원하지 않는 gate 이름
- 잘못된 qubit 수. 예: qubit 하나로 `cx` 호출
- 누락된 parameter. 예: theta 없이 `rx` 호출
- register 범위를 벗어난 qubit 또는 clbit index
- `num_clbits < num_qubits`인 상태에서 `measure_all()` 호출

예:

```python
from symbolicq import CircuitValidationError, QuantumCircuit

qc = QuantumCircuit(2)

try:
    qc.cx(0, 2)
except CircuitValidationError as exc:
    print(exc)
```

## Job 결과가 아직 준비되지 않음

job이 아직 실행 중이면 `client.get_result()`와 `job.refresh_result()`가 `JobNotCompleteError`를 발생시킬 수 있습니다.

```python
from symbolicq import JobNotCompleteError

try:
    result = job.refresh_result()
except JobNotCompleteError:
    result = job.result()
```

## Timeout 처리

```python
try:
    result = job.result(timeout=300.0, poll_interval=2.0)
except TimeoutError:
    print(job.status())
```

## CSV Metadata Parsing

`metadata` column은 JSON object string이어야 합니다.

올바른 예:

```text
delay,0,,5.0,"{""unit"": ""ns""}",,,
```

잘못된 예:

```text
delay,0,,5.0,unit=ns,,,
```

## ZIP 응답 검사

```python
from symbolicq import read_zip_members

members = read_zip_members(zip_bytes)
for member in members:
    print(member.filename)
    print(member.text())
```

## 로컬 검증 명령

```bash
python -m pytest -q
python -m py_compile src/symbolicq/*.py examples/*.py
python -m build
```
