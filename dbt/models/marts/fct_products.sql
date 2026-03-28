{{ config(materialized='table') }}

with staging as (
    -- Usando o ref() para criar a dependência automática com a View que você acabou de criar
    select * from {{ ref('stg_products') }}
),

final as (
    select
        product_id,
        title,
        current_price,
        original_price,
        discount_percentage,
        
        --Categorizando o nível do desconto
        case
            when discount_percentage >= 20 then 'Super Desconto (20%+)'
            when discount_percentage > 0 then 'Desconto Padrão'
            else 'Sem Desconto'
        end as discount_category,
        
        condition,
        free_shipping,
        seller_id,
        sold_quantity,
        available_quantity,
        collected_at
        
    from staging
)

select * from final