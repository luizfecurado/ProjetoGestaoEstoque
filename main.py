from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import crud
from database import engine, get_db

# Criar tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

# Configuração da aplicação FastAPI
app = FastAPI(
    title="API de Gestão de Estoque",
    description="API CRUD completa para gestão de produtos, estoque e pedidos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints para Produtos
@app.post("/produtos/", response_model=schemas.Produto, status_code=status.HTTP_201_CREATED, 
          summary="Criar Produto", description="Cria um novo produto no sistema")
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo produto com as seguintes informações:
    
    - **nome**: Nome do produto (obrigatório)
    - **descricao**: Descrição do produto (opcional)
    - **preco**: Preço unitário (deve ser maior que zero)
    - **quantidadeEstoque**: Quantidade inicial em estoque (deve ser zero ou maior)
    """
    return crud.ProdutoCRUD.criar_produto(db=db, produto=produto)

@app.get("/produtos/", response_model=List[schemas.Produto], 
         summary="Listar Produtos", description="Retorna lista de todos os produtos")
def listar_produtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os produtos com paginação:
    
    - **skip**: Número de registros para pular (padrão: 0)
    - **limit**: Número máximo de registros a retornar (padrão: 100)
    """
    produtos = crud.ProdutoCRUD.listar_produtos(db=db, skip=skip, limit=limit)
    return produtos

@app.get("/produtos/{produto_id}", response_model=schemas.Produto,
         summary="Obter Produto", description="Retorna um produto específico por ID")
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """
    Obtém um produto específico pelo ID:
    
    - **produto_id**: ID único do produto
    """
    produto = crud.ProdutoCRUD.obter_produto(db=db, produto_id=produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.put("/produtos/{produto_id}", response_model=schemas.Produto,
         summary="Atualizar Produto", description="Atualiza um produto existente")
def atualizar_produto(produto_id: int, produto: schemas.ProdutoUpdate, db: Session = Depends(get_db)):
    """
    Atualiza um produto existente:
    
    - **produto_id**: ID do produto a ser atualizado
    - **produto**: Dados para atualização (todos os campos são opcionais)
    """
    produto_atualizado = crud.ProdutoCRUD.atualizar_produto(db=db, produto_id=produto_id, produto_update=produto)
    if produto_atualizado is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto_atualizado

@app.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Excluir Produto", description="Remove um produto do sistema")
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    """
    Remove um produto do sistema:
    
    - **produto_id**: ID do produto a ser removido
    """
    sucesso = crud.ProdutoCRUD.excluir_produto(db=db, produto_id=produto_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

# Endpoints para Pedidos
@app.post("/pedidos/", response_model=schemas.Pedido, status_code=status.HTTP_201_CREATED,
          summary="Criar Pedido", description="Cria um novo pedido e atualiza o estoque")
def criar_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo pedido com as seguintes informações:
    
    - **cliente**: Nome do cliente (obrigatório)
    - **itens**: Lista de itens do pedido (deve ter pelo menos um item)
        - **produtoId**: ID do produto
        - **quantidade**: Quantidade do item (deve ser maior que zero)
    
    O sistema automaticamente:
    - Valida se os produtos existem
    - Verifica se há estoque suficiente
    - Calcula os valores totais
    - Atualiza o estoque dos produtos
    """
    try:
        return crud.PedidoCRUD.criar_pedido(db=db, pedido=pedido)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/pedidos/", response_model=List[schemas.Pedido],
         summary="Listar Pedidos", description="Retorna lista de todos os pedidos")
def listar_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os pedidos com paginação:
    
    - **skip**: Número de registros para pular (padrão: 0)
    - **limit**: Número máximo de registros a retornar (padrão: 100)
    """
    pedidos = crud.PedidoCRUD.listar_pedidos(db=db, skip=skip, limit=limit)
    return pedidos

@app.get("/pedidos/{pedido_id}", response_model=schemas.Pedido,
         summary="Obter Pedido", description="Retorna um pedido específico por ID")
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Obtém um pedido específico pelo ID:
    
    - **pedido_id**: ID único do pedido
    """
    pedido = crud.PedidoCRUD.obter_pedido(db=db, pedido_id=pedido_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@app.put("/pedidos/{pedido_id}", response_model=schemas.Pedido,
         summary="Atualizar Pedido", description="Atualiza um pedido existente")
def atualizar_pedido(pedido_id: int, pedido: schemas.PedidoUpdate, db: Session = Depends(get_db)):
    """
    Atualiza um pedido existente:
    
    - **pedido_id**: ID do pedido a ser atualizado
    - **pedido**: Dados para atualização
    
    O sistema automaticamente:
    - Restaura o estoque dos itens antigos
    - Valida os novos itens
    - Atualiza o estoque dos novos itens
    - Recalcula o valor total
    """
    pedido_atualizado = crud.PedidoCRUD.atualizar_pedido(db=db, pedido_id=pedido_id, pedido_update=pedido)
    if pedido_atualizado is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido_atualizado

@app.delete("/pedidos/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Excluir Pedido", description="Remove um pedido e restaura o estoque")
def excluir_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Remove um pedido do sistema:
    
    - **pedido_id**: ID do pedido a ser removido
    
    O sistema automaticamente restaura o estoque dos produtos do pedido.
    """
    sucesso = crud.PedidoCRUD.excluir_pedido(db=db, pedido_id=pedido_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

# Endpoint de saúde da API
@app.get("/", summary="Status da API", description="Verifica se a API está funcionando")
def status_api():
    """
    Endpoint de verificação de status da API.
    Retorna uma mensagem confirmando que a API está funcionando.
    """
    return {
        "message": "API de Gestão de Estoque funcionando!",
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Tratamento de erros personalizado
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"detail": "Recurso não encontrado"}

@app.exception_handler(400)
async def bad_request_handler(request, exc):
    return {"detail": str(exc.detail)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"detail": "Erro interno do servidor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 