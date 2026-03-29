import pytest
import sys
import os

# Adiciona a pasta 'collector' ao caminho do sistema para o pytest achar os arquivos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../collector')))

from ml_api_client import get_smartphones_data

def test_get_smartphones_data_returns_list():
    """Testa se a função retorna uma lista."""
    resultado = get_smartphones_data()
    assert isinstance(resultado, list), "O resultado deve ser uma lista"

def test_get_smartphones_data_has_correct_keys():
    """Testa se os dicionários dentro da lista possuem os 10 campos exigidos no case."""
    resultado = get_smartphones_data()
    
    # Se a lista não estiver vazia, pega o primeiro item para testar
    if len(resultado) > 0:
        produto = resultado[0]
        campos_esperados = [
            'id', 'title', 'price', 'original_price', 'condition', 
            'free_shipping', 'seller_id', 'sold_quantity', 
            'available_quantity', 'collected_at'
        ]
        
        for campo in campos_esperados:
            assert campo in produto, f"Campo obrigatório faltando: {campo}"