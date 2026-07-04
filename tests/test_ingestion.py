from data_job_market_radar.ingestion import build_ranges, parse_total_from_content_range


def test_parse_total_from_content_range():
    range_ = "offres 0-100/453"

    assert parse_total_from_content_range(range_=range_) == 453

def test_parse_total_from_content_range_empty():
    range_ = "*/0"

    assert parse_total_from_content_range(range_=range_) == 0

def test_build_ranges():
    total = 453
    page_size = 150

    ranges = build_ranges(total, page_size)

    assert len(ranges) == 4
    assert ranges[0] == "0-149"
    assert ranges[3] == "450-452"
