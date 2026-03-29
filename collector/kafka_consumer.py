import json
import psycopg2
import os
from confluent_kafka import Consumer, KafkaError


# Configurações do Kafka dinâmicas (Se não achar no .env, usa o padrão do Docker)
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:29092")
TOPIC_NAME = 'ml_smartphones_raw'

# Configurações do Banco dinâmicas
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
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
    print(f"Iniciando o consumidor da Confluent apontando para: {KAFKA_BROKER}")
    
    # Configuração do Consumer da Confluent
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'ml_consumer_group',
        'auto.offset.reset': 'earliest' # Lê desde o começo
    }
    
    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Aguardando mensagens... (Pressione Ctrl+C para parar)")
    
    try:
        empty_polls = 0
        
        while True:
            # Fica escutando a fila. Retorna None se não tiver nada novo no segundo atual
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                empty_polls += 1
                # Se passar 5 segundos sem receber mensagens, encerra o loop
                if empty_polls >= 5:
                    print("Nenhuma mensagem nova na fila. Encerrando o consumidor para o Airflow seguir...")
                    break
                continue
            
            # Zerar o contador assim que receber uma mensagem válida
            empty_polls = 0
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Erro no Kafka: {msg.error()}")
                    break
            
            # Pega o JSON da mensagem e converte para dicionário Python
            produto = json.loads(msg.value().decode('utf-8'))
            
            # Idempotência no PostgreSQL
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
            
    except KeyboardInterrupt:
        print("Consumidor interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
    finally:
        cursor.close()
        conn.close()
        consumer.close()
        print("Conexões encerradas.")

if __name__ == "__main__":
    run_consumer()