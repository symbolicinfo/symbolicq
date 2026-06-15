# symbolicq 매뉴얼

`symbolicq`는 Symbolic Q cloud simulator REST API를 위한 Python SDK입니다. 기본적으로 `https://q.symbolicinfo.com`을 사용하며, `QuantumCircuit -> SymbolicQBackend.run() -> Job -> Result` workflow를 제공합니다.

## 문서 지도

- [설치와 설정](configuration.ko.md): 설치, 환경 변수, API key, base URL 결정 순서
- [회로 작성](circuits.ko.md): `QuantumCircuit`, gate method, 직렬화, 검증 규칙
- [실행과 결과](jobs-and-results.ko.md): `SymbolicQBackend`, `Job`, `Result`, polling, 취소
- [CSV와 ZIP 포맷](formats.ko.md): API.md CSV/ZIP 요청과 응답 helper
- [저수준 클라이언트 API](client-reference.ko.md): endpoint 단위 `SymbolicQClient` method
- [문제 해결](troubleshooting.ko.md): 일반적인 오류와 점검 항목

## 최소 예제

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

## 핵심 객체

| 객체 | 역할 |
|---|---|
| `QuantumCircuit` | 회로를 만들고 API.md JSON/CSV operation으로 직렬화합니다 |
| `SymbolicQBackend` | 회로를 업로드하고 run을 시작하며 `Job` handle을 반환합니다 |
| `Job` | 상태 조회, polling, 취소, 결과 조회를 제공합니다 |
| `Result` | counts, probabilities, metadata, CSV export/import를 제공합니다 |
| `SymbolicQClient` | REST endpoint를 직접 호출합니다 |

## Bit Order

결과 bitstring은 API.md를 따릅니다: MSB-left, `c[n-1] ... c[0]`. Qubit/classical bit index `0`은 least-significant bit입니다.
