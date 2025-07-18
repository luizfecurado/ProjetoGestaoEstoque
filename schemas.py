from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Schemas para Produto
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do produto")
    descricao: Optional[str] = Field(None, description="Descrição do produto")
    preco: float = Field(..., gt=0, description="Preço unitário do produto")
    quantidade_estoque: int = Field(..., ge=0, description="Quantidade em estoque")

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    preco: Optional[float] = Field(None, gt=0)
    quantidade_estoque: Optional[int] = Field(None, ge=0)

class Produto(ProdutoBase):
    id: int
    
    model_config = {"from_attributes": True}

# Schemas para Item do Pedido
class ItemPedidoBase(BaseModel):
    produto_id: int = Field(..., description="ID do produto")
    quantidade: int = Field(..., gt=0, description="Quantidade do item")

class ItemPedidoCreate(ItemPedidoBase):
    pass

class ItemPedido(ItemPedidoBase):
    id: int
    pedido_id: int
    nome_produto: str
    preco_unitario: float
    valor_total_item: float
    
    model_config = {"from_attributes": True}

# Schemas para Pedido
class PedidoBase(BaseModel):
    cliente: str = Field(..., min_length=1, max_length=100, description="Nome do cliente")
    itens: List[ItemPedidoCreate] = Field(..., min_items=1, description="Lista de itens do pedido")

class PedidoCreate(PedidoBase):
    pass

class PedidoUpdate(BaseModel):
    cliente: Optional[str] = Field(None, min_length=1, max_length=100)
    itens: Optional[List[ItemPedidoCreate]] = Field(None, min_items=1)

class Pedido(BaseModel):
    id: int
    cliente: str
    itens: List[ItemPedido]
    valorTotalPedido: float
    dataPedido: datetime
    
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

# Schema para resposta de erro
class ErrorResponse(BaseModel):
    detail: str 