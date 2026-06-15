from symbolicq import (
    QuantumCircuit,
    make_circuit_csv_zip,
    make_circuit_json_zip,
    make_zip,
    read_first_zip_member,
    read_first_zip_text,
    read_zip_members,
)


def test_make_zip_and_read_members():
    zip_bytes = make_zip("hello.txt", "hello")

    members = read_zip_members(zip_bytes)

    assert len(members) == 1
    assert members[0].filename == "hello.txt"
    assert members[0].text() == "hello"


def test_read_first_zip_member_prefers_json_then_csv():
    json_zip = make_zip("circuit.json", '{"num_qubits": 1}')
    csv_zip = make_zip("circuit.csv", "name,qubits\nh,0\n")

    assert read_first_zip_member(json_zip).filename == "circuit.json"
    assert read_first_zip_text(csv_zip) == "name,qubits\nh,0\n"


def test_make_circuit_json_zip():
    qc = QuantumCircuit(1, name="one")
    qc.h(0)

    text = read_first_zip_text(make_circuit_json_zip(qc))

    assert '"num_qubits": 1' in text
    assert '"name": "h"' in text


def test_make_circuit_csv_zip():
    qc = QuantumCircuit(1, name="one")
    qc.h(0)

    text = read_first_zip_text(make_circuit_csv_zip(qc))

    assert "name,qubits,clbits,params,metadata,num_qubits,num_clbits,circuit_name" in text
    assert "h,0,,,,1,1,one" in text
