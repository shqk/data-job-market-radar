from pathlib import Path
from typing import TypedDict
import re
import json

import duckdb

CREATE_BRONZE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.france_travail_offres (
raw_file_path VARCHAR NOT NULL,
offer_id VARCHAR NOT NULL,
search_date DATE NOT NULL,
query VARCHAR NOT NULL,
range VARCHAR NOT NULL,
source VARCHAR NOT NULL,
saved_at TIMESTAMP NOT NULL,
loaded_at TIMESTAMP DEFAULT current_timestamp,
payload JSON NOT NULL,
PRIMARY KEY (raw_file_path, offer_id)
);
"""


class BronzeRow(TypedDict):
    raw_file_path: str
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
def find_raw_directories(path: Path):
    pass


# Read raw directory (metadata + response) => Open response.json & metadata.json
def read_raw_directory(path: Path) -> list[BronzeRow]:
    try:
        rows : list[BronzeRow] = []
        response_path = path / "response.json"
        metadata_path = path / "metadata.json"

        m = re.search(r"search_date=(\d{4}-\d{2}-\d{2})", str(path), re.IGNORECASE)
        search_date = m.group(1) if m else None

        print("Search date :", search_date)

        if search_date:
            with open(response_path) as response:
                response_dict = json.load(response)
                print('test1')
                print(len(response_dict.items()))

            
            with open(metadata_path) as metadata:
                metadata_dict = json.load(metadata)
                print('test2')
            
            for result in response_dict["resultats"]:
                row : BronzeRow = {}
                row["raw_file_path"] = str(path)
                row["offer_id"] = result["id"]
                row["search_date"] = str(search_date)
                row["query"] = metadata_dict["query"]
                row["range"] = metadata_dict["range"]
                row["source"] = metadata_dict["source"]
                row["saved_at"] = metadata_dict["saved_at"]
                row["payload"] = json.dumps(result)
                rows.append(row)
    
        return rows
    except FileNotFoundError:
        print("The file doesn't exist.")




# Write in DuckDB
def write_to_bronze(connection: duckdb.DuckDBPyConnection, rows: BronzeRow):
    pass


# Orchestrate logic
def load_bronze(connection: duckdb.DuckDBPyConnection):
    # Start connection
    # initialize_bronze
    # read_raw_directory
    # write_to_bronze
    # close connection
    pass
