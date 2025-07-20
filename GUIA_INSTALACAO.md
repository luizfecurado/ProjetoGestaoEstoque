# 🚀 Guia Rápido de Instalação - Windows

## Pré-requisitos

### 1. Instalar Docker Desktop
1. Baixe o Docker Desktop para Windows: https://www.docker.com/products/docker-desktop/
2. Execute o instalador e siga as instruções
3. Reinicie o computador após a instalação
4. Abra o Docker Desktop e aguarde inicializar

### 2. Verificar Instalação
Abra o PowerShell ou Prompt de Comando e execute:
```cmd
docker --version
docker-compose --version
```

## Deploy Rápido

### Opção 1: Script Automatizado (Recomendado)
```cmd
.\deploy.bat
```

### Opção 2: Comandos Manuais
```cmd
# 1. Configurar variáveis de ambiente
copy env.example .env

# 2. Editar configurações (opcional)
notepad .env

# 3. Iniciar serviços
docker-compose up --build -d

# 4. Verificar status
docker-compose ps
```

## Acessos

Após o deploy bem-sucedido, acesse:

- **Interface Web**: http://localhost
- **Documentação API**: http://localhost/docs
- **API Direta**: http://localhost:8000

## Comandos Úteis

```cmd
# Ver logs em tempo real
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Reiniciar serviços
docker-compose restart

# Ver status dos containers
docker-compose ps

# Backup do banco
docker-compose exec postgres pg_dump -U postgres gestao_estoque > backup.sql
```

## Migração de Dados (SQLite → PostgreSQL)

Se você tem dados no SQLite antigo:

```cmd
# Executar migração
python migrate_sqlite_to_postgres.py
```

## Troubleshooting

### Docker não encontrado
- Verifique se o Docker Desktop está rodando
- Reinicie o Docker Desktop
- Verifique se está no PATH do sistema

### Porta já em uso
```cmd
# Verificar portas em uso
netstat -ano | findstr :8000
netstat -ano | findstr :80

# Parar processo que está usando a porta
taskkill /PID <PID> /F
```

### Erro de permissão
- Execute o PowerShell como Administrador
- Verifique as configurações do Windows Defender

### Containers não iniciam
```cmd
# Ver logs detalhados
docker-compose logs

# Reconstruir containers
docker-compose up --build --force-recreate -d
```

## Estrutura de Arquivos

```
API-GestaoEstoque/
├── deploy.bat              # Script de deploy para Windows
├── deploy.sh               # Script de deploy para Linux/Mac
├── docker-compose.yml      # Configuração dos containers
├── Dockerfile              # Configuração da aplicação
├── .env                    # Variáveis de ambiente (criado automaticamente)
├── env.example             # Exemplo de variáveis
├── frontend/               # Interface web
│   ├── index.html
│   └── script.js
├── main.py                 # API FastAPI
├── models.py               # Modelos do banco
├── database.py             # Configuração do banco
├── config.py               # Configurações da aplicação
└── README.md               # Documentação completa
```

## Próximos Passos

1. **Teste a Interface**: Acesse http://localhost
2. **Adicione Produtos**: Use a interface para cadastrar produtos
3. **Crie Pedidos**: Teste o fluxo completo de pedidos
4. **Configure Backup**: Configure backup automático do banco
5. **Personalize**: Adapte cores e layout conforme necessário

## Suporte

- **Documentação API**: http://localhost/docs
- **Logs do Sistema**: `docker-compose logs -f`
- **Issues**: Abra uma issue no repositório

---

**🎯 Sistema pronto para uso em produção!** 