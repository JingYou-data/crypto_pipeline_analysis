{{
    config(
        materialized='table',
        schema='silver',
    )
}}

WITH raw AS (
    SELECT * FROM {{ source('bronze', 'raw_trades') }}
)

SELECT DISTINCT ON (trade_id)
    trade_id,
    product_id,
    price::NUMERIC AS price,
    size::NUMERIC AS size,
    side,
    time::TIMESTAMP AS time,
    raw_data

FROM raw

WHERE
    trade_id IS NOT NULL
    AND size is not null
ORDER BY trade_id

