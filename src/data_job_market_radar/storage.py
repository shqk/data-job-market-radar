# Store response from client inside raw zone

import json
import re
import httpx
from pathlib import Path
from datetime import date, datetime, timezone

def slugify_query(query: str) -> str:
    value = query.strip().lower()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^\w\-]", "", value)
    return value

# def normalize_range(range_: str) -> str:
#     return range_.replace("-", "_")

def build_path(base_dir: Path, query: str, range_: str, search_date: date) -> Path:
    return (
        base_dir /
        "france_travail" /
        "offres" /
        f"search_date={search_date.isoformat()}" /
        f"query={query}" /
        f"range={range_}"
    )

def save_raw_search_response(base_dir: Path, query: str, range_: str, response: httpx.Response) -> Path:
    # Créer le dossier
    raw_dir = build_path(base_dir=base_dir, query=slugify_query(query), range_=range_, search_date=datetime.today())
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarder les données

    # Response
    with open(raw_dir / "response.json", "w", encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2)
    
    # Headers
    with open(raw_dir / "headers.json", "w", encoding='utf-8') as f:
        json.dump(dict(response.headers), f, indent=2)
    
    # Request
    with open(raw_dir / "request.json", "w", encoding='utf-8') as f:
        request = response.request

        request_data = {
            "method" : request.method,
            "url" : str(request.url),
            "params" : dict(request.url.params),
            "headers" : {
                k: v
                for k, v in request.headers.items()
                if k != 'authorization'
            }
        }

        json.dump(request_data, f, indent=2)
    
    # Metadata
    
    return raw_dir
