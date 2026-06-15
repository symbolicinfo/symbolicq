# 회로 작성

`QuantumCircuit`은 API.md의 `POST /circuits` JSON body와 operation object를 Python 객체로 만드는 빌더입니다.

## Bell 회로

```python
from symbolicq import QuantumCircuit

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure(0, 0)
qc.measure(1, 1)
```

`measure_all()`은 같은 index의 qubit을 같은 index의 classical bit으로 측정합니다.

```python
qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
```

## JSON 직렬화

```python
body = qc.to_dict()
```

예상 형태:

```python
{
    "num_qubits": 2,
    "num_clbits": 2,
    "name": "bell",
    "operations": [
        {"name": "h", "qubits": [0], "clbits": [], "params": [], "metadata": {}},
        {"name": "cx", "qubits": [0, 1], "clbits": [], "params": [], "metadata": {}},
    ],
}
```

서버 응답에서 다시 만들 수도 있습니다.

```python
rebuilt = QuantumCircuit.from_dict(server_payload)
```

## CSV 직렬화

```python
csv_text = qc.to_csv()
rebuilt = QuantumCircuit.from_csv(csv_text)
```

CSV는 API.md의 columns를 따릅니다.

```text
name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name
h,0,,,,2,2,bell
cx,0 1,,,,,
measure,0,0,,,,
measure,1,1,,,,
```

## 지원 게이트

`symbolicq.SUPPORTED_GATES`는 API.md section 12를 따릅니다.

```python
from symbolicq import SUPPORTED_GATES

print(SUPPORTED_GATES["h"])
print(SUPPORTED_GATES["cx"])
```

편의 메서드가 제공되는 대표 게이트:

- Single-qubit: `id`, `x`, `y`, `z`, `h`, `s`, `sdg`, `t`, `tdg`, `sx`, `sxdg`
- Parameterized: `p`, `phase`, `rx`, `ry`, `rz`, `u`, `u1`, `u2`, `u3`
- Controlled/two-qubit: `cx`, `cnot`, `cy`, `cz`, `ch`, `csx`, `cp`, `cu1`, `crx`, `cry`, `crz`, `cu`, `cu3`
- Swap/interaction: `swap`, `iswap`, `dcx`, `ecr`, `rxx`, `ryy`, `rzz`, `rzx`
- Multi-qubit: `ccx`, `toffoli`, `ccz`, `cswap`, `fredkin`, `mcx`, `mcy`, `mcz`, `mcp`, `mcrx`, `mcry`, `mcrz`
- Special: `measure`, `measure_all`, `reset`, `barrier`, `delay`, `global_phase`

## 직접 append

새 편의 메서드가 필요 없거나 동적으로 회로를 만들 때는 `append()`를 쓰면 됩니다.

```python
qc.append("rx", qubits=0, params=[3.141592])
qc.append("mcp", qubits=[0, 1, 2], params=[0.25])
```

`append()`는 지원 게이트 이름, qubit 수, parameter 수, index 범위를 검증합니다. 문제가 있으면 `CircuitValidationError`가 발생합니다.

```python
from symbolicq import CircuitValidationError

try:
    qc.append("cx", qubits=[0])
except CircuitValidationError as exc:
    print(exc)
```
