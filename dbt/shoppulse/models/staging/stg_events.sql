SELECT 
    event_id,
    user_key,
    product_key,
    event_type,
    quantity,
    amount,
    to_timestamp(event_ts / 1000.0) AS event_timestamp,
    cast(to_timestamp(event_ts / 1000.0) as date) AS event_date
FROM {{ source('raw', 'events') }}
