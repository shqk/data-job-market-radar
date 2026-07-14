with source_data as (
    select *
    from {{ source('france_travail', 'france_travail_offres') }}
),

renamed_and_typed as (
    select
        raw_directory_path,
        offer_id,
        search_date as collected_on,
        query as search_query,
        range as search_range,
        source as source_name,
        saved_at as raw_saved_at,
        loaded_at as bronze_loaded_at,
        json_extract_string(payload, '$.intitule') as title,
        json_extract_string(payload, '$.description') as description,
        try_cast(
            json_extract_string(payload, '$.dateCreation') as timestamp with time zone
        ) as offer_created_at,
        try_cast(
            json_extract_string(payload, '$.dateActualisation') as timestamp with time zone
        ) as offer_updated_at,
        json_extract_string(payload, '$.entreprise.nom') as company_name,
        json_extract_string(payload, '$.typeContrat') as contract_type_code,
        json_extract_string(payload, '$.typeContratLibelle') as contract_type_label,
        try_cast(json_extract_string(payload, '$.alternance') as boolean) as is_alternance,
        try_cast(json_extract_string(payload, '$.nombrePostes') as integer) as positions_count,
        json_extract_string(payload, '$.lieuTravail.libelle') as work_location_label,
        json_extract_string(payload, '$.lieuTravail.codePostal') as postal_code,
        json_extract_string(payload, '$.lieuTravail.commune') as city_code,
        try_cast(json_extract_string(payload, '$.lieuTravail.latitude') as double) as latitude,
        try_cast(json_extract_string(payload, '$.lieuTravail.longitude') as double) as longitude,
        json_extract_string(payload, '$.origineOffre.urlOrigine') as offer_url
    from source_data
)

select *
from renamed_and_typed
