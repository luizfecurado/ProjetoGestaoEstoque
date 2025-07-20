# 🗄️ Diagrama Visual da Modelagem de Dados

## 📊 Estrutura Completa do Banco

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SISTEMA DE GESTÃO DE ESTOQUE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐                    ┌─────────────────┐
│     PRODUTOS    │                    │     PEDIDOS     │
├─────────────────┤                    ├─────────────────┤
│ PK: id (INT)    │                    │ PK: id (INT)    │
│ nome (VARCHAR)  │                    │ cliente (VARCHAR)│
│ descricao (TEXT)│                    │ valorTotal (FLOAT)│
│ preco (FLOAT)   │                    │ dataPedido (TIMESTAMP)│
│ quantidade_esto │                    └─────────────────┘
│ (INT)           │                              │
└─────────────────┘                              │
         │                                       │
         │ 1:N                                  │ 1:N
         │ (Um produto pode estar               │ (Um pedido tem vários itens)
         │  em vários itens)                    │
         │                                       │
         └───────────────────────────────────────┼─────────────────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │   ITENS_PEDIDO  │
                                         ├─────────────────┤
                                         │ PK: id (INT)    │
                                         │ FK: pedido_id   │
                                         │ FK: produto_id  │
                                         │ nome_produto    │
                                         │ quantidade (INT)│
                                         │ preco_unitario  │
                                         │ valor_total_item│
                                         └─────────────────┘
```

## 🔗 Relacionamentos Detalhados

### **1. Produto ↔ ItemPedido (1:N)**
```
┌─────────────┐         ┌─────────────┐
│   PRODUTO   │   1     │ ITEM_PEDIDO │
│             │ ──────► │             │
│ - id        │         │ - produto_id│
│ - nome      │         │ - nome_prod │
│ - preco     │         │ - preco_unit│
│ - estoque   │         │ - quantidade│
└─────────────┘         └─────────────┘
```

**Características:**
- **Cardinalidade**: 1:N (Um produto pode estar em vários itens de pedido)
- **Chave Estrangeira**: `produto_id` em `itens_pedido` referencia `id` em `produtos`
- **Snapshots**: `nome_produto` e `preco_unitario` são copiados no momento do pedido

### **2. Pedido ↔ ItemPedido (1:N)**
```
┌─────────────┐         ┌─────────────┐
│   PEDIDO    │   1     │ ITEM_PEDIDO │
│             │ ──────► │             │
│ - id        │         │ - pedido_id │
│ - cliente   │         │ - produto_id│
│ - valorTotal│         │ - quantidade│
│ - dataPedido│         │ - valor_item│
└─────────────┘         └─────────────┘
```

**Características:**
- **Cardinalidade**: 1:N (Um pedido tem vários itens)
- **Chave Estrangeira**: `pedido_id` em `itens_pedido` referencia `id` em `pedidos`
- **Cascade Delete**: Se pedido for excluído, itens são removidos automaticamente

## 📋 Especificação Técnica das Tabelas

### **Tabela: produtos**
```sql
CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco FLOAT NOT NULL CHECK (preco > 0),
    quantidade_estoque INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_estoque >= 0)
);

CREATE INDEX idx_produtos_nome ON produtos(nome);
```

### **Tabela: pedidos**
```sql
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente VARCHAR(100) NOT NULL,
    valorTotalPedido FLOAT NOT NULL DEFAULT 0.0,
    dataPedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pedidos_data ON pedidos(dataPedido);
```

### **Tabela: itens_pedido**
```sql
CREATE TABLE itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    nome_produto VARCHAR(100) NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario FLOAT NOT NULL CHECK (preco_unitario > 0),
    valor_total_item FLOAT NOT NULL CHECK (valor_total_item > 0),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);
```

## 🎯 Fluxo de Dados

### **1. Criação de Produto**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │───►│ Validação   │───►│   Banco     │
│             │    │ Pydantic    │    │ PostgreSQL  │
│ - nome      │    │ - nome > 0  │    │ - INSERT    │
│ - preco     │    │ - preco > 0 │    │ - COMMIT    │
│ - estoque   │    │ - estoque>=0│    │ - RETURN ID │
└─────────────┘    └─────────────┘    └─────────────┘
```

### **2. Criação de Pedido**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │───►│ Validação   │───►│ Processamento│───►│   Banco     │
│             │    │ Pydantic    │    │ CRUD        │    │ PostgreSQL  │
│ - cliente   │    │ - cliente   │    │ - Verificar │    │ - INSERT    │
│ - itens[]   │    │ - itens > 0 │    │   estoque   │    │   pedido    │
│             │    │             │    │ - Calcular  │    │ - INSERT    │
│             │    │             │    │   valores   │    │   itens     │
│             │    │             │    │ - Atualizar │    │ - UPDATE    │
│             │    │             │    │   estoque   │    │   estoque   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🔄 Operações CRUD

### **CREATE (Criar)**
```python
# Produto
produto = ProdutoCRUD.criar_produto(db, produto_data)

# Pedido
pedido = PedidoCRUD.criar_pedido(db, pedido_data)
```

### **READ (Ler)**
```python
# Produto
produto = ProdutoCRUD.obter_produto(db, produto_id)
produtos = ProdutoCRUD.listar_produtos(db, skip=0, limit=100)

# Pedido
pedido = PedidoCRUD.obter_pedido(db, pedido_id)
pedidos = PedidoCRUD.listar_pedidos(db, skip=0, limit=100)
```

### **UPDATE (Atualizar)**
```python
# Produto
produto = ProdutoCRUD.atualizar_produto(db, produto_id, update_data)

# Pedido
pedido = PedidoCRUD.atualizar_pedido(db, pedido_id, update_data)
```

### **DELETE (Excluir)**
```python
# Produto
success = ProdutoCRUD.excluir_produto(db, produto_id)

# Pedido (restaura estoque automaticamente)
success = PedidoCRUD.excluir_pedido(db, pedido_id)
```

## 🎯 Regras de Negócio Implementadas

### **1. Validações de Produto**
- ✅ Nome obrigatório (1-100 caracteres)
- ✅ Preço deve ser maior que zero
- ✅ Quantidade de estoque não pode ser negativa
- ✅ Descrição opcional

### **2. Validações de Pedido**
- ✅ Cliente obrigatório (1-100 caracteres)
- ✅ Pelo menos um item no pedido
- ✅ Quantidade de cada item deve ser maior que zero
- ✅ Estoque suficiente para todos os itens

### **3. Controle Automático de Estoque**
- ✅ Estoque é reduzido automaticamente ao criar pedido
- ✅ Estoque é restaurado automaticamente ao cancelar pedido
- ✅ Estoque é ajustado automaticamente ao atualizar pedido
- ✅ Validação de estoque insuficiente

### **4. Cálculos Automáticos**
- ✅ Valor total do item = quantidade × preço unitário
- ✅ Valor total do pedido = soma de todos os itens
- ✅ Snapshots de preços e nomes preservados

## 🔍 Consultas Otimizadas

### **1. Produtos em Baixo Estoque**
```sql
SELECT id, nome, quantidade_estoque 
FROM produtos 
WHERE quantidade_estoque < 10 
ORDER BY quantidade_estoque ASC;
```

### **2. Valor Total do Estoque**
```sql
SELECT SUM(preco * quantidade_estoque) as valor_total_estoque 
FROM produtos;
```

### **3. Pedidos por Cliente**
```sql
SELECT p.cliente, COUNT(*) as total_pedidos, SUM(p.valorTotalPedido) as valor_total
FROM pedidos p
GROUP BY p.cliente
ORDER BY valor_total DESC;
```

### **4. Produtos Mais Vendidos**
```sql
SELECT p.nome, SUM(ip.quantidade) as total_vendido
FROM produtos p
JOIN itens_pedido ip ON p.id = ip.produto_id
GROUP BY p.id, p.nome
ORDER BY total_vendido DESC
LIMIT 10;
```

## 🚀 Benefícios da Modelagem

### **1. Integridade de Dados**
- ✅ Foreign Keys garantem relacionamentos válidos
- ✅ Check constraints validam regras de negócio
- ✅ Cascade delete mantém consistência

### **2. Performance**
- ✅ Índices otimizam consultas frequentes
- ✅ Snapshots evitam JOINs desnecessários
- ✅ Lazy loading carrega dados sob demanda

### **3. Escalabilidade**
- ✅ Estrutura preparada para crescimento
- ✅ Relacionamentos bem definidos
- ✅ Fácil extensão para novas funcionalidades

### **4. Manutenibilidade**
- ✅ Código limpo e bem documentado
- ✅ Separação clara de responsabilidades
- ✅ Schemas Pydantic para validação

---

**Esta modelagem garante um sistema robusto, eficiente e fácil de manter! 🎯** 