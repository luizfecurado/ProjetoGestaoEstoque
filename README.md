# Sistema de Gestão de Estoque

Sistema completo de gestão de estoque com API REST, interface web moderna e banco de dados PostgreSQL.

## 🚀 Características

- **API REST** com FastAPI
- **Interface Web** responsiva e moderna
- **Banco PostgreSQL** para produção
- **Docker** para deploy simplificado
- **Gestão completa** de produtos e pedidos
- **Controle automático** de estoque
- **Documentação automática** da API

## 📋 Pré-requisitos

- Docker e Docker Compose
- Git

## 🛠️ Instalação e Deploy

### Opção 1: Deploy Automatizado (Recomendado)

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd API-GestaoEstoque
```

2. **Execute o script de deploy:**
```bash
chmod +x deploy.sh
./deploy.sh
```

O script irá:
- Verificar se o Docker está instalado
- Criar arquivo de configuração (.env) se necessário
- Construir e iniciar todos os containers
- Verificar se os serviços estão funcionando
- Mostrar as URLs de acesso

### Opção 2: Deploy Manual

1. **Configure as variáveis de ambiente:**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

2. **Inicie os serviços:**
```bash
docker-compose up --build -d
```

3. **Verifique se está funcionando:**
```bash
docker-compose ps
```

## 🌐 Acessos

Após o deploy, você pode acessar:

- **Interface Web**: http://localhost
- **Documentação API**: http://localhost/docs
- **API Direta**: http://localhost:8000
- **Banco PostgreSQL**: localhost:5432

## 📊 Funcionalidades

### Dashboard
- Visão geral do sistema
- Estatísticas em tempo real
- Produtos em baixo estoque
- Últimos pedidos

### Gestão de Produtos
- Cadastrar novos produtos
- Editar produtos existentes
- Excluir produtos
- Controle de preços e estoque

### Gestão de Pedidos
- Criar novos pedidos
- Selecionar produtos e quantidades
- Cálculo automático de valores
- Atualização automática do estoque

### Controle de Estoque
- Monitoramento em tempo real
- Alertas de baixo estoque
- Ajuste manual de quantidades
- Valor total do estoque

## 🗄️ Estrutura do Banco

### Tabelas Principais

**produtos**
- id (PK)
- nome
- descricao
- preco
- quantidade_estoque

**pedidos**
- id (PK)
- cliente
- valorTotalPedido
- dataPedido

**itens_pedido**
- id (PK)
- pedido_id (FK)
- produto_id (FK)
- nome_produto
- quantidade
- preco_unitario
- valor_total_item

## 🔧 Comandos Úteis

### Docker
```bash
# Ver logs em tempo real
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Reiniciar serviços
docker-compose restart

# Reconstruir containers
docker-compose up --build -d
```

### Banco de Dados
```bash
# Backup do banco
docker-compose exec postgres pg_dump -U postgres gestao_estoque > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres gestao_estoque < backup.sql

# Acessar banco via psql
docker-compose exec postgres psql -U postgres gestao_estoque
```

### Desenvolvimento
```bash
# Instalar dependências localmente
pip install -r requirements.txt

# Executar API localmente
python main.py

# Executar testes
python test_api.py
```

## 🔒 Configuração de Segurança

### Variáveis de Ambiente Importantes

Edite o arquivo `.env`:

```env
# Configurações do PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_segura
POSTGRES_DB=gestao_estoque

# Configurações da aplicação
DEBUG=False
SECRET_KEY=sua_chave_secreta_muito_segura

# URL do banco
DATABASE_URL=postgresql://postgres:sua_senha_segura@postgres:5432/gestao_estoque
```

### Recomendações de Segurança

1. **Altere as senhas padrão** no arquivo `.env`
2. **Use HTTPS** em produção
3. **Configure firewall** para limitar acesso
4. **Faça backups regulares** do banco
5. **Monitore logs** regularmente

## 🐛 Troubleshooting

### Problemas Comuns

**Container não inicia:**
```bash
# Verificar logs
docker-compose logs api

# Verificar se a porta está livre
netstat -tulpn | grep :8000
```

**Banco não conecta:**
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs do PostgreSQL
docker-compose logs postgres
```

**Interface não carrega:**
```bash
# Verificar se nginx está rodando
docker-compose ps nginx

# Verificar logs do nginx
docker-compose logs nginx
```

### Logs Úteis

```bash
# Logs de todos os serviços
docker-compose logs

# Logs específicos
docker-compose logs api
docker-compose logs postgres
docker-compose logs nginx

# Logs em tempo real
docker-compose logs -f
```

## 📈 Monitoramento

### Health Checks

A API inclui endpoint de saúde:
```bash
curl http://localhost:8000/
```

Resposta esperada:
```json
{
  "message": "API de Gestão de Estoque funcionando!",
  "status": "online",
  "database": "online",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### Métricas Importantes

- **Total de produtos** no sistema
- **Produtos em baixo estoque** (< 10 unidades)
- **Valor total** do estoque
- **Número de pedidos** realizados

## 🔄 Migração de Dados

### Do SQLite para PostgreSQL

Se você estava usando SQLite anteriormente:

1. **Exporte dados do SQLite:**
```bash
sqlite3 estoque.db ".dump" > backup_sqlite.sql
```

2. **Converta para PostgreSQL:**
```bash
# Edite o arquivo backup_sqlite.sql para compatibilidade
# Remova comandos específicos do SQLite
```

3. **Importe no PostgreSQL:**
```bash
docker-compose exec -T postgres psql -U postgres gestao_estoque < backup_sqlite.sql
```

## 📝 Licença

Este projeto está sob a licença MIT.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação da API em `/docs`
- Verifique os logs do sistema

---

**Desenvolvido com ❤️ usando FastAPI, PostgreSQL e Docker** 