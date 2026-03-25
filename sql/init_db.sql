
CREATE SCHEMA IF NOT EXISTS raw;


CREATE TABLE IF NOT EXISTS raw.raw_products (
    id VARCHAR PRIMARY KEY,
    title VARCHAR,
    price NUMERIC,
    original_price NUMERIC,
    condition VARCHAR,
    free_shipping BOOLEAN,
    seller_id VARCHAR,
    sold_quantity INTEGER,
    available_quantity INTEGER,
    collected_at TIMESTAMP
);