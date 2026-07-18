with staging as (
    select *
    from {{ ref('stg_france_travail__offres') }}
),

offer_observations as (
    select
        offer_id,
        min(collected_on) as first_seen_on,
        max(collected_on) as last_seen_on,
        count(*) as observation_count,
        count(distinct search_query) as search_query_count
    from staging
    group by offer_id
),

ranked_offers as (
    select
        *,
        row_number() over (
            partition by offer_id
            order by
                collected_on desc,
                offer_updated_at desc,
                bronze_loaded_at desc,
                raw_directory_path desc
        ) as observation_rank
    from staging
),

latest_offers as (
    select
        offer_id,
        title,
        description,
        company_name,
        offer_created_at,
        offer_updated_at,
        contract_type_code,
        contract_type_label,
        is_alternance,
        positions_count,
        work_location_label,
        postal_code,
        city_code,
        latitude,
        longitude,
        offer_url,
        source_name
    from ranked_offers
    where observation_rank = 1
)

select
    latest_offers.offer_id,
    latest_offers.title,
    latest_offers.description,
    latest_offers.company_name,
    latest_offers.offer_created_at,
    latest_offers.offer_updated_at,
    offer_observations.first_seen_on,
    offer_observations.last_seen_on,
    offer_observations.observation_count,
    offer_observations.search_query_count,
    latest_offers.contract_type_code,
    latest_offers.contract_type_label,
    latest_offers.is_alternance,
    latest_offers.positions_count,
    latest_offers.work_location_label,
    latest_offers.postal_code,
    latest_offers.city_code,
    latest_offers.latitude,
    latest_offers.longitude,
    latest_offers.offer_url,
    latest_offers.source_name
from latest_offers
inner join offer_observations using (offer_id)
