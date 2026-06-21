import json

import duckdb

from data_job_market_radar.bronze import initialize_bronze, read_raw_directory


def test_initialize_bronze_expected_table():
    connection = duckdb.connect(":memory:")
    initialize_bronze(connection=connection)

    # Test "IF NOT EXISTS"
    initialize_bronze(connection=connection)

    table_exists = connection.execute("""
    SELECT COUNT(*) FROM information_schema.tables
    WHERE table_schema = 'bronze'
        AND table_name = 'france_travail_offres'
    """).fetchone()[0]

    assert table_exists == 1

    connection.close()


def test_read_raw_directory(tmp_path):

    raw_dir = (
        tmp_path
        / "france_travail"
        / "offres"
        / "search_date=2026-06-15"
        / "query=data_engineer"
        / "range=0-100"
    )
    raw_dir.mkdir(parents=True)

    response = {
        "resultats": [
            {"id": "id1"},
            {"id": "id2"},
            {"id": "id3"},
        ]
    }

    metadata = {
        "source": "france_travail",
        "endpoint": "france_travail",
        "query": "data engineer",
        "range": "0-100",
        "status_code": 206,
        "content_range": "offres 0-100/478",
        "accept_range": "150",
        "result_count": 101,
        "saved_at": "2026-06-15T09:03:16.846571+00:00",
    }

    with open(raw_dir / "response.json", "w") as f:
        json.dump(response, f, indent=2)

    with open(raw_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    rows = read_raw_directory(raw_dir)
    assert len(rows) == 3
    assert [row["offer_id"] for row in rows] == ["id1", "id2", "id3"]
    assert rows[0] == {
        "raw_file_path": str(raw_dir),
        "offer_id": "id1",
        "search_date": "2026-06-15",
        "query": metadata["query"],
        "range": metadata["range"],
        "source": metadata["source"],
        "saved_at": metadata["saved_at"],
        "payload": json.dumps(response["resultats"][0]),
    }

