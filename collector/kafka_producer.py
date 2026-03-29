import os
import json
import time
import logging
from kafka import KafkaProducer
from ml_api_client import get_smartphones_data


# Configuração do Log Estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('KafkaProducer')

# Configurações do Kafka
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:29092")
TOPIC_NAME = 'ml_smartphones_raw'

def create_producer():
    """Cria e retorna um producer do Kafka."""
    
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def run_producer():
    
    logger.info("Iniciando o Produtor Kafka...")
    producer = create_producer()
    
    logger.info("Buscando dados na API do Mercado Livre...")
    produtos = get_smartphones_data()
    
    if not produtos:
        logger.warning("Nenhum produto foi retornado pela API.")
        return

    logger.info(f"Enviando {len(produtos)} registros para o tópico '{TOPIC_NAME}'...")
    
    for produto in produtos:
        # Envia para o tópico
        producer.send(TOPIC_NAME, value=produto)
        time.sleep(0.01)
        
    # Garante que todas as mensagens na fila interna sejam enviadas
    producer.flush()
    logger.info("Envio concluído com sucesso!")

if __name__ == "__main__":
    run_producer()