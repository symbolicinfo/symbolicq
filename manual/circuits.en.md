# Circuit Construction

`QuantumCircuit` is a builder that turns the `POST /circuits` JSON body and operation objects from API.md into Python objects.

## Bell Circuit

```python
from symbolicq import QuantumCircuit

qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure(0, 0)
qc.measure(1, 1)
```

`measure_all()` measures each qubit into the classical bit with the same index.

```python
qc = QuantumCircuit(2, 2, name="bell")
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
```

## JSON Serialization

```python
body = qc.to_dict()
```

Expected shape:

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

You can also rebuild a circuit from a server response.

```python
rebuilt = QuantumCircuit.from_dict(server_payload)
```

## CSV Serialization

```python
csv_text = qc.to_csv()
rebuilt = QuantumCircuit.from_csv(csv_text)
```

CSV follows the columns defined in API.md.

```text
name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name
h,0,,,,2,2,bell
cx,0 1,,,,,
measure,0,0,,,,
measure,1,1,,,,
```

## Supported Gates

`symbolicq.SUPPORTED_GATES` follows section 12 of API.md.

```python
from symbolicq import SUPPORTED_GATES

print(SUPPORTED_GATES["h"])
print(SUPPORTED_GATES["cx"])
```

Representative gates with convenience methods:

- Single-qubit: `id`, `x`, `y`, `z`, `h`, `s`, `sdg`, `t`, `tdg`, `sx`, `sxdg`
- Parameterized: `p`, `phase`, `rx`, `ry`, `rz`, `u`, `u1`, `u2`, `u3`
- Controlled/two-qubit: `cx`, `cnot`, `cy`, `cz`, `ch`, `csx`, `cp`, `cu1`, `crx`, `cry`, `crz`, `cu`, `cu3`
- Swap/interaction: `swap`, `iswap`, `dcx`, `ecr`, `rxx`, `ryy`, `rzz`, `rzx`
- Multi-qubit: `ccx`, `toffoli`, `ccz`, `cswap`, `fredkin`, `mcx`, `mcy`, `mcz`, `mcp`, `mcrx`, `mcry`, `mcrz`
- Special: `measure`, `measure_all`, `reset`, `barrier`, `delay`, `global_phase`

## Direct Append

Use `append()` when you do not need a new convenience method or when building circuits dynamically.

```python
qc.append("rx", qubits=0, params=[3.141592])
qc.append("mcp", qubits=[0, 1, 2], params=[0.25])
```

`append()` validates the supported gate name, qubit count, parameter count, and index ranges. If there is a problem, it raises `CircuitValidationError`.

```python
from symbolicq import CircuitValidationError

try:
    qc.append("cx", qubits=[0])
except CircuitValidationError as exc:
    print(exc)
```
