{{ config(materialized='view') }}

with source as (

    select * from {{ source('raw_data', 'raw_products') }}
),

transformed as (
    select
        id as product_id,
        title,
        cast(price as numeric) as current_price,
        cast(original_price as numeric) as original_price,
        condition,
        free_shipping,
        seller_id,
        sold_quantity,
        available_quantity,
        cast(collected_at as timestamp) as collected_at,

        -- Calculando a % de desconto
        case
            when original_price is not null and original_price > 0
            then round((1 - (price / original_price)) * 100, 2)
            else 0
        end as discount_percentage

    from source
)

select * from transformed