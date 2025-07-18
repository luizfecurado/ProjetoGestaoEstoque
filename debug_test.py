#!/usr/bin/env python3
"""
Script de debug para testar a funcionalidade da API diretamente
"""

from database import SessionLocal, engine
import models
import schemas
import crud

# Criar tabelas
models.Base.metadata.create_all(bind=engine)

# Criar sessão
db = SessionLocal()

try:
    print("=== TESTE DIRETO DA FUNCIONALIDADE ===\n")
    
    # 1. Criar produto
    print("1. Criando produto...")
    produto_data = schemas.ProdutoCreate(
        nome="Caneta Azul",
        descricao="Caneta esferográfica azul",
        preco=2.50,
        quantidade_estoque=150
    )
    
    produto = crud.ProdutoCRUD.criar_produto(db=db, produto=produto_data)
    print(f"   ✅ Produto criado: {produto.nome} (ID: {produto.id})")
    
    # 2. Criar pedido
    print("\n2. Criando pedido...")
    pedido_data = schemas.PedidoCreate(
        cliente="João da Silva",
        itens=[
            schemas.ItemPedidoCreate(produto_id=produto.id, quantidade=10)
        ]
    )
    
    pedido = crud.PedidoCRUD.criar_pedido(db=db, pedido=pedido_data)
    print(f"   ✅ Pedido criado: ID {pedido.id} - Cliente: {pedido.cliente}")
    print(f"      Valor total: R$ {pedido.valorTotalPedido:.2f}")
    print(f"      Itens: {len(pedido.itens)}")
    
    # 3. Verificar estoque atualizado
    print("\n3. Verificando estoque atualizado...")
    produto_atualizado = crud.ProdutoCRUD.obter_produto(db=db, produto_id=produto.id)
    print(f"   Estoque atual: {produto_atualizado.quantidade_estoque}")
    
    print("\n✅ Todos os testes passaram!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close() 