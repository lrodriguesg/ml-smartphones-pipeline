{{ config(
    materialized='table',
    unique_key='seller_id'
) }}

with staging_products as (
    select * from {{ ref('stg_products') }}
),

seller_metrics as (
    -- Agrupamos por vendedor para criar uma dimensão única e adicionamos inteligência
    select
        seller_id,
        min(collected_at) as first_seen_at,
        max(collected_at) as last_seen_at,
        count(distinct product_id) as total_distinct_products, -- CORRIGIDO: id alterado para product_id
        sum(sold_quantity) as lifetime_sold_quantity
    from staging_products
    where seller_id is not null
    group by seller_id
)

select
    seller_id,
    total_distinct_products,
    lifetime_sold_quantity,
    first_seen_at,
    last_seen_at,
    current_timestamp as dbt_updated_at
from seller_metrics