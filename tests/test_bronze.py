import json

import duckdb
import pytest

from data_job_market_radar.bronze import (
    BronzeRow,
    find_raw_directories,
    initialize_bronze,
    read_raw_directory,
    write_to_bronze,
)


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


def test_read_raw_directory_row(tmp_path):

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
        "result_count": 3,
        "saved_at": "2026-06-15T09:03:16.846571+00:00",
    }

    with open(raw_dir / "response.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)

    with open(raw_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    rows = read_raw_directory(raw_dir)
    assert len(rows) == 3
    assert [row["offer_id"] for row in rows] == ["id1", "id2", "id3"]
    assert rows[0] == {
        "raw_directory_path": str(raw_dir),
        "offer_id": "id1",
        "search_date": "2026-06-15",
        "query": metadata["query"],
        "range": metadata["range"],
        "source": metadata["source"],
        "saved_at": metadata["saved_at"],
        "payload": response["resultats"][0],
    }

def test_read_raw_directory_row_raises(tmp_path):
    
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

    with open(raw_dir / "response.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)

    with pytest.raises(FileNotFoundError):
        read_raw_directory(raw_dir)
    

def test_read_raw_directory_path(tmp_path):
    raw_dir = (
        tmp_path
        / "france_travail"
        / "offres"
        / "query=data_engineer"
        / "range=0-100"
    )
    raw_dir.mkdir(parents=True)

    with pytest.raises(ValueError):
        read_raw_directory(raw_dir)

def test_find_raw_directories(tmp_path):
    offers_root = (
        tmp_path
        / "data"
        / "raw"
        / "france_travail"
        / "offres"
    )

    raw_dir_1 = (
        offers_root
        / "search_date=2026-06-15"
        / "query=data_engineer"
        / "range=0-100"
    )

    raw_dir_2 = (
        offers_root
        / "search_date=2026-06-16"
        / "query=data_scientist"
        / "range=0-100"
    )

    raw_dir_1.mkdir(parents=True)
    raw_dir_2.mkdir(parents=True)
    
    with open(raw_dir_1 / "response.json", "w", encoding="utf-8") as f:
        json.dump({"response" : "test"}, f, indent=2)

    with open(raw_dir_1 / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({"metadata" : "test"}, f, indent=2)

    with open(raw_dir_2 / "response.json", "w", encoding="utf-8") as f:
        json.dump({"response" : "test"}, f, indent=2)

    with open(raw_dir_2 / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({"metadata" : "test"}, f, indent=2)

    assert find_raw_directories(offers_path=offers_root) == [raw_dir_1, raw_dir_2]


def test_find_raw_directories_missing_json(tmp_path):

    offers_root = (
        tmp_path
        / "data"
        / "raw"
        / "france_travail"
        / "offres"
    )

    raw_dir_1 = (
        offers_root
        / "search_date=2026-06-15"
        / "query=data_engineer"
        / "range=0-100"
    
    )

    raw_dir_2 = (
        offers_root
        / "search_date=2026-06-16"
        / "query=data_scientist"
        / "range=0-100"
    )

    raw_dir_1.mkdir(parents=True)
    raw_dir_2.mkdir(parents=True)

    with open(raw_dir_1 / "response.json", "w", encoding="utf-8") as f:
        json.dump({"response" : "test"}, f, indent=2)

    with open(raw_dir_1 / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({"metadata" : "test"}, f, indent=2)

    with open(raw_dir_2 / "response.json", "w", encoding="utf-8") as f:
        json.dump({"response" : "test"}, f, indent=2)


    assert find_raw_directories(offers_path=offers_root) == [raw_dir_1]

def test_find_raw_directories_returns_empty_when_all_directories_are_incomplete(tmp_path):

    offers_root = (
        tmp_path
        / "data"
        / "raw"
        / "france_travail"
        / "offres"
    )

    raw_dir_1 = (
        offers_root
        / "search_date=2026-06-15"
        / "query=data_engineer"
        / "range=0-100"
    
    )

    raw_dir_2 = (
        offers_root
        / "search_date=2026-06-16"
        / "query=data_scientist"
        / "range=0-100"
    )

    raw_dir_1.mkdir(parents=True)
    raw_dir_2.mkdir(parents=True)

    with open(raw_dir_1 / "response.json", "w", encoding="utf-8") as f:
        json.dump({"response" : "test"}, f, indent=2)

    with open(raw_dir_2 / "response.json", "w", encoding="utf-8") as f:
        json.dump({"response" : "test"}, f, indent=2)


    assert find_raw_directories(offers_path=offers_root) == []

def test_write_to_bronze():
    connection = duckdb.connect(":memory:")
    connection.execute("""
        CREATE SCHEMA IF NOT EXISTS bronze;

        CREATE TABLE IF NOT EXISTS bronze.france_travail_offres (
        raw_directory_path VARCHAR NOT NULL,
        offer_id VARCHAR NOT NULL,
        search_date DATE NOT NULL,
        query VARCHAR NOT NULL,
        range VARCHAR NOT NULL,
        source VARCHAR NOT NULL,
        saved_at TIMESTAMP NOT NULL,
        loaded_at TIMESTAMP DEFAULT current_timestamp,
        payload JSON NOT NULL,
        PRIMARY KEY (raw_directory_path, offer_id)
        );
        """
    )

    response = {
        "resultats": [
            {"id": "id1"},
            {"id": "id2"},
        ]
    }
    row_1 = BronzeRow(
            raw_directory_path="/search_date=2026-06-14/query=data_engineer/range=0-100/headers.json",
            offer_id="209NMRK",
            search_date="2026-06-14",
            query="data engineer",
            range="0-100",
            source="france_travail",
            saved_at="2026-06-15T09:03:16.846571+00:00",
            payload=response["resultats"][1],
    )
    
    row_2 = BronzeRow(
        raw_directory_path="/search_date=2026-06-14/query=data_engineer/range=0-100/headers.json",
        offer_id="209PCPR",
        search_date="2026-06-14",
        query="data engineer",
        range="0-100",
        source="france_travail",
        saved_at="2026-06-15T09:03:16.846571+00:00",
        payload=response["resultats"][0],
    )

    

    rows = [row_1, row_2]

    write_to_bronze(connection=connection, rows=rows)

    added = connection.execute("SELECT offer_id, payload FROM bronze.france_travail_offres ORDER BY offer_id").fetchall()

    assert len(added) == 2
    assert added[0][0] == "209NMRK"
    assert added[1][0] == "209PCPR"

    assert added[0][1] == '{"id": "id2"}'
    assert added[1][1] == '{"id": "id1"}'
    connection.close()


def test_write_to_bronze_idempotence():
    connection = duckdb.connect(":memory:")
    connection.execute("""
        CREATE SCHEMA IF NOT EXISTS bronze;

        CREATE TABLE IF NOT EXISTS bronze.france_travail_offres (
        raw_directory_path VARCHAR NOT NULL,
        offer_id VARCHAR NOT NULL,
        search_date DATE NOT NULL,
        query VARCHAR NOT NULL,
        range VARCHAR NOT NULL,
        source VARCHAR NOT NULL,
        saved_at TIMESTAMP NOT NULL,
        loaded_at TIMESTAMP DEFAULT current_timestamp,
        payload JSON NOT NULL,
        PRIMARY KEY (raw_directory_path, offer_id)
        );
        """
    )

    response = {
        "resultats": [
            {"id": "id1"},
        ]
    }

    row_1 = BronzeRow(
        raw_directory_path="/search_date=2026-06-14/query=data_engineer/range=0-100/headers.json",
        offer_id="209PCPR",
        search_date="2026-06-14",
        query="data engineer",
        range="0-100",
        source="france_travail",
        saved_at="2026-06-15T09:03:16.846571+00:00",
        payload=response["resultats"][0],
    )

    rows = [row_1]

    write_to_bronze(connection=connection, rows=rows)
    write_to_bronze(connection=connection, rows=rows)

    added = connection.execute("SELECT offer_id, payload FROM bronze.france_travail_offres").fetchall()

    assert len(added) == 1

    connection.close()

def test_write_to_bronze_no_rows():
    connection = duckdb.connect(":memory:")
    connection.execute("""
        CREATE SCHEMA IF NOT EXISTS bronze;

        CREATE TABLE IF NOT EXISTS bronze.france_travail_offres (
        raw_directory_path VARCHAR NOT NULL,
        offer_id VARCHAR NOT NULL,
        search_date DATE NOT NULL,
        query VARCHAR NOT NULL,
        range VARCHAR NOT NULL,
        source VARCHAR NOT NULL,
        saved_at TIMESTAMP NOT NULL,
        loaded_at TIMESTAMP DEFAULT current_timestamp,
        payload JSON NOT NULL,
        PRIMARY KEY (raw_directory_path, offer_id)
        );
        """
    )

    rows = []

    assert write_to_bronze(connection=connection, rows=rows) is None

    added = connection.execute("SELECT offer_id, payload FROM bronze.france_travail_offres LIMIT 10").fetchall()

    assert len(added) == 0

    connection.close()

