CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.raw_trades (
    trade_id    BIGINT,
    product_id  TEXT,
    price       NUMERIC,
    size        NUMERIC,
    side        TEXT,
    time        TIMESTAMP,
    raw_data    JSON
);