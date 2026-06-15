import pytest

from symbolicq import QuantumCircuit
from symbolicq.exceptions import CircuitValidationError


def test_bell_circuit_to_dict():
    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)

    d = qc.to_dict()
    assert d["num_qubits"] == 2
    assert d["num_clbits"] == 2
    assert d["name"] == "bell"
    names = [op["name"] for op in d["operations"]]
    assert names == ["h", "cx", "measure", "measure"]
    assert d["operations"][1]["qubits"] == [0, 1]


def test_default_num_clbits_equals_num_qubits():
    qc = QuantumCircuit(3)
    assert qc.num_clbits == 3


def test_measure_all():
    qc = QuantumCircuit(2, 2)
    qc.measure_all()
    assert [op.name for op in qc.operations] == ["measure", "measure"]
    assert qc.operations[1].qubits == [1]
    assert qc.operations[1].clbits == [1]


def test_param_gate():
    qc = QuantumCircuit(1)
    qc.rx(3.14, 0)
    assert qc.operations[0].name == "rx"
    assert qc.operations[0].params == [3.14]


def test_all_supported_gate_methods_emit_expected_operations():
    qc = QuantumCircuit(5)
    qc.id(0).x(0).y(0).z(0).h(0).s(0).sdg(0).t(0).tdg(0).sx(0).sxdg(0)
    qc.p(0.1, 0).phase(0.2, 0).rx(0.3, 0).ry(0.4, 0).rz(0.5, 0)
    qc.u(0.1, 0.2, 0.3, 0).u1(0.4, 0).u2(0.5, 0.6, 0).u3(0.7, 0.8, 0.9, 0)
    qc.cx(0, 1).cnot(0, 1).cy(0, 1).cz(0, 1).ch(0, 1).csx(0, 1)
    qc.cp(0.1, 0, 1).cu1(0.2, 0, 1).crx(0.3, 0, 1).cry(0.4, 0, 1)
    qc.crz(0.5, 0, 1).cu(0.1, 0.2, 0.3, 0.4, 0, 1).cu3(0.1, 0.2, 0.3, 0, 1)
    qc.swap(0, 1).iswap(0, 1).dcx(0, 1).ecr(0, 1)
    qc.rxx(0.1, 0, 1).ryy(0.2, 0, 1).rzz(0.3, 0, 1).rzx(0.4, 0, 1)
    qc.ccx(0, 1, 2).toffoli(0, 1, 2).ccz(0, 1, 2).cswap(0, 1, 2).fredkin(0, 1, 2)
    qc.mcx([0, 1], 2).mcy([0, 1], 2).mcz([0, 1, 2]).mcp(0.1, [0, 1, 2])
    qc.mcrx(0.2, [0, 1], 2).mcry(0.3, [0, 1], 2).mcrz(0.4, [0, 1], 2)
    qc.reset([0, 1]).barrier([0, 1]).delay(5, 0, unit="ns").global_phase(0.25)

    names = [op.name for op in qc.operations]
    assert "phase" in names
    assert "cu" in names
    assert "mcrz" in names
    assert names[-1] == "global_phase"
    assert qc.operations[-1].qubits == []
    assert qc.operations[-1].params == [0.25]


def test_unsupported_gate_rejected():
    qc = QuantumCircuit(1)
    with pytest.raises(CircuitValidationError):
        qc.append("not_a_gate", 0)


def test_wrong_qubit_count_rejected():
    qc = QuantumCircuit(2)
    with pytest.raises(CircuitValidationError):
        qc.append("cx", [0])  # cx needs 2 qubits


def test_qubit_out_of_range():
    qc = QuantumCircuit(2)
    with pytest.raises(CircuitValidationError):
        qc.h(5)


def test_wrong_param_count():
    qc = QuantumCircuit(1)
    with pytest.raises(CircuitValidationError):
        qc.append("rx", 0, params=[])  # rx needs 1 param


def test_mcx_variable_qubits():
    qc = QuantumCircuit(4)
    qc.mcx([0, 1, 2], 3)
    assert qc.operations[0].qubits == [0, 1, 2, 3]


def test_variable_gate_minimum_qubits_rejected():
    qc = QuantumCircuit(2)
    with pytest.raises(CircuitValidationError):
        qc.mcx([], 0)
    with pytest.raises(CircuitValidationError):
        qc.mcrx(0.5, [], 0)


def test_from_dict_roundtrip():
    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    server_shape = {"circuit_id": "abc", "circuit": qc.to_dict()}
    rebuilt = QuantumCircuit.from_dict(server_shape)
    assert rebuilt.num_qubits == 2
    assert rebuilt.name == "bell"
    assert [op.name for op in rebuilt.operations] == ["h", "cx"]


def test_to_csv_includes_api_columns_and_metadata():
    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.delay(5, 1, unit="ns")

    csv_text = qc.to_csv()

    assert "name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name" in csv_text
    assert "h,0,,,,2,2,bell" in csv_text
    assert 'delay,1,,5.0,"{""unit"": ""ns""}",,,' in csv_text


def test_from_csv_with_explicit_metadata():
    csv_text = (
        "name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name\n"
        "h,0,,,,2,2,bell\n"
        'delay,1,,5.0,"{""unit"": ""ns""}",,,\n'
        "measure,0,0,,,,\n"
        "measure,1,1,,,,\n"
    )

    qc = QuantumCircuit.from_csv(csv_text)

    assert qc.num_qubits == 2
    assert qc.num_clbits == 2
    assert qc.name == "bell"
    assert [op.name for op in qc.operations] == ["h", "delay", "measure", "measure"]
    assert qc.operations[1].metadata == {"unit": "ns"}


def test_from_simple_csv_infers_register_sizes():
    csv_text = (
        "name,qubits,clbits,params,metadata\n"
        "h,0,,,\n"
        'cx,"0 1",,,\n'
        "measure,1,1,,\n"
    )

    qc = QuantumCircuit.from_csv(csv_text)

    assert qc.num_qubits == 2
    assert qc.num_clbits == 2
    assert [op.qubits for op in qc.operations] == [[0], [0, 1], [1]]
