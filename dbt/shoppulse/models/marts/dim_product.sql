SELECT DISTINCT 
    product_key,
    'PROD-' || product_key AS product_id,
    'Product ' || product_key AS product_name,
    case
        when product_key % 4 = 0 then 'Electronics'
        when product_key % 3 = 0 then 'Apparel'
        when product_key % 3 = 1 then 'Home'
        else 'Toys'
    end AS category,
    product_key * 10.0 AS price
FROM {{ ref('stg_events') }}