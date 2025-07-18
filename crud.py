from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import models
import schemas
from fastapi import HTTPException

# Operações CRUD para Produtos
class ProdutoCRUD:
    @staticmethod
    def criar_produto(db: Session, produto: schemas.ProdutoCreate) -> models.Produto:
        db_produto = models.Produto(**produto.model_dump())
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        return db_produto
    
    @staticmethod
    def obter_produto(db: Session, produto_id: int) -> Optional[models.Produto]:
        return db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    
    @staticmethod
    def listar_produtos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Produto]:
        return db.query(models.Produto).offset(skip).limit(limit).all()
    
    @staticmethod
    def atualizar_produto(db: Session, produto_id: int, produto_update: schemas.ProdutoUpdate) -> Optional[models.Produto]:
        db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
        if not db_produto:
            return None
        
        update_data = produto_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_produto, field, value)
        
        db.commit()
        db.refresh(db_produto)
        return db_produto
    
    @staticmethod
    def excluir_produto(db: Session, produto_id: int) -> bool:
        db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
        if not db_produto:
            return False
        
        db.delete(db_produto)
        db.commit()
        return True
    
    @staticmethod
    def atualizar_estoque(db: Session, produto_id: int, quantidade: int) -> bool:
        """Atualiza a quantidade em estoque de um produto"""
        db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
        if not db_produto:
            return False
        
        nova_quantidade = db_produto.quantidadeEstoque + quantidade
        if nova_quantidade < 0:
            raise HTTPException(status_code=400, detail="Quantidade em estoque insuficiente")
        
        db_produto.quantidadeEstoque = nova_quantidade
        db.commit()
        return True

# Operações CRUD para Pedidos
class PedidoCRUD:
    @staticmethod
    def criar_pedido(db: Session, pedido: schemas.PedidoCreate) -> models.Pedido:
        # Validar se todos os produtos existem e têm estoque suficiente
        valor_total = 0.0
        itens_validados = []
        
        for item in pedido.itens:
            produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
            if not produto:
                raise HTTPException(status_code=404, detail=f"Produto com ID {item.produto_id} não encontrado")
            
            if produto.quantidade_estoque < item.quantidade:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Estoque insuficiente para o produto '{produto.nome}'. Disponível: {produto.quantidade_estoque}, Solicitado: {item.quantidade}"
                )
            
            valor_item = produto.preco * item.quantidade
            valor_total += valor_item
            
            itens_validados.append({
                'produto': produto,
                'quantidade': item.quantidade,
                'valor_item': valor_item
            })
        
        # Criar o pedido
        db_pedido = models.Pedido(
            cliente=pedido.cliente,
            valorTotalPedido=valor_total
        )
        db.add(db_pedido)
        db.flush()  # Para obter o ID do pedido
        
        # Criar os itens do pedido e atualizar estoque
        for item_validado in itens_validados:
            produto = item_validado['produto']
            
            # Criar item do pedido
            db_item = models.ItemPedido(
                pedido_id=db_pedido.id,
                produto_id=produto.id,
                nome_produto=produto.nome,
                quantidade=item_validado['quantidade'],
                preco_unitario=produto.preco,
                valor_total_item=item_validado['valor_item']
            )
            db.add(db_item)
            
            # Atualizar estoque
            produto.quantidade_estoque -= item_validado['quantidade']
        
        db.commit()
        db.refresh(db_pedido)
        return db_pedido
    
    @staticmethod
    def obter_pedido(db: Session, pedido_id: int) -> Optional[models.Pedido]:
        return db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    
    @staticmethod
    def listar_pedidos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Pedido]:
        return db.query(models.Pedido).offset(skip).limit(limit).all()
    
    @staticmethod
    def atualizar_pedido(db: Session, pedido_id: int, pedido_update: schemas.PedidoUpdate) -> Optional[models.Pedido]:
        db_pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
        if not db_pedido:
            return None
        
        update_data = pedido_update.model_dump(exclude_unset=True)
        
        # Se há novos itens, recriar o pedido
        if 'itens' in update_data:
            # Restaurar estoque dos itens antigos
            for item in db_pedido.itens:
                produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
                if produto:
                    produto.quantidade_estoque += item.quantidade
            
            # Remover itens antigos
            db.query(models.ItemPedido).filter(models.ItemPedido.pedido_id == pedido_id).delete()
            
            # Criar novos itens (similar ao criar_pedido)
            valor_total = 0.0
            for item in update_data['itens']:
                produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
                if not produto:
                    raise HTTPException(status_code=404, detail=f"Produto com ID {item.produto_id} não encontrado")
                
                if produto.quantidade_estoque < item.quantidade:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Estoque insuficiente para o produto '{produto.nome}'"
                    )
                
                valor_item = produto.preco * item.quantidade
                valor_total += valor_item
                
                db_item = models.ItemPedido(
                    pedido_id=pedido_id,
                    produto_id=produto.id,
                    nome_produto=produto.nome,
                    quantidade=item.quantidade,
                    preco_unitario=produto.preco,
                    valor_total_item=valor_item
                )
                db.add(db_item)
                produto.quantidade_estoque -= item.quantidade
            
            db_pedido.valorTotalPedido = valor_total
        
        # Atualizar outros campos
        if 'cliente' in update_data:
            db_pedido.cliente = update_data['cliente']
        
        db.commit()
        db.refresh(db_pedido)
        return db_pedido
    
    @staticmethod
    def excluir_pedido(db: Session, pedido_id: int) -> bool:
        db_pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
        if not db_pedido:
            return False
        
        # Restaurar estoque dos produtos
        for item in db_pedido.itens:
            produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
            if produto:
                produto.quantidade_estoque += item.quantidade
        
        db.delete(db_pedido)
        db.commit()
        return True 