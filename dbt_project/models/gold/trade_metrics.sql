{{
    config(
        materialized='table',
        schema='gold',
    )
}}

WITH trades AS (
    SELECT * FROM {{ ref('trades') }}
),
price_bounds AS (
    SELECT DISTINCT
        product_id,
        DATE_TRUNC('hour', time) AS trade_hour,
        FIRST_VALUE(price) OVER (
            PARTITION BY product_id, DATE_TRUNC('hour', time)
            ORDER BY time
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS price_open,
        LAST_VALUE(price) OVER (
            PARTITION BY product_id, DATE_TRUNC('hour', time)
            ORDER BY time
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS price_close
    FROM trades
),
aggregated AS (
    SELECT
        product_id,
        DATE_TRUNC('hour', time)                            AS trade_hour,
        SUM(size)                                           AS total_volume,
        SUM(CASE WHEN side = 'buy'  THEN size ELSE 0 END)  AS buy_volume,
        SUM(CASE WHEN side = 'sell' THEN size ELSE 0 END)  AS sell_volume,
        COUNT(*)                                            AS trade_count,
        MAX(price)                                          AS high_price,
        MIN(price)                                          AS low_price,
        ROUND(AVG(price), 4)                               AS avg_price
    FROM trades
    GROUP BY product_id, DATE_TRUNC('hour', time)
)

SELECT
    a.product_id,
    a.trade_hour,
    a.total_volume,
    a.buy_volume,
    a.sell_volume,
    a.trade_count,
    a.high_price,
    a.low_price,
    a.avg_price,
    p.price_open,
    p.price_close,
    ROUND(a.buy_volume / NULLIF(a.total_volume, 0), 4)     AS buy_ratio
FROM aggregated a
JOIN price_bounds p ON a.product_id = p.product_id AND a.trade_hour = p.trade_hour
ORDER BY a.product_id, a.trade_hour