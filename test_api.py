#!/usr/bin/env python3
"""
Script de teste para demonstrar o funcionamento da API de Gestão de Estoque
Execute este script após iniciar a API com: uvicorn main:app --reload
"""

import requests
import json
from datetime import datetime

# Configuração da API
BASE_URL = "http://localhost:8000"

def test_produtos():
    """Testa todas as operações CRUD de produtos"""
    print("=== TESTANDO OPERAÇÕES DE PRODUTOS ===\n")
    
    # 1. Criar produtos
    print("1. Criando produtos...")
    produtos_data = [
        {
            "nome": "Caneta Azul",
            "descricao": "Caneta esferográfica azul",
            "preco": 2.50,
            "quantidade_estoque": 150
        },
        {
            "nome": "Caderno A4",
            "descricao": "Caderno universitário 96 folhas",
            "preco": 15.90,
            "quantidade_estoque": 80
        },
        {
            "nome": "Lápis HB",
            "descricao": "Lápis grafite HB",
            "preco": 1.20,
            "quantidade_estoque": 200
        }
    ]
    
    produtos_criados = []
    for produto_data in produtos_data:
        response = requests.post(f"{BASE_URL}/produtos/", json=produto_data)
        if response.status_code == 201:
            produto = response.json()
            produtos_criados.append(produto)
            print(f"   ✅ Produto criado: {produto['nome']} (ID: {produto['id']})")
        else:
            print(f"   ❌ Erro ao criar produto: {response.text}")
    
    print()
    
    # 2. Listar produtos
    print("2. Listando produtos...")
    response = requests.get(f"{BASE_URL}/produtos/")
    if response.status_code == 200:
        produtos = response.json()
        print(f"   ✅ Total de produtos: {len(produtos)}")
        for produto in produtos:
            print(f"      - {produto['nome']}: R$ {produto['preco']:.2f} (Estoque: {produto['quantidade_estoque']})")
    else:
        print(f"   ❌ Erro ao listar produtos: {response.text}")
    
    print()
    
    # 3. Obter produto específico
    if produtos_criados:
        produto_id = produtos_criados[0]['id']
        print(f"3. Obtendo produto ID {produto_id}...")
        response = requests.get(f"{BASE_URL}/produtos/{produto_id}")
        if response.status_code == 200:
            produto = response.json()
            print(f"   ✅ Produto encontrado: {produto['nome']}")
        else:
            print(f"   ❌ Erro ao obter produto: {response.text}")
    
    print()
    
    # 4. Atualizar produto
    if produtos_criados:
        produto_id = produtos_criados[0]['id']
        print(f"4. Atualizando produto ID {produto_id}...")
        update_data = {
            "preco": 3.00,
            "quantidade_estoque": 120
        }
        response = requests.put(f"{BASE_URL}/produtos/{produto_id}", json=update_data)
        if response.status_code == 200:
            produto = response.json()
            print(f"   ✅ Produto atualizado: {produto['nome']} - Novo preço: R$ {produto['preco']:.2f}")
        else:
            print(f"   ❌ Erro ao atualizar produto: {response.text}")
    
    return produtos_criados

def test_pedidos(produtos_criados):
    """Testa todas as operações CRUD de pedidos"""
    print("\n=== TESTANDO OPERAÇÕES DE PEDIDOS ===\n")
    
    if not produtos_criados:
        print("❌ Nenhum produto disponível para criar pedidos")
        return []
    
    # 1. Criar pedido
    print("1. Criando pedido...")
    pedido_data = {
        "cliente": "João da Silva",
                    "itens": [
                {
                    "produto_id": produtos_criados[0]['id'],
                    "quantidade": 10
                },
                {
                    "produto_id": produtos_criados[1]['id'],
                    "quantidade": 2
                }
            ]
    }
    
    response = requests.post(f"{BASE_URL}/pedidos/", json=pedido_data)
    if response.status_code == 201:
        pedido = response.json()
        print(f"   ✅ Pedido criado: ID {pedido['id']} - Cliente: {pedido['cliente']}")
        print(f"      Valor total: R$ {pedido['valorTotalPedido']:.2f}")
        print(f"      Itens: {len(pedido['itens'])}")
        for item in pedido['itens']:
            print(f"         - {item['nome_produto']}: {item['quantidade']}x R$ {item['preco_unitario']:.2f}")
    else:
        print(f"   ❌ Erro ao criar pedido: {response.text}")
        return []
    
    print()
    
    # 2. Listar pedidos
    print("2. Listando pedidos...")
    response = requests.get(f"{BASE_URL}/pedidos/")
    if response.status_code == 200:
        pedidos = response.json()
        print(f"   ✅ Total de pedidos: {len(pedidos)}")
        for pedido in pedidos:
            print(f"      - Pedido {pedido['id']}: {pedido['cliente']} - R$ {pedido['valorTotalPedido']:.2f}")
    else:
        print(f"   ❌ Erro ao listar pedidos: {response.text}")
    
    print()
    
    # 3. Verificar estoque atualizado
    print("3. Verificando estoque atualizado...")
    response = requests.get(f"{BASE_URL}/produtos/")
    if response.status_code == 200:
        produtos = response.json()
        for produto in produtos:
            print(f"      - {produto['nome']}: Estoque atual = {produto['quantidade_estoque']}")
    
    return [pedido] if response.status_code == 201 else []

def test_erros():
    """Testa cenários de erro da API"""
    print("\n=== TESTANDO CENÁRIOS DE ERRO ===\n")
    
    # 1. Tentar criar pedido com produto inexistente
    print("1. Tentando criar pedido com produto inexistente...")
    pedido_invalido = {
        "cliente": "Teste",
        "itens": [
            {
                "produto_id": 999,
                "quantidade": 1
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/pedidos/", json=pedido_invalido)
    if response.status_code == 404:
        print("   ✅ Erro tratado corretamente: Produto não encontrado")
    else:
        print(f"   ❌ Erro inesperado: {response.status_code}")
    
    # 2. Tentar obter produto inexistente
    print("2. Tentando obter produto inexistente...")
    response = requests.get(f"{BASE_URL}/produtos/999")
    if response.status_code == 404:
        print("   ✅ Erro tratado corretamente: Produto não encontrado")
    else:
        print(f"   ❌ Erro inesperado: {response.status_code}")

def main():
    """Função principal que executa todos os testes"""
    print("🚀 INICIANDO TESTES DA API DE GESTÃO DE ESTOQUE")
    print("=" * 50)
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API está funcionando!")
        else:
            print("❌ API não está respondendo corretamente")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que ela está rodando em http://localhost:8000")
        print("   Execute: uvicorn main:app --reload")
        return
    
    print()
    
    # Executar testes
    produtos = test_produtos()
    pedidos = test_pedidos(produtos)
    test_erros()
    
    print("\n" + "=" * 50)
    print("🎉 TESTES CONCLUÍDOS!")
    print(f"📊 Resumo: {len(produtos)} produtos e {len(pedidos)} pedidos criados")
    print("\n📖 Acesse a documentação da API em:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    main() 