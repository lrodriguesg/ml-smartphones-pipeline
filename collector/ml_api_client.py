import json
import random
import uuid
from datetime import datetime

def get_smartphones_data():
    """
    Gera dados simulados de smartphones devido ao bloqueio recente (Erro 403) 
    na API pública de buscas do Mercado Livre. O contrato de dados original foi mantido.
    """
    
    print("Gerando dados simulados (Mock) de smartphones...")
    
    marcas = ["Samsung Galaxy", "iPhone", "Motorola Moto", "Xiaomi Redmi"]
    modelos = ["S23", "13", "G99", "Note 12", "S22 Ultra", "14 Pro", "Edge 30", "Poco X5"]
    
    processed_products = []
    
    # Gera 50 produtos simulados
    for _ in range(50):
        marca = random.choice(marcas)
        modelo = random.choice(modelos)
        title = f"Smartphone {marca} {modelo} {random.choice(['128GB', '256GB', '512GB'])}"
        
        # Simula preços realistas
        original_price = round(random.uniform(1500.0, 7000.0), 2)
        # 30% de chance de ter desconto
        has_discount = random.choice([True, False, False])
        price = round(original_price * random.uniform(0.7, 0.95), 2) if has_discount else original_price
        
        product = {
            "id": f"MLB{random.randint(1000000000, 9999999999)}",
            "title": title,
            "price": price,
            "original_price": original_price if has_discount else None,
            "condition": random.choices(["new", "used"], weights=[0.8, 0.2])[0],
            "free_shipping": random.choice([True, False]),
            "seller_id": str(random.randint(100000, 999999)),
            "sold_quantity": random.randint(0, 500),
            "available_quantity": random.randint(1, 50),
            "collected_at": datetime.now().isoformat()
        }
        processed_products.append(product)
        
    print(f"Coleta finalizada! {len(processed_products)} produtos gerados com sucesso.")
    return processed_products

if __name__ == "__main__":
    produtos = get_smartphones_data()
    if produtos:
        print(json.dumps(produtos[0], indent=2, ensure_ascii=False))