SELECT DISTINCT
    event_date,
    EXTRACT(YEAR FROM event_date) AS year,
    EXTRACT(MONTH FROM event_date) AS month,
    EXTRACT(DAY FROM event_date) AS day,
    EXTRACT(DOW FROM event_date) AS day_of_week,
    CASE
        WHEN EXTRACT(DOW FROM event_date) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type
FROM {{ ref('stg_events') }}