# Script de Deploy para Sistema de Gestão de Estoque (PowerShell)
# Este script automatiza o processo de deploy da aplicação no Windows

param(
    [switch]$SkipChecks,
    [switch]$Force
)

# Configurações
$ErrorActionPreference = "Stop"

# Funções para output colorido
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Blue
}

# Função para verificar se Docker está instalado
function Test-Docker {
    Write-Step "Verificando se Docker está instalado..."
    
    try {
        $dockerVersion = docker --version
        Write-Info "Docker encontrado: $dockerVersion"
    }
    catch {
        Write-Error "Docker não está instalado ou não está no PATH"
        Write-Info "Por favor, instale o Docker Desktop para Windows"
        exit 1
    }
    
    try {
        $composeVersion = docker-compose --version
        Write-Info "Docker Compose encontrado: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose não está instalado"
        Write-Info "Por favor, instale o Docker Compose"
        exit 1
    }
}

# Função para verificar arquivo .env
function Test-EnvFile {
    Write-Step "Verificando arquivo de configuração..."
    
    if (-not (Test-Path ".env")) {
        Write-Warning "Arquivo .env não encontrado"
        
        if (Test-Path "env.example") {
            Write-Info "Criando .env a partir do exemplo..."
            Copy-Item "env.example" ".env"
            Write-Warning "Por favor, edite o arquivo .env com suas configurações"
            
            if (-not $Force) {
                $response = Read-Host "Pressione Enter para continuar após editar o .env (ou 'q' para sair)"
                if ($response -eq 'q') {
                    exit 0
                }
            }
        }
        else {
            Write-Error "Arquivo env.example não encontrado!"
            exit 1
        }
    }
    else {
        Write-Info "Arquivo .env encontrado"
    }
}

# Função para parar containers existentes
function Stop-Containers {
    Write-Step "Parando containers existentes..."
    
    try {
        docker-compose down --remove-orphans
        Write-Info "Containers parados"
    }
    catch {
        Write-Warning "Nenhum container estava rodando ou erro ao parar"
    }
}

# Função para construir e iniciar containers
function Start-Containers {
    Write-Step "Construindo e iniciando containers..."
    
    try {
        docker-compose up --build -d
        Write-Info "Containers iniciados"
        
        Write-Info "Aguardando serviços iniciarem..."
        Start-Sleep -Seconds 10
        
        # Verificar se containers estão rodando
        $containers = docker-compose ps --format "table {{.Name}}\t{{.Status}}"
        if ($containers -match "Up") {
            Write-Info "Todos os containers estão rodando"
        }
        else {
            Write-Error "Alguns containers não iniciaram corretamente"
            docker-compose logs
            exit 1
        }
    }
    catch {
        Write-Error "Erro ao iniciar containers: $_"
        docker-compose logs
        exit 1
    }
}

# Função para verificar saúde dos serviços
function Test-Services {
    Write-Step "Verificando saúde dos serviços..."
    
    # Aguardar PostgreSQL
    Write-Info "Aguardando PostgreSQL..."
    $timeout = 60
    $postgresReady = $false
    
    while ($timeout -gt 0 -and -not $postgresReady) {
        try {
            docker-compose exec -T postgres pg_isready -U postgres | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $postgresReady = $true
                Write-Info "PostgreSQL está pronto"
            }
        }
        catch {
            # Ignorar erros durante verificação
        }
        
        if (-not $postgresReady) {
            Start-Sleep -Seconds 2
            $timeout -= 2
        }
    }
    
    if (-not $postgresReady) {
        Write-Error "PostgreSQL não iniciou no tempo esperado"
        exit 1
    }
    
    # Verificar API
    Write-Info "Verificando API..."
    $timeout = 30
    $apiReady = $false
    
    while ($timeout -gt 0 -and -not $apiReady) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                $apiReady = $true
                Write-Info "API está funcionando"
            }
        }
        catch {
            # Ignorar erros durante verificação
        }
        
        if (-not $apiReady) {
            Start-Sleep -Seconds 2
            $timeout -= 2
        }
    }
    
    if (-not $apiReady) {
        Write-Warning "API pode não estar totalmente pronta ainda"
    }
}

# Função para mostrar informações finais
function Show-FinalInfo {
    Write-Step "Deploy concluído com sucesso!"
    Write-Host ""
    Write-Host "Sistema de Gestao de Estoque" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "Interface Web: http://localhost" -ForegroundColor White
    Write-Host "Documentação API: http://localhost/docs" -ForegroundColor White
    Write-Host "API Direta: http://localhost:8000" -ForegroundColor White
    Write-Host "Banco PostgreSQL: localhost:5432" -ForegroundColor White
    Write-Host ""
    Write-Host "Comandos úteis:" -ForegroundColor Yellow
    Write-Host "  - Ver logs: docker-compose logs -f" -ForegroundColor Gray
    Write-Host "  - Parar: docker-compose down" -ForegroundColor Gray
    Write-Host "  - Reiniciar: docker-compose restart" -ForegroundColor Gray
    Write-Host "  - Backup DB: docker-compose exec postgres pg_dump -U postgres gestao_estoque > backup.sql" -ForegroundColor Gray
    Write-Host ""
}

# Função para migração de dados (se necessário)
function Invoke-Migration {
    if (Test-Path "estoque.db") {
        Write-Step "Arquivo SQLite encontrado. Deseja migrar os dados?"
        $response = Read-Host "Digite 's' para migrar ou Enter para pular"
        
        if ($response -eq 's') {
            Write-Info "Executando migração de dados..."
            try {
                python migrate_sqlite_to_postgres.py
                Write-Info "Migração concluída"
            }
            catch {
                Write-Error "Erro durante migração: $_"
            }
        }
    }
}

# Função principal
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Sistema de Gestao de Estoque - Deploy" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not $SkipChecks) {
        Test-Docker
    }
    
    Test-EnvFile
    Stop-Containers
    Start-Containers
    Test-Services
    Invoke-Migration
    Show-FinalInfo
}

# Executar função principal
Main 