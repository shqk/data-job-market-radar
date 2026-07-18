with job_offers as (
    select *
    from {{ ref('fct_job_offers') }}
),

contract_counts as (
    select
        contract_type_code,
        count(*) as offer_count,
        sum(positions_count) as total_positions_count,
        count(*) filter (where is_alternance) as alternance_offer_count
    from job_offers
    group by contract_type_code
)

select
    contract_type_code,
    offer_count,
    total_positions_count,
    alternance_offer_count,
    round(100.0 * offer_count / sum(offer_count) over (), 2) as offer_share_pct
from contract_counts
