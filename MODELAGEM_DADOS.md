# 📊 Modelagem de Dados - Sistema de Gestão de Estoque

## 🎯 Visão Geral

A modelagem de dados foi projetada para um sistema de gestão de estoque com foco em:
- **Simplicidade**: Estrutura clara e intuitiva
- **Integridade**: Relacionamentos bem definidos
- **Performance**: Índices otimizados
- **Escalabilidade**: Preparado para crescimento

## 🗄️ Diagrama ER (Entidade-Relacionamento)

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     PRODUTOS    │         │     PEDIDOS     │         │   ITENS_PEDIDO  │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ PK: id          │         │ PK: id          │         │ PK: id          │
│ nome            │         │ cliente         │         │ FK: pedido_id   │
│ descricao       │         │ valorTotal      │         │ FK: produto_id  │
│ preco           │         │ dataPedido      │         │ nome_produto    │
│ quantidade_esto │         └─────────────────┘         │ quantidade      │
└─────────────────┘                   │                 │ preco_unitario  │
         │                            │                 │ valor_total_item│
         │                            │                 └─────────────────┘
         │                            │                           │
         └────────────────────────────┼───────────────────────────┘
                                      │
                                      │ 1:N (Um pedido tem vários itens)
                                      │ N:1 (Cada item pertence a um pedido)
                                      │
                                      │ 1:N (Um produto pode estar em vários itens)
                                      │ N:1 (Cada item referencia um produto)
```

## 📋 Detalhamento das Tabelas

### 1. **Tabela: produtos**

| Campo | Tipo | Tamanho | Nullable | Default | Descrição |
|-------|------|---------|----------|---------|-----------|
| `id` | INTEGER | - | ❌ | AUTO_INCREMENT | Chave primária |
| `nome` | VARCHAR | 100 | ❌ | - | Nome do produto |
| `descricao` | TEXT | - | ✅ | NULL | Descrição detalhada |
| `preco` | FLOAT | - | ❌ | - | Preço unitário |
| `quantidade_estoque` | INTEGER | - | ❌ | 0 | Quantidade disponível |

**Índices:**
- `PRIMARY KEY` em `id`
- `INDEX` em `nome` (para busca rápida)

**Regras de Negócio:**
- Nome obrigatório e único
- Preço deve ser maior que zero
- Quantidade de estoque não pode ser negativa

### 2. **Tabela: pedidos**

| Campo | Tipo | Tamanho | Nullable | Default | Descrição |
|-------|------|---------|----------|---------|-----------|
| `id` | INTEGER | - | ❌ | AUTO_INCREMENT | Chave primária |
| `cliente` | VARCHAR | 100 | ❌ | - | Nome do cliente |
| `valorTotalPedido` | FLOAT | - | ❌ | 0.0 | Valor total do pedido |
| `dataPedido` | TIMESTAMP | - | ❌ | NOW() | Data/hora do pedido |

**Índices:**
- `PRIMARY KEY` em `id`
- `INDEX` em `dataPedido` (para ordenação)

**Regras de Negócio:**
- Cliente obrigatório
- Valor total calculado automaticamente
- Data/hora automática

### 3. **Tabela: itens_pedido**

| Campo | Tipo | Tamanho | Nullable | Default | Descrição |
|-------|------|---------|----------|---------|-----------|
| `id` | INTEGER | - | ❌ | AUTO_INCREMENT | Chave primária |
| `pedido_id` | INTEGER | - | ❌ | - | FK para pedidos |
| `produto_id` | INTEGER | - | ❌ | - | FK para produtos |
| `nome_produto` | VARCHAR | 100 | ❌ | - | Nome do produto (snapshot) |
| `quantidade` | INTEGER | - | ❌ | - | Quantidade pedida |
| `preco_unitario` | FLOAT | - | ❌ | - | Preço unitário (snapshot) |
| `valor_total_item` | FLOAT | - | ❌ | - | Valor total do item |

**Índices:**
- `PRIMARY KEY` em `id`
- `FOREIGN KEY` em `pedido_id` → `pedidos.id`
- `FOREIGN KEY` em `produto_id` → `produtos.id`

**Regras de Negócio:**
- Quantidade deve ser maior que zero
- Preços e nomes são snapshots (não mudam se o produto for alterado)
- Valor total = quantidade × preço unitário

## 🔗 Relacionamentos

### 1. **Pedido ↔ Itens (1:N)**
```python
# Em Pedido
itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

# Em ItemPedido  
pedido = relationship("Pedido", back_populates="itens")
```

**Características:**
- **Cascade Delete**: Se um pedido for excluído, todos os itens são removidos
- **Bidirecional**: Permite navegar de pedido para itens e vice-versa

### 2. **Produto ↔ Itens (1:N)**
```python
# Em Produto
itens_pedido = relationship("ItemPedido", back_populates="produto")

# Em ItemPedido
produto = relationship("Produto", back_populates="itens_pedido", lazy="joined")
```

**Características:**
- **Lazy Loading**: Produto é carregado automaticamente com o item
- **Bidirecional**: Permite navegar de produto para itens e vice-versa

## 📝 Schemas Pydantic

### **Produto Schemas**

```python
# Base para criação e leitura
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    preco: float = Field(..., gt=0)  # Deve ser maior que zero
    quantidade_estoque: int = Field(..., ge=0)  # Deve ser zero ou maior

# Para criação (herda validações da base)
class ProdutoCreate(ProdutoBase):
    pass

# Para atualização (todos os campos opcionais)
class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    preco: Optional[float] = Field(None, gt=0)
    quantidade_estoque: Optional[int] = Field(None, ge=0)

# Para resposta (inclui ID)
class Produto(ProdutoBase):
    id: int
```

### **Pedido Schemas**

```python
# Item do pedido
class ItemPedidoBase(BaseModel):
    produto_id: int
    quantidade: int = Field(..., gt=0)  # Deve ser maior que zero

# Para criação de pedido
class PedidoCreate(BaseModel):
    cliente: str = Field(..., min_length=1, max_length=100)
    itens: List[ItemPedidoCreate] = Field(..., min_items=1)  # Pelo menos 1 item

# Para resposta completa
class Pedido(BaseModel):
    id: int
    cliente: str
    itens: List[ItemPedido]  # Lista completa de itens
    valorTotalPedido: float
    dataPedido: datetime
```

## 🎯 Decisões de Design

### 1. **Snapshots em Itens de Pedido**
```python
# Em vez de apenas referenciar o produto:
produto_id: int

# Também armazenamos dados do momento do pedido:
nome_produto: str      # Nome no momento do pedido
preco_unitario: float  # Preço no momento do pedido
```

**Vantagens:**
- Histórico preservado mesmo se produto for alterado
- Consultas mais rápidas (não precisa fazer JOIN)
- Integridade histórica

### 2. **Cálculo Automático de Valores**
```python
# Valor total do item
valor_total_item = quantidade * preco_unitario

# Valor total do pedido
valorTotalPedido = sum(item.valor_total_item for item in itens)
```

### 3. **Controle de Estoque Automático**
```python
# Ao criar pedido
produto.quantidade_estoque -= item.quantidade

# Ao cancelar pedido  
produto.quantidade_estoque += item.quantidade
```

## 🔍 Consultas Otimizadas

### 1. **Produtos em Baixo Estoque**
```sql
SELECT * FROM produtos 
WHERE quantidade_estoque < 10 
ORDER BY quantidade_estoque ASC;
```

### 2. **Valor Total do Estoque**
```sql
SELECT SUM(preco * quantidade_estoque) as valor_total 
FROM produtos;
```

### 3. **Pedidos por Período**
```sql
SELECT * FROM pedidos 
WHERE dataPedido BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY dataPedido DESC;
```

### 4. **Produtos Mais Vendidos**
```sql
SELECT p.nome, SUM(ip.quantidade) as total_vendido
FROM produtos p
JOIN itens_pedido ip ON p.id = ip.produto_id
GROUP BY p.id, p.nome
ORDER BY total_vendido DESC;
```

## 🚀 Migração SQLite → PostgreSQL

### **Compatibilidade**
- ✅ **Tipos de dados**: Todos compatíveis
- ✅ **Índices**: Mantidos
- ✅ **Relacionamentos**: Preservados
- ✅ **Constraints**: Aplicados

### **Melhorias no PostgreSQL**
- **Performance**: Melhor para consultas complexas
- **Concorrência**: Melhor controle de transações
- **Escalabilidade**: Suporte a grandes volumes
- **Recursos**: Triggers, procedures, views

## 📊 Exemplo de Uso

### **Criar Produto**
```python
produto_data = {
    "nome": "Notebook Dell Inspiron",
    "descricao": "Notebook 15 polegadas, 8GB RAM, 256GB SSD",
    "preco": 2999.99,
    "quantidade_estoque": 15
}
```

### **Criar Pedido**
```python
pedido_data = {
    "cliente": "João Silva",
    "itens": [
        {"produto_id": 1, "quantidade": 2},
        {"produto_id": 3, "quantidade": 1}
    ]
}
```

### **Resultado Automático**
```python
# Sistema automaticamente:
# 1. Valida estoque disponível
# 2. Calcula valores totais
# 3. Atualiza estoque
# 4. Cria snapshots dos dados
```

## 🎯 Benefícios da Modelagem

1. **Simplicidade**: Fácil de entender e manter
2. **Integridade**: Dados consistentes e válidos
3. **Performance**: Consultas otimizadas
4. **Escalabilidade**: Preparado para crescimento
5. **Histórico**: Preserva dados históricos
6. **Flexibilidade**: Fácil de estender

---

**Esta modelagem garante um sistema robusto, escalável e fácil de manter! 🎯** 