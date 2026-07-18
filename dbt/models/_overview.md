{% docs __overview__ %}

# Data Job Market Radar

This dbt project transforms France Travail job-offer occurrences loaded into DuckDB by the
Python ingestion pipeline into documented and tested analytical models.

## Lineage

1. `bronze.france_travail_offres` contains one row per offer found in one raw response directory.
2. `stg_france_travail__offres` extracts and types the useful fields without changing that grain.
3. `fct_job_offers` keeps one latest observed occurrence per France Travail `offer_id`.
4. Contract and location aggregates provide dashboard-ready metrics.

## Model grains

| Model | Grain |
| --- | --- |
| `stg_france_travail__offres` | One collected occurrence per `(raw_directory_path, offer_id)` |
| `fct_job_offers` | One deduplicated observed offer per `offer_id` |
| `agg_job_offers_by_contract` | One row per contract-type code |
| `agg_job_offers_by_location` | One row per location label, postal code and commune code |

## Metric interpretation

- `offer_count` counts distinct deduplicated job offers.
- `positions_count` is the number of positions advertised by one offer.
- `total_positions_count` sums advertised positions across offers.
- The latest observed occurrence is not proof that an offer is currently active.

{% enddocs %}
