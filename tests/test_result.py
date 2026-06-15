from symbolicq import Result


def test_result_to_csv():
    result = Result(
        {
            "job_id": "jid",
            "status": "completed",
            "result": {
                "counts": {"00": 1, "11": 3},
                "probabilities": {"00": 0.25, "11": 0.75},
                "shots": 4,
            },
        }
    )

    assert result.to_csv() == (
        "bitstring,count,probability\n"
        "00,1,0.25\n"
        "11,3,0.75\n"
    )


def test_result_from_csv_and_accessors():
    result = Result.from_csv(
        "bitstring,count,probability\n"
        "00,1,0.25\n"
        "11,3,0.75\n",
        job_id="jid",
    )

    assert result.job_id == "jid"
    assert result.shots == 4
    assert result.count("11") == 3
    assert result.probability("00") == 0.25
    assert result.most_frequent() == "11"
    assert result.count("missing") == 0
    assert result.probability("missing") == 0.0
