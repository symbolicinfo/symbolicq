# Symbolic Q Flask Server API 규격

## Base URL

https://q.symbolicinfo.com

## Bit Order

Public readout follows Qiskit's convention:

- qubit index `0` is the least-significant computational bit
- classical bit index `0` is the least-significant displayed bit
- count/probability bitstrings are displayed MSB-left as `c[n-1] ... c[0]`
- for a register with classical bits `c3 c2 c1 c0`, the JSON key `"1001"`
  means `c3=1`, `c2=0`, `c1=0`, `c0=1`

## 지원 포맷

요청:
- application/json
- text/csv
- application/zip
- Content-Encoding: zip

응답:
- application/json
- text/csv
- application/zip

ZIP 요청은 `.json` 또는 `.csv` 파일을 1개 이상 포함한 ZIP archive이다. 서버는 archive 안에서 `.json`/`.csv` 파일을 우선 선택한다.
ZIP 응답은 다음 중 하나로 요청한다.

Accept: application/zip

또는

Accept-Encoding: zip

또는

?format=zip

또는

?zip=1

CSV 응답은 다음 중 하나로 요청한다.

Accept: text/csv

또는

?format=csv


## ZIP 통신

### ZIP 요청

회로 생성과 실행 요청 body는 ZIP archive로 보낼 수 있다.

지원 방식:
- `Content-Type: application/zip`
- `Content-Encoding: zip`
- `?format=zip`

ZIP 내부 파일 선택 규칙:
1. `.json` 또는 `.csv` 확장자를 가진 파일을 우선 사용한다.
2. 확장자가 없으면 `X-Zip-Content-Type: application/json` 또는 `X-Zip-Content-Type: text/csv` 힌트를 사용할 수 있다.
3. 기본값은 JSON이다.

안전 제한 기본값:
- `QSIM_API_MAX_ZIP_MEMBERS=16`
- `QSIM_API_MAX_ZIP_UNCOMPRESSED_BYTES=67108864`

### ZIP 응답

모든 정상 JSON/CSV 응답은 ZIP으로 감쌀 수 있다.

요청 방식:
- `Accept: application/zip`
- `Accept-Encoding: zip`
- `?format=zip`
- `?zip=1`

응답 헤더:
- `Content-Type: application/zip`
- `Content-Encoding: zip`
- `X-Zip-Inner-Filename: response.json` 또는 CSV 파일명

### ZIP curl 예제

```bash
zip circuit.zip circuit.json

curl -X POST https://q.symbolicinfo.com/circuits \
  -H "Content-Type: application/zip" \
  --data-binary "@circuit.zip"

curl https://q.symbolicinfo.com/circuits/{circuit_id}?zip=1 \
  -o circuit_response.zip
```

---

# 1. Health Check

## GET /health

### Response JSON

{
  "ok": true,
  "service": "symbolic-q-flask-server"
}


---

# 2. 회로 생성

## POST /circuits

JSON 또는 CSV로 회로를 생성한다.

---

## 2.1 JSON 회로 생성

### Request Headers

Content-Type: application/json

### Request Body

{
  "num_qubits": 2,
  "num_clbits": 2,
  "name": "bell",
  "operations": [
    {
      "name": "h",
      "qubits": [0],
      "clbits": [],
      "params": [],
      "metadata": {}
    },
    {
      "name": "cx",
      "qubits": [0, 1],
      "clbits": [],
      "params": [],
      "metadata": {}
    },
    {
      "name": "measure",
      "qubits": [0],
      "clbits": [0],
      "params": [],
      "metadata": {}
    },
    {
      "name": "measure",
      "qubits": [1],
      "clbits": [1],
      "params": [],
      "metadata": {}
    }
  ]
}

### Field

| field | type | required | description |
|---|---:|---:|---|
| num_qubits | int | yes | 큐비트 수 |
| num_clbits | int | no | 고전 비트 수. 생략 시 num_qubits |
| name | string/null | no | 회로 이름 |
| operations | array | no | 게이트 operation 목록 |
| operations[].name | string | yes | 게이트 이름 |
| operations[].qubits | int[] | no | 큐비트 인덱스 |
| operations[].clbits | int[] | no | 고전 비트 인덱스 |
| operations[].params | array | no | 게이트 파라미터 |
| operations[].metadata | object | no | 추가 메타데이터 |

### Response 201

{
  "circuit_id": "uuid",
  "circuit": {
    "num_qubits": 2,
    "num_clbits": 2,
    "name": "bell",
    "operations": [...]
  }
}


---

## 2.2 CSV 회로 생성

### Request Headers

Content-Type: text/csv

### CSV Columns

name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name

필수 컬럼:
- name

권장 컬럼:
- qubits
- clbits
- params
- metadata

선택 컬럼:
- num_qubits
- num_clbits
- circuit_name

num_qubits, num_clbits, circuit_name은 첫 번째 row에서만 읽는다.

### CSV Example

name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name
h,0,,,,2,2,bell
cx,"0 1",,,,,
measure,0,0,,,,
measure,1,1,,,,

### Simple CSV Example

name,qubits,clbits,params,metadata
h,0,,,
cx,"0 1",,,
measure,0,0,,
measure,1,1,,

### CSV Cell Rules

qubits:
- "0"
- "0 1"
- "0,1"

clbits:
- "0"
- "0 1"
- "0,1"

params:
- "3.141592"
- "0.5 1.0"
- "0.5,1.0"

metadata:
- JSON object string


---

# 3. 회로 조회

## GET /circuits/{circuit_id}

회로를 JSON으로 조회한다.

### Response JSON

{
  "circuit_id": "uuid",
  "circuit": {
    "num_qubits": 2,
    "num_clbits": 2,
    "name": "bell",
    "operations": [
      {
        "name": "h",
        "qubits": [0],
        "clbits": [],
        "params": [],
        "metadata": {}
      }
    ]
  }
}


---

## GET /circuits/{circuit_id}?format=csv

또는

Accept: text/csv

### Response CSV

name,qubits,clbits,params,metadata
h,0,,,
cx,0 1,,,
measure,0,0,,
measure,1,1,,


---

# 4. 회로 삭제

## DELETE /circuits/{circuit_id}

### Response JSON

{
  "circuit_id": "uuid",
  "deleted": true
}


---

# 5. 회로 실행

## POST /circuits/{circuit_id}/runs

회로 실행 job을 생성한다.

### Request Headers

Content-Type: application/json

### Request Body

{
  "shots": 1024,
  "seed": 7,
  "simulator_options": {
    "measurement_uses_density": true,
    "settle_after_instruction": true
  }
}

### Field

| field | type | required | default |
|---|---:|---:|---:|
| shots | int | no | 1024 |
| seed | int/null | no | null |
| seed_simulator | int/null | no | null |
| simulator_options | object | no | {} |
| simulator_options.measurement_uses_density | bool | no | default |
| simulator_options.settle_after_instruction | bool | no | default |

### Response 202

{
  "job_id": "uuid",
  "status": "queued"
}


---

# 6. 실행 현황 조회

## GET /runs/{job_id}/status

Optional query:

| query | type | default | description |
|---|---:|---:|---|
| counts_limit | int | 16 | Maximum number of partial count entries returned in `sampling_progress.counts_partial`. `partial_counts_limit` is also accepted. |

### Response JSON

{
  "job_id": "uuid",
  "circuit_id": "uuid",
  "status": "queued | running | completed | failed | cancelled",
  "shots": 1024,
  "shots_completed": 37,
  "shots_remaining": 987,
  "seed": 7,
  "created_at": 1781010000.0,
  "started_at": 1781010001.0,
  "finished_at": null,
  "cancel_requested": false,
  "progress": {
    "stage": "queued | compiling | lowering | sampling | aggregating | completed",
    "unit": "shots",
    "completed": 37,
    "total": 1024,
    "ratio": 0.0361328125,
    "message": "sampling shot 37/1024"
  },
  "timing": {
    "created_at": 1781010000.0,
    "started_at": 1781010001.0,
    "finished_at": null,
    "elapsed_seconds": 42.3,
    "queue_elapsed_seconds": 1.0,
    "run_elapsed_seconds": 41.3
  },
  "compiler_progress": {
    "enabled": true,
    "stage": "gate_cancel",
    "passes_total": 9,
    "passes_completed": 4,
    "before_ops": 286624,
    "current_ops": 120003,
    "after_ops": null
  },
  "sampling_progress": {
    "shots_total": 1024,
    "shots_completed": 37,
    "shots_failed": 0,
    "current_shot": 38,
    "counts_partial": {
      "0101": 3
    }
  },
  "backend_progress": {
    "backend": "qsim.api.Simulator[SUnitBackend]",
    "stage": "dynamics_apply",
    "operation_index": 12400,
    "operation_total": 286624,
    "lowered_primitives_completed": null,
    "lowered_primitives_total": null
  },
  "heartbeat_at": 1781010042.3,
  "trace_enabled": false,
  "error": null
}

Progress notes:
- Existing fields are preserved. New progress fields are optional additions.
- Unknown values are returned as `null` or omitted; the server does not synthesize ETA.
- `progress.ratio` is non-null only when `completed` and `total` are known and `total > 0`.
- `counts_partial` is bounded by `counts_limit` and never includes statevectors or large logs.


---

# 7. 실행 결과 조회

## GET /runs/{job_id}/result

완료된 job의 결과를 조회한다.

### Response JSON

{
  "job_id": "uuid",
  "status": "completed",
  "result": {
    "counts": {
      "00": 511,
      "11": 513
    },
    "probabilities": {
      "00": 0.5,
      "11": 0.5
    },
    "shots": 1024,
    "metadata": {
      "backend": "qsim.api.Simulator[SUnitBackend]",
      "statevector_used": false,
      "seed": 7,
      "lowered_primitives": 4,
      "backend_instructions": 4,
      "progress": {
        "progress": {
          "stage": "completed",
          "unit": "shots",
          "completed": 1024,
          "total": 1024,
          "ratio": 1.0,
          "message": "completed"
        },
        "compiler_progress": {},
        "sampling_progress": {},
        "backend_progress": {},
        "heartbeat_at": 1781010042.3,
        "timing": {}
      }
    }
  }
}

### Not Completed Response 409

{
  "job_id": "uuid",
  "circuit_id": "uuid",
  "status": "running",
  "shots": 1024,
  "seed": 7,
  "created_at": 1781010000.0,
  "started_at": 1781010001.0,
  "finished_at": null,
  "cancel_requested": false,
  "error": null
}


---

## GET /runs/{job_id}/result?format=csv

또는

Accept: text/csv

### Response CSV

bitstring,count,probability
00,511,0.5
11,513,0.5


---

# 8. 실행 중지

## POST /runs/{job_id}/cancel

### Response JSON

{
  "job_id": "uuid",
  "circuit_id": "uuid",
  "status": "cancelled | queued | running | completed | failed",
  "shots": 1024,
  "seed": 7,
  "created_at": 1781010000.0,
  "started_at": null,
  "finished_at": 1781010001.0,
  "cancel_requested": true,
  "error": null
}

주의:
- queued 상태 job은 즉시 cancel 가능.
- 이미 running 상태인 job은 cancel_requested=true로 표시된다.
- 현재 Symbolic Q Simulator.run 내부에 cooperative cancel token이 없으므로 running job의 즉시 강제 중단은 보장되지 않는다.


---

# 9. 회로 목록 조회

## GET /circuits

### Response JSON

{
  "circuits": [
    {
      "circuit_id": "uuid",
      "num_qubits": 2,
      "num_clbits": 2,
      "operations": 4,
      "name": "bell",
      "created_at": 1781010000.0,
      "updated_at": 1781010000.0
    }
  ]
}


---

# 10. 실행 목록 조회

## GET /runs

### Response JSON

{
  "runs": [
    {
      "job_id": "uuid",
      "circuit_id": "uuid",
      "status": "completed",
      "shots": 1024,
      "seed": 7,
      "created_at": 1781010000.0,
      "started_at": 1781010001.0,
      "finished_at": 1781010002.0,
      "cancel_requested": false,
      "error": null
    }
  ]
}


---

# 11. Operation JSON 규격

## 공통 Operation Object

{
  "name": "gate_name",
  "qubits": [0, 1],
  "clbits": [],
  "params": [3.141592],
  "metadata": {}
}

## 공통 규칙

- name은 소문자 게이트 이름 권장.
- qubits는 0-based index.
- clbits는 0-based index.
- params는 각도/파라미터 배열.
- metadata는 선택 사항.
- 지원되지 않는 게이트는 실행 시 lowering 단계에서 에러가 난다.


---

# 12. 지원 게이트 전체 목록

Symbolic Q lowering 계층의 supported_gates 기준 전체 목록은 다음과 같다. :contentReference[oaicite:1]{index=1}

## 12.1 단일 큐비트 게이트

| name | qubits | params | alias / note |
|---|---:|---:|---|
| id | 1 | 0 | identity |
| i | 1 | 0 | id alias |
| x | 1 | 0 | Pauli-X |
| y | 1 | 0 | Pauli-Y |
| z | 1 | 0 | Pauli-Z |
| h | 1 | 0 | Hadamard |
| s | 1 | 0 | S |
| sdg | 1 | 0 | S dagger |
| t | 1 | 0 | T |
| tdg | 1 | 0 | T dagger |
| sx | 1 | 0 | sqrt-X |
| sxdg | 1 | 0 | sqrt-X dagger |
| p | 1 | 1 | phase(theta) |
| phase | 1 | 1 | p alias at API builder level |
| rx | 1 | 1 | rx(theta) |
| ry | 1 | 1 | ry(theta) |
| rz | 1 | 1 | rz(theta) |
| u | 1 | 3 | u(theta, phi, lam) |
| u1 | 1 | 1 | p(lam) alias |
| u2 | 1 | 2 | u2(phi, lam) |
| u3 | 1 | 3 | u alias |

## 12.2 2큐비트 / 제어 게이트

| name | qubits | params | alias / note |
|---|---:|---:|---|
| cx | 2 | 0 | CNOT |
| cnot | 2 | 0 | cx alias |
| cy | 2 | 0 | controlled-Y |
| cz | 2 | 0 | controlled-Z |
| ch | 2 | 0 | controlled-H |
| csx | 2 | 0 | controlled-sqrt-X |
| cp | 2 | 1 | cp(theta) |
| cu1 | 2 | 1 | cp alias |
| crx | 2 | 1 | crx(theta) |
| cry | 2 | 1 | cry(theta) |
| crz | 2 | 1 | crz(theta) |
| cu | 2 | 4 | cu(theta, phi, lam, gamma) |
| cu3 | 2 | 3 | cu3(theta, phi, lam) |
| swap | 2 | 0 | SWAP |
| iswap | 2 | 0 | iSWAP |
| dcx | 2 | 0 | double-CX: `cx(q0, q1)` followed by `cx(q1, q0)`, matching Qiskit operand order |
| ecr | 2 | 0 | echoed cross-resonance |
| rxx | 2 | 1 | rxx(theta) |
| ryy | 2 | 1 | ryy(theta) |
| rzz | 2 | 1 | rzz(theta) |
| rzx | 2 | 1 | rzx(theta) |

## 12.3 다중 제어 게이트

| name | qubits | params | note |
|---|---:|---:|---|
| ccx | 3 | 0 | Toffoli |
| toffoli | 3 | 0 | ccx alias |
| ccz | 3 | 0 | 3-qubit controlled-Z style |
| cswap | 3 | 0 | controlled-SWAP |
| fredkin | 3 | 0 | cswap alias |
| mcx | n | 0 | qubits = controls..., target |
| mcy | n | 0 | qubits = controls..., target |
| mcz | n | 0 | qubits = all controlled phase participants |
| mcp | n | 1 | params = [theta], qubits = all phase participants |
| mcrx | n | 1 | qubits = controls..., target |
| mcry | n | 1 | qubits = controls..., target |
| mcrz | n | 1 | qubits = controls..., target |

## 12.4 레이어 / 특수 게이트

| name | qubits | params | note |
|---|---:|---:|---|
| measure | 1 | 0 | qubits=[q], clbits=[c] |
| reset | 1 또는 n | 0 | reset |
| barrier | n | 0 | metadata/no-op style |
| delay | 1 | 1 | params=[duration], metadata={"unit":"..."} |
| global_phase | 0 | 1 | params=[theta] |


---

# 13. JSON 예제

## Bell 회로 생성

POST /circuits

{
  "num_qubits": 2,
  "num_clbits": 2,
  "name": "bell",
  "operations": [
    {"name": "h", "qubits": [0]},
    {"name": "cx", "qubits": [0, 1]},
    {"name": "measure", "qubits": [0], "clbits": [0]},
    {"name": "measure", "qubits": [1], "clbits": [1]}
  ]
}

## 실행

POST /circuits/{circuit_id}/runs

{
  "shots": 1024,
  "seed": 7
}

## 결과

GET /runs/{job_id}/result


---

# 14. CSV 예제

## bell.csv

name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name
h,0,,,,2,2,bell
cx,"0 1",,,,,
measure,0,0,,,,
measure,1,1,,,,

## 생성

curl -X POST https://q.symbolicinfo.com/circuits \
  -H "Content-Type: text/csv" \
  --data-binary "@bell.csv"

## CSV 결과 조회

curl https://q.symbolicinfo.com/runs/{job_id}/result \
  -H "Accept: text/csv"


---

# 15. 에러 응답

## 400 Bad Request

{
  "error": "missing required field: num_qubits"
}

## 404 Not Found

{
  "error": "circuit not found"
}

또는

{
  "error": "job not found"
}

## 409 Conflict

job이 아직 completed가 아닐 때 result 조회.

{
  "job_id": "uuid",
  "status": "running",
  "error": null
}
