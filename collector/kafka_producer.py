import json
import time
from kafka import KafkaProducer
from ml_api_client import get_smartphones_data

# Configurações do Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'ml_smartphones_raw'

def create_producer():
    """Cria e retorna um producer do Kafka."""
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        # Converte o dicionário Python para string JSON em bytes antes de enviar
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def run_producer():
    producer = create_producer()
    print("Buscando dados...")
    
    produtos = get_smartphones_data()
    
    if not produtos:
        print("Nenhum produto para enviar.")
        return

    print(f"Enviando {len(produtos)} registros para o Kafka...")
    
    for produto in produtos:
        # Envia para o tópico
        producer.send(TOPIC_NAME, value=produto)
        time.sleep(0.01)
        
    # Garante que todas as mensagens na fila interna sejam enviadas
    producer.flush()
    print("Envio concluído com sucesso!")

if __name__ == "__main__":
    run_producer()