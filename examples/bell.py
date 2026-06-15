"""Run a Bell circuit against the Symbolic Q cloud simulator."""

from symbolicq import QuantumCircuit, SymbolicQBackend


def main() -> None:
    backend = SymbolicQBackend()

    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    job = backend.run(qc, shots=1024, seed=7)
    print("job:", job.job_id)

    result = job.result()
    print("counts:", result.get_counts())
    print("probabilities:", result.get_probabilities())


if __name__ == "__main__":
    main()
