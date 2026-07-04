from pathlib import Path

from .storage import save_raw_search_response


def parse_total_from_content_range(range_: str | None) -> int:
    if not range_ or "/" not in range_:
        raise ValueError(f"Invalid content-range header: {range_}")

    total = range_.split("/")[-1]

    try:
        return int(total)
    except ValueError as exc:
        raise ValueError(f"Invalid content-range total: {range_}") from exc

def build_ranges(total: int, page_size: int) -> list[str]:
    ranges = []

    for start in range(0, total, page_size):
        end = min(start + page_size - 1, total - 1)
        fetch = f"{start}-{end}"
        ranges.append(fetch)

    return ranges


def ingest_raw_search(client, query: str, base_dir: Path) -> int:
    first_response = client.search_jobs(query, "0-149")
    total = parse_total_from_content_range(first_response.headers.get("content-range"))

    if total == 0:
        return 0

    save_raw_search_response(base_dir, query=query, range_="0-149", response=first_response)
    ranges = build_ranges(total, 150)

    for range_ in ranges[1:]:
        response = client.search_jobs(query, range_)
        save_raw_search_response(base_dir, query=query, range_=range_, response=response)

    return len(ranges)
