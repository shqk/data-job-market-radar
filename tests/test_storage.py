from datetime import date, datetime
from pathlib import Path
import json

import pytest
import httpx

from data_job_market_radar.storage import (
    slugify_query,
    build_path,
    save_raw_search_response,
)


@pytest.mark.parametrize(
    "query, expected",
    [
        ("data engineer", "data_engineer"),
        ("DATA ENGINEER", "data_engineer"),
        ("data   engineer  ", "data_engineer"),
        ("Data Engineer!", "data_engineer"),
        ("data-engineer", "data-engineer"),
        ("développeur", "developpeur"),
    ],
)
def test_slugify_query_normalizes_spaces_and_case(query, expected):

    assert slugify_query(query) == expected


def test_build_path_builds_expected_raw_search_directory():
    query = "data_engineer"
    range_ = "0-100"
    base_dir = Path("test")
    assert build_path(
        base_dir=base_dir, query=query, range_=range_, search_date=date(2026, 6, 15)
    ) == (
        Path("test")
        / "france_travail"
        / "offres"
        / "search_date=2026-06-15"
        / "query=data_engineer"
        / "range=0-100"
    )


def test_save_raw_search_response_save_files(tmp_path):
    query = "data_engineer"
    range_ = "0-100"

    request = httpx.Request(
        method="GET",
        url="https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        headers={
            "Authorization": "Bearer token",
            "Accept": "application/json",
        },
        params={"motCles": "data engineer", "range": "0-100"},
    )

    response = httpx.Response(
        json={
            "resultats": [
                {"id": "id1"},
                {"id": "id2"},
                {"id": "id3"},
            ]
        },
        status_code=200,
        request=request,
        headers={"content-range": "0-100", "accept-range": "150"},
    )

    file_path = (
        tmp_path
        / "france_travail"
        / "offres"
        / f"search_date={date.today().isoformat()}"
        / f"query={query}"
        / f"range={range_}"
    )

    assert (
        save_raw_search_response(
            base_dir=tmp_path, query=query, range_=range_, response=response
        )
        == file_path
    )

    assert (file_path / "response.json").exists()
    assert (file_path / "headers.json").exists()
    assert (file_path / "metadata.json").exists()
    assert (file_path / "request.json").exists()

    with open(file_path / "response.json", "r") as f:
        response_data = json.load(f)

        assert response_data["resultats"] == [
            {"id": "id1"},
            {"id": "id2"},
            {"id": "id3"},
        ]

    with open(file_path / "headers.json", "r") as f:
        headers_data = json.load(f)
        assert headers_data == response.headers

    with open(file_path / "metadata.json", "r") as f:
        metadata_data = json.load(f)

        assert metadata_data["source"] == "france_travail" 
        assert metadata_data["endpoint"] == "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search" 
        assert metadata_data["query"] == query
        assert metadata_data["range"] == range_
        assert metadata_data["status_code"] == response.status_code
        assert metadata_data["content_range"] == "0-100"
        assert metadata_data["accept_range"] == "150"
        assert metadata_data["result_count"] == 3
        assert datetime.fromisoformat(metadata_data["saved_at"])

    with open(file_path / "request.json", "r") as f:
        request_data = json.load(f)

        assert request_data == {
            "method": request.method,
            "url": str(request.url),
            "params": dict(request.url.params),
            "headers": {
                k: v for k, v in request.headers.items() if k.lower() != "authorization"
            },
        }

        assert "authorization" not in request_data["headers"]