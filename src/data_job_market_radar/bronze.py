import json
import re
from pathlib import Path
from typing import TypedDict

import duckdb

CREATE_BRONZE_TABLE_SQL = """
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


class BronzeRow(TypedDict):
    raw_directory_path: str
    offer_id: str
    search_date: str
    query: str
    range: str
    source: str
    saved_at: str
    payload: dict[str, object]


def initialize_bronze(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(CREATE_BRONZE_TABLE_SQL)


# Find valid raw folders
def find_raw_directories(offers_path: Path) -> list[Path]:
    directories: list[Path] = []
    pathlist = offers_path.glob("*/*/*/")

    for path in pathlist:
        # Check if response.json && metadata.json
        if (path / "response.json").exists() and (path / "metadata.json").exists():
            directories.append(path)

    return sorted(directories)

# Read raw directory (metadata + response) => Open response.json & metadata.json
def read_raw_directory(path: Path) -> list[BronzeRow]:
    try:
        rows : list[BronzeRow] = []
        response_path = path / "response.json"
        metadata_path = path / "metadata.json"

        m = re.search(r"search_date=(\d{4}-\d{2}-\d{2})", str(path), re.IGNORECASE)
        search_date = m.group(1) if m else None

        
        if search_date is None:
            raise ValueError(f"Missing search_date in raw path: {path}")

        if search_date:
            with open(response_path, encoding="utf-8") as response:
                response_dict = json.load(response)

            
            with open(metadata_path, encoding="utf-8") as metadata:
                metadata_dict = json.load(metadata)
            
            for result in response_dict["resultats"]:
                row = BronzeRow(
                    raw_directory_path=str(path),
                    offer_id=result["id"],
                    search_date=str(search_date),
                    query=metadata_dict["query"],
                    range=metadata_dict["range"],
                    source=metadata_dict["source"],
                    saved_at=metadata_dict["saved_at"],
                    payload=result,
                )
                rows.append(row)
        return rows
        
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Raw directory is incomplete: {path}"
        ) from exc




# Write in DuckDB
def write_to_bronze(connection: duckdb.DuckDBPyConnection, rows: list[BronzeRow]) -> None:
    if not rows:
        return

    connection.executemany("""
        INSERT INTO bronze.france_travail_offres (raw_directory_path, offer_id, search_date, query, range, source, saved_at, payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT DO NOTHING
    """, 
    [
        [row["raw_directory_path"], row["offer_id"], row["search_date"], row["query"], row["range"], row["source"], row["saved_at"], json.dumps(row["payload"])] 
        for row in rows]
    )


# Orchestrate logic
def load_bronze(connection: duckdb.DuckDBPyConnection):
    # Start connection
    # initialize_bronze
    # read_raw_directory
    # write_to_bronze
    # close connection
    pass
