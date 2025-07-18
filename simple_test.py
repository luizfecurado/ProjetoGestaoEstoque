#!/usr/bin/env python3
"""
Teste simples da API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple():
    print("=== TESTE SIMPLES DA API ===\n")
    
    # 1. Verificar status
    print("1. Verificando status da API...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
        return
    
    # 2. Criar produto
    print("\n2. Criando produto...")
    produto_data = {
        "nome": "Produto Teste",
        "preco": 10.0,
        "quantidade_estoque": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}/produtos/", json=produto_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            produto = response.json()
            print(f"   Produto criado: {produto}")
            
            # 3. Criar pedido
            print("\n3. Criando pedido...")
            pedido_data = {
                "cliente": "Cliente Teste",
                "itens": [
                    {
                        "produto_id": produto['id'],
                        "quantidade": 5
                    }
                ]
            }
            
            response = requests.post(f"{BASE_URL}/pedidos/", json=pedido_data)
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")

if __name__ == "__main__":
    test_simple() 