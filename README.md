# API CRUD de Estoque, Produtos e Pedidos

## Descrição
API REST completa para gestão de estoque, produtos e pedidos desenvolvida em Python com FastAPI e SQLAlchemy.

## Funcionalidades

### Produtos
- ✅ Criar produto
- ✅ Listar produtos
- ✅ Obter produto por ID
- ✅ Atualizar produto
- ✅ Excluir produto
- ✅ Gerenciamento automático de estoque

### Pedidos
- ✅ Criar pedido
- ✅ Listar pedidos
- ✅ Obter pedido por ID
- ✅ Atualizar pedido
- ✅ Excluir pedido
- ✅ Cálculo automático de valores

## Tecnologias Utilizadas
- **FastAPI**: Framework web para API
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI

## Instalação e Execução

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar a aplicação:**
```bash
uvicorn main:app --reload
```

3. **Acessar a documentação:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estrutura do Projeto
```
├── main.py                 # Arquivo principal da aplicação
├── models.py              # Modelos do banco de dados
├── schemas.py             # Schemas Pydantic
├── database.py            # Configuração do banco
├── crud.py                # Operações CRUD
├── requirements.txt       # Dependências
└── README.md             # Documentação
```

## Endpoints da API

### Produtos
- `GET /produtos/` - Listar todos os produtos
- `GET /produtos/{id}` - Obter produto por ID
- `POST /produtos/` - Criar novo produto
- `PUT /produtos/{id}` - Atualizar produto
- `DELETE /produtos/{id}` - Excluir produto

### Pedidos
- `GET /pedidos/` - Listar todos os pedidos
- `GET /pedidos/{id}` - Obter pedido por ID
- `POST /pedidos/` - Criar novo pedido
- `PUT /pedidos/{id}` - Atualizar pedido
- `DELETE /pedidos/{id}` - Excluir pedido

## Exemplos de Uso

### Criar Produto
```json
{
  "nome": "Caneta Azul",
  "descricao": "Caneta esferográfica azul",
  "preco": 2.50,
  "quantidade_estoque": 150
}
```

### Criar Pedido
```json
{
  "cliente": "João da Silva",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 10
    }
  ]
}
``` 