{% snapshot dim_user_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='user_key',
        strategy='check',
        check_cols=['segment']
    )
}}

-- Internal snapshot of the dim_user table to track changes in the 'segment' column over time.
SELECT
    user_key,
    'USER-' || user_key AS user_id,
    'User ' || user_key AS user_name,
    case
        when user_key % 3 = 0 then 'Premium'
        when user_key % 2 = 0 then 'Active'
        else 'New'
    end AS segment
FROM {{ source('raw', 'events') }}
GROUP BY 1, 2, 3

{%- endsnapshot -%}