import json
import psycopg2
import os
from kafka import KafkaConsumer
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'ml_smartphones_raw'

# Busca as credenciais de forma segura do .env
# O segundo parâmetro (ex: "localhost") é o valor padrão caso a variável não exista
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
DB_NAME = os.getenv("POSTGRES_DB", "ecommerce_dw")

def get_db_connection():
    """Cria e retorna a conexão com o banco PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def run_consumer():
    print("Iniciando o consumidor do Kafka...")
    
    # Configuração do Consumer
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest', # Lê desde o começo do tópico se for a primeira vez
        enable_auto_commit=True,
        group_id='ml_consumer_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Aguardando mensagens... (Pressione Ctrl+C para parar)")
    
    try:
        # Loop infinito escutando novas mensagens
        for message in consumer:
            produto = message.value
            
            # A mágica da Idempotência: Se o ID já existir, atualiza os dados em vez de duplicar
            insert_query = """
                INSERT INTO raw.raw_products (
                    id, title, price, original_price, condition, 
                    free_shipping, seller_id, sold_quantity, 
                    available_quantity, collected_at
                ) VALUES (
                    %(id)s, %(title)s, %(price)s, %(original_price)s, %(condition)s, 
                    %(free_shipping)s, %(seller_id)s, %(sold_quantity)s, 
                    %(available_quantity)s, %(collected_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    price = EXCLUDED.price,
                    original_price = EXCLUDED.original_price,
                    sold_quantity = EXCLUDED.sold_quantity,
                    available_quantity = EXCLUDED.available_quantity,
                    collected_at = EXCLUDED.collected_at;
            """
            
            cursor.execute(insert_query, produto)
            conn.commit()
            
            print(f"Salvo no banco: {produto['id']} - {produto['title']}")
            
            # Condição de saída para não ficar em loop infinito durante nossos testes locais
            # Assim que ele ler todas as mensagens disponíveis, ele para.
            # No Airflow, ele fará a carga e encerrará.
            if message.offset == consumer.highwater(message.topic_partition) - 1:
                print("Todas as mensagens da fila foram processadas!")
                break
            
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
    finally:
        cursor.close()
        conn.close()
        consumer.close()
        print("Conexões encerradas.")

if __name__ == "__main__":
    run_consumer()