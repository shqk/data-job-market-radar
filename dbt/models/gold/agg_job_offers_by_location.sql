with job_offers as (
    select *
    from {{ ref('fct_job_offers') }}
)

select
    work_location_label,
    postal_code,
    city_code,
    avg(latitude) as latitude,
    avg(longitude) as longitude,
    count(*) as offer_count,
    sum(positions_count) as total_positions_count,
    count(*) filter (where is_alternance) as alternance_offer_count
from job_offers
group by
    work_location_label,
    postal_code,
    city_code
