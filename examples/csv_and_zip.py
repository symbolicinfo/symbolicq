"""Submit circuits through the API.md CSV and ZIP formats."""

from symbolicq import (
    QuantumCircuit,
    SymbolicQBackend,
    make_circuit_json_zip,
    read_first_zip_text,
)


def main() -> None:
    backend = SymbolicQBackend()

    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    csv_text = qc.to_csv()
    csv_job = backend.run_csv(csv_text, shots=1024, seed=7)
    print("csv job:", csv_job.job_id)

    zip_bytes = make_circuit_json_zip(qc)
    print("zip preview:", read_first_zip_text(zip_bytes))
    zip_job = backend.run_zip(zip_bytes, shots=1024, seed=7)
    print("zip job:", zip_job.job_id)


if __name__ == "__main__":
    main()
