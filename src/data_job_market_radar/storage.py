# Store response from client inside raw zone

import json
import re
import unicodedata
from datetime import UTC, date, datetime
from pathlib import Path

import httpx


class RawStorageError(Exception):
    pass


def slugify_query(query: str) -> str:
    value = query.strip().lower()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^\w\-]", "", value)
    nfkd = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in nfkd if not unicodedata.combining(c))
    return value


# def normalize_range(range_: str) -> str:
#     return range_.replace("-", "_")


def build_path(base_dir: Path, query: str, range_: str, search_date: date) -> Path:
    return (
        base_dir
        / "france_travail"
        / "offres"
        / f"search_date={search_date.isoformat()}"
        / f"query={query}"
        / f"range={range_}"
    )


def write_json(path: Path, payload: dict) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError as exc:
        raise RawStorageError(f"Could not write raw files to {path}") from exc


def save_raw_search_response(
    base_dir: Path, query: str, range_: str, response: httpx.Response
) -> Path:
    # Créer le dossier
    raw_dir = build_path(
        base_dir=base_dir,
        query=slugify_query(query),
        range_=range_,
        search_date=date.today(),
    )
    raw_dir.mkdir(parents=True, exist_ok=True)

    request = response.request

    write_json(raw_dir / "response.json", response.json())

    request_data = {
        "method": request.method,
        "url": str(request.url),
        "params": dict(request.url.params),
        "headers": {k: v for k, v in request.headers.items() if k.lower() != "authorization"},
    }

    metadata = {
        "source": "france_travail",
        "endpoint": "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        "query": query,
        "range": range_,
        "status_code": response.status_code,
        "content_range": response.headers.get("content-range"),
        "accept_range": response.headers.get("accept-range"),
        "result_count": len(response.json().get("resultats", [])),
        "saved_at": datetime.now(UTC).isoformat(),
    }

    write_json(raw_dir / "headers.json", dict(response.headers))
    write_json(raw_dir / "request.json", request_data)
    write_json(raw_dir / "metadata.json", metadata)

    return raw_dir
