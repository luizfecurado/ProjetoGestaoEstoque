@echo off
chcp 65001 >nul
echo ==========================================
echo   Sistema de Gestao de Estoque - Deploy
echo ==========================================
echo.

REM Verificar se Docker está instalado
echo [STEP] Verificando se Docker está instalado...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker não está instalado ou não está no PATH
    echo Por favor, instale o Docker Desktop para Windows
    pause
    exit /b 1
)
echo [INFO] Docker encontrado

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose não está instalado
    echo Por favor, instale o Docker Compose
    pause
    exit /b 1
)
echo [INFO] Docker Compose encontrado

REM Verificar arquivo .env
echo [STEP] Verificando arquivo de configuração...
if not exist ".env" (
    echo [WARNING] Arquivo .env não encontrado
    if exist "env.example" (
        echo [INFO] Criando .env a partir do exemplo...
        copy "env.example" ".env" >nul
        echo [WARNING] Por favor, edite o arquivo .env com suas configurações
        echo Pressione qualquer tecla para continuar após editar o .env...
        pause
    ) else (
        echo [ERROR] Arquivo env.example não encontrado!
        pause
        exit /b 1
    )
) else (
    echo [INFO] Arquivo .env encontrado
)

REM Parar containers existentes
echo [STEP] Parando containers existentes...
docker-compose down --remove-orphans >nul 2>&1
echo [INFO] Containers parados

REM Construir e iniciar containers
echo [STEP] Construindo e iniciando containers...
docker-compose up --build -d
if %errorlevel% neq 0 (
    echo [ERROR] Erro ao iniciar containers
    docker-compose logs
    pause
    exit /b 1
)
echo [INFO] Containers iniciados

echo [INFO] Aguardando serviços iniciarem...
timeout /t 10 /nobreak >nul

REM Verificar se containers estão rodando
docker-compose ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Alguns containers não iniciaram corretamente
    docker-compose logs
    pause
    exit /b 1
)
echo [INFO] Todos os containers estão rodando

REM Verificar saúde dos serviços
echo [STEP] Verificando saúde dos serviços...

REM Aguardar PostgreSQL
echo [INFO] Aguardando PostgreSQL...
set timeout=60
:wait_postgres
docker-compose exec -T postgres pg_isready -U postgres >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] PostgreSQL está pronto
    goto check_api
)
timeout /t 2 /nobreak >nul
set /a timeout-=2
if %timeout% leq 0 (
    echo [ERROR] PostgreSQL não iniciou no tempo esperado
    pause
    exit /b 1
)
goto wait_postgres

:check_api
REM Verificar API
echo [INFO] Verificando API...
set timeout=30
:wait_api
curl -f http://localhost:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] API está funcionando
    goto show_info
)
timeout /t 2 /nobreak >nul
set /a timeout-=2
if %timeout% leq 0 (
    echo [WARNING] API pode não estar totalmente pronta ainda
    goto show_info
)
goto wait_api

:show_info
REM Mostrar informações finais
echo.
echo [STEP] Deploy concluído com sucesso!
echo.
echo Sistema de Gestao de Estoque
echo ================================
echo Interface Web: http://localhost
echo Documentação API: http://localhost/docs
echo API Direta: http://localhost:8000
echo Banco PostgreSQL: localhost:5432
echo.
echo Comandos úteis:
echo   - Ver logs: docker-compose logs -f
echo   - Parar: docker-compose down
echo   - Reiniciar: docker-compose restart
echo   - Backup DB: docker-compose exec postgres pg_dump -U postgres gestao_estoque ^> backup.sql
echo.

REM Verificar se há arquivo SQLite para migração
if exist "estoque.db" (
    echo [STEP] Arquivo SQLite encontrado. Deseja migrar os dados?
    set /p response="Digite 's' para migrar ou Enter para pular: "
    if /i "%response%"=="s" (
        echo [INFO] Executando migração de dados...
        python migrate_sqlite_to_postgres.py
        if %errorlevel% equ 0 (
            echo [INFO] Migração concluída
        ) else (
            echo [ERROR] Erro durante migração
        )
    )
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul 