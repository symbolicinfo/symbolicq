import pytest
import responses

from symbolicq import QuantumCircuit, SymbolicQBackend
from symbolicq.client import DEFAULT_BASE_URL
from symbolicq.exceptions import APIError, JobNotCompleteError

BASE = DEFAULT_BASE_URL


def _bell():
    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc


@responses.activate
def test_run_and_get_counts():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    responses.add(
        responses.POST,
        f"{BASE}/circuits/cid/runs",
        json={"job_id": "jid", "status": "queued"},
        status=202,
    )
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/status",
        json={"job_id": "jid", "status": "completed"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/result",
        json={
            "job_id": "jid",
            "status": "completed",
            "result": {
                "counts": {"00": 511, "11": 513},
                "probabilities": {"00": 0.5, "11": 0.5},
                "shots": 1024,
                "metadata": {"backend": "qsim", "seed": 7},
            },
        },
        status=200,
    )

    backend = SymbolicQBackend()
    job = backend.run(_bell(), shots=1024, seed=7)
    result = job.result(poll_interval=0)

    assert result.get_counts() == {"00": 511, "11": 513}
    assert result.get_probabilities() == {"00": 0.5, "11": 0.5}
    assert result.shots == 1024
    assert result.backend_name == "qsim"


@responses.activate
def test_run_sends_shots_and_seed():
    responses.add(responses.POST, f"{BASE}/circuits",
                  json={"circuit_id": "cid", "circuit": {}}, status=201)
    responses.add(responses.POST, f"{BASE}/circuits/cid/runs",
                  json={"job_id": "jid", "status": "queued"}, status=202)

    backend = SymbolicQBackend()
    backend.run(_bell(), shots=2048, seed=42,
                simulator_options={"measurement_uses_density": True})

    run_call = responses.calls[1].request
    import json
    body = json.loads(run_call.body)
    assert body["shots"] == 2048
    assert body["seed"] == 42
    assert body["simulator_options"] == {"measurement_uses_density": True}


@responses.activate
def test_run_csv_uploads_csv_then_starts_run():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    responses.add(
        responses.POST,
        f"{BASE}/circuits/cid/runs",
        json={"job_id": "jid", "status": "queued"},
        status=202,
    )

    backend = SymbolicQBackend()
    job = backend.run_csv("name,qubits\nh,0\n", shots=123, seed=9)

    assert job.job_id == "jid"
    assert job.circuit_id == "cid"
    assert responses.calls[0].request.headers["Content-Type"] == "text/csv"
    assert responses.calls[0].request.body == b"name,qubits\nh,0\n"


@responses.activate
def test_run_zip_uploads_zip_then_starts_run():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    responses.add(
        responses.POST,
        f"{BASE}/circuits/cid/runs",
        json={"job_id": "jid", "status": "queued"},
        status=202,
    )

    backend = SymbolicQBackend()
    job = backend.run_zip(b"zip-data", shots=321, inner_content_type="text/csv")

    assert job.job_id == "jid"
    assert job.circuit_id == "cid"
    assert responses.calls[0].request.headers["Content-Type"] == "application/zip"
    assert responses.calls[0].request.headers["X-Zip-Content-Type"] == "text/csv"
    assert responses.calls[0].request.body == b"zip-data"


@responses.activate
def test_result_for_failed_job_raises():
    responses.add(responses.POST, f"{BASE}/circuits",
                  json={"circuit_id": "cid", "circuit": {}}, status=201)
    responses.add(responses.POST, f"{BASE}/circuits/cid/runs",
                  json={"job_id": "jid", "status": "queued"}, status=202)
    responses.add(responses.GET, f"{BASE}/runs/jid/status",
                  json={"job_id": "jid", "status": "failed"}, status=200)

    backend = SymbolicQBackend()
    job = backend.run(_bell())
    with pytest.raises(APIError):
        job.result(poll_interval=0)


@responses.activate
def test_404_raises_api_error():
    responses.add(responses.GET, f"{BASE}/circuits/missing",
                  json={"error": "circuit not found"}, status=404)
    backend = SymbolicQBackend()
    with pytest.raises(APIError) as exc:
        backend.client.get_circuit("missing")
    assert exc.value.status_code == 404
    assert "not found" in str(exc.value)


@responses.activate
def test_409_raises_job_not_complete():
    responses.add(responses.GET, f"{BASE}/runs/jid/result",
                  json={"job_id": "jid", "status": "running"}, status=409)
    backend = SymbolicQBackend()
    with pytest.raises(JobNotCompleteError):
        backend.client.get_result("jid")


@responses.activate
def test_health():
    responses.add(responses.GET, f"{BASE}/health",
                  json={"ok": True, "service": "symbolic-q-flask-server"}, status=200)
    backend = SymbolicQBackend()
    assert backend.status()["ok"] is True


@responses.activate
def test_create_circuit_csv():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    backend = SymbolicQBackend()
    out = backend.client.create_circuit_csv("name,qubits\nh,0\n")

    assert out["circuit_id"] == "cid"
    request = responses.calls[0].request
    assert request.headers["Content-Type"] == "text/csv"
    assert request.body == b"name,qubits\nh,0\n"


@responses.activate
def test_create_circuit_zip():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    backend = SymbolicQBackend()
    out = backend.client.create_circuit_zip(
        b"zip-data", inner_content_type="application/json"
    )

    assert out["circuit_id"] == "cid"
    request = responses.calls[0].request
    assert request.headers["Content-Type"] == "application/zip"
    assert request.headers["X-Zip-Content-Type"] == "application/json"
    assert request.body == b"zip-data"


@responses.activate
def test_create_circuit_json_zip_packs_body():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    backend = SymbolicQBackend()
    out = backend.client.create_circuit_json_zip({"num_qubits": 1, "operations": []})

    assert out["circuit_id"] == "cid"
    request = responses.calls[0].request
    assert request.headers["Content-Type"] == "application/zip"
    assert request.body.startswith(b"PK")


@responses.activate
def test_create_circuit_csv_zip_packs_body():
    responses.add(
        responses.POST,
        f"{BASE}/circuits",
        json={"circuit_id": "cid", "circuit": {}},
        status=201,
    )
    backend = SymbolicQBackend()
    out = backend.client.create_circuit_csv_zip("name,qubits\nh,0\n")

    assert out["circuit_id"] == "cid"
    request = responses.calls[0].request
    assert request.headers["Content-Type"] == "application/zip"
    assert request.body.startswith(b"PK")


@responses.activate
def test_get_circuit_csv():
    responses.add(
        responses.GET,
        f"{BASE}/circuits/cid",
        body="name,qubits\nh,0\n",
        status=200,
        content_type="text/csv",
    )
    backend = SymbolicQBackend()
    csv_text = backend.client.get_circuit_csv("cid")

    assert csv_text == "name,qubits\nh,0\n"
    request = responses.calls[0].request
    assert request.headers["Accept"] == "text/csv"
    assert request.url == f"{BASE}/circuits/cid?format=csv"


@responses.activate
def test_get_result_csv():
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/result",
        body="bitstring,count,probability\n00,1,1.0\n",
        status=200,
        content_type="text/csv",
    )
    backend = SymbolicQBackend()
    csv_text = backend.client.get_result_csv("jid")

    assert csv_text.startswith("bitstring,count")
    request = responses.calls[0].request
    assert request.headers["Accept"] == "text/csv"
    assert request.url == f"{BASE}/runs/jid/result?format=csv"


@responses.activate
def test_get_zip_responses():
    responses.add(
        responses.GET,
        f"{BASE}/circuits/cid",
        body=b"zip-circuit",
        status=200,
        content_type="application/zip",
    )
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/result",
        body=b"zip-result",
        status=200,
        content_type="application/zip",
    )
    backend = SymbolicQBackend()

    assert backend.client.get_circuit_zip("cid") == b"zip-circuit"
    assert backend.client.get_result_zip("jid") == b"zip-result"
    assert responses.calls[0].request.headers["Accept"] == "application/zip"
    assert responses.calls[0].request.url == f"{BASE}/circuits/cid?zip=1"
    assert responses.calls[1].request.url == f"{BASE}/runs/jid/result?zip=1"


@responses.activate
def test_request_zip_supports_any_endpoint():
    responses.add(
        responses.GET,
        f"{BASE}/health",
        body=b"zip-health",
        status=200,
        content_type="application/zip",
    )
    backend = SymbolicQBackend()

    assert backend.client.request_zip("GET", "/health") == b"zip-health"
    request = responses.calls[0].request
    assert request.headers["Accept"] == "application/zip"
    assert request.url == f"{BASE}/health?zip=1"


@responses.activate
def test_cancel():
    responses.add(responses.POST, f"{BASE}/runs/jid/cancel",
                  json={"job_id": "jid", "status": "cancelled",
                        "cancel_requested": True}, status=200)
    backend = SymbolicQBackend()
    from symbolicq.job import Job
    job = Job(backend.client, "jid")
    out = job.cancel()
    assert out["cancel_requested"] is True


@responses.activate
def test_job_status_helpers():
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/status",
        json={
            "job_id": "jid",
            "status": "running",
            "progress": {"ratio": 0.5, "stage": "sampling"},
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/status",
        json={
            "job_id": "jid",
            "status": "running",
            "progress": {"ratio": 0.5, "stage": "sampling"},
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/status",
        json={
            "job_id": "jid",
            "status": "running",
            "progress": {"ratio": 0.5, "stage": "sampling"},
        },
        status=200,
    )

    backend = SymbolicQBackend()
    from symbolicq.job import Job
    job = Job(backend.client, "jid")

    assert job.status_text() == "running"
    assert job.progress()["stage"] == "sampling"
    assert job.progress_ratio() == 0.5


@responses.activate
def test_job_refresh_result():
    responses.add(
        responses.GET,
        f"{BASE}/runs/jid/result",
        json={
            "job_id": "jid",
            "status": "completed",
            "result": {
                "counts": {"0": 1},
                "probabilities": {"0": 1.0},
                "shots": 1,
            },
        },
        status=200,
    )

    backend = SymbolicQBackend()
    from symbolicq.job import Job
    job = Job(backend.client, "jid")

    assert job.refresh_result().get_counts() == {"0": 1}
