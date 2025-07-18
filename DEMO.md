# Demonstração da API de Gestão de Estoque

## 🚀 Como Usar a API

### 1. Iniciar a API
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar a API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Acessar a Documentação
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 Exemplos Práticos

### Criar Produtos

```bash
# Criar caneta azul
curl -X POST "http://localhost:8000/produtos/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Caneta Azul",
    "descricao": "Caneta esferográfica azul",
    "preco": 2.50,
    "quantidade_estoque": 150
  }'

# Criar caderno
curl -X POST "http://localhost:8000/produtos/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Caderno A4",
    "descricao": "Caderno universitário 96 folhas",
    "preco": 15.90,
    "quantidade_estoque": 80
  }'
```

### Listar Produtos

```bash
# Listar todos os produtos
curl -X GET "http://localhost:8000/produtos/"

# Listar com paginação
curl -X GET "http://localhost:8000/produtos/?skip=0&limit=10"
```

### Obter Produto Específico

```bash
# Obter produto por ID
curl -X GET "http://localhost:8000/produtos/1"
```

### Atualizar Produto

```bash
# Atualizar preço e estoque
curl -X PUT "http://localhost:8000/produtos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "preco": 3.00,
    "quantidade_estoque": 120
  }'
```

### Criar Pedido

```bash
# Criar pedido com múltiplos itens
curl -X POST "http://localhost:8000/pedidos/" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": "João da Silva",
    "itens": [
      {
        "produto_id": 1,
        "quantidade": 10
      },
      {
        "produto_id": 2,
        "quantidade": 2
      }
    ]
  }'
```

### Listar Pedidos

```bash
# Listar todos os pedidos
curl -X GET "http://localhost:8000/pedidos/"

# Obter pedido específico
curl -X GET "http://localhost:8000/pedidos/1"
```

### Atualizar Pedido

```bash
# Atualizar cliente e itens
curl -X PUT "http://localhost:8000/pedidos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": "Maria Santos",
    "itens": [
      {
        "produto_id": 1,
        "quantidade": 5
      }
    ]
  }'
```

### Excluir Recursos

```bash
# Excluir produto
curl -X DELETE "http://localhost:8000/produtos/1"

# Excluir pedido
curl -X DELETE "http://localhost:8000/pedidos/1"
```

## 🔍 Respostas da API

### Produto Criado
```json
{
  "id": 1,
  "nome": "Caneta Azul",
  "descricao": "Caneta esferográfica azul",
  "preco": 2.50,
  "quantidade_estoque": 150
}
```

### Pedido Criado
```json
{
  "id": 1,
  "cliente": "João da Silva",
  "itens": [
    {
      "id": 1,
      "produto_id": 1,
      "quantidade": 10,
      "pedido_id": 1,
      "nome_produto": "Caneta Azul",
      "preco_unitario": 2.50,
      "valor_total_item": 25.00
    }
  ],
  "valorTotalPedido": 25.00,
  "dataPedido": "2025-07-18T00:17:38"
}
```

## ⚠️ Tratamento de Erros

### Produto não encontrado
```json
{
  "detail": "Produto não encontrado"
}
```

### Estoque insuficiente
```json
{
  "detail": "Estoque insuficiente para o produto 'Caneta Azul'. Disponível: 5, Solicitado: 10"
}
```

### Dados inválidos
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "nome"],
      "msg": "Field required"
    }
  ]
}
```

## 🧪 Testes Automatizados

Execute os testes para verificar todas as funcionalidades:

```bash
# Teste completo
python test_api.py

# Teste simples
python simple_test.py

# Teste direto (sem API)
python debug_test.py
```

## 📊 Funcionalidades Implementadas

✅ **Produtos**
- Criar produto
- Listar produtos
- Obter produto por ID
- Atualizar produto
- Excluir produto

✅ **Pedidos**
- Criar pedido
- Listar pedidos
- Obter pedido por ID
- Atualizar pedido
- Excluir pedido

✅ **Estoque**
- Atualização automática do estoque
- Validação de estoque suficiente
- Restauração do estoque ao excluir pedidos

✅ **Validações**
- Validação de dados de entrada
- Tratamento de erros
- Mensagens de erro claras

✅ **Documentação**
- Swagger UI automática
- ReDoc automática
- Exemplos de uso 