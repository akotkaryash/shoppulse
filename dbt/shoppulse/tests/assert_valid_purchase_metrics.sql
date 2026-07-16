SELECT 
    event_id,
    user_key,
    event_type,
    quantity,
    amount
FROM {{ ref('fact_events') }}
WHERE event_type = 'purchase'
    AND (quantity < 1 OR amount < 0)