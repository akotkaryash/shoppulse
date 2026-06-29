SELECT DISTINCT
    event_id,
    user_key,
    product_key,
    event_date as date_key,
    event_type,
    quantity,
    amount,
    event_timestamp as event_ts
FROM {{ ref('stg_events') }}
