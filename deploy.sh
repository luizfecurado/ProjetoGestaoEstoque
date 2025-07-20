#!/bin/bash

# Script de Deploy para Sistema de Gestão de Estoque
# Este script automatiza o processo de deploy da aplicação

set -e  # Para o script se houver erro

echo "🚀 Iniciando deploy do Sistema de Gestão de Estoque..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar se Docker está instalado
check_docker() {
    print_step "Verificando se Docker está instalado..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    fi
    
    print_message "Docker e Docker Compose encontrados!"
}

# Verificar se arquivo .env existe
check_env_file() {
    print_step "Verificando arquivo de configuração..."
    if [ ! -f .env ]; then
        print_warning "Arquivo .env não encontrado. Criando a partir do exemplo..."
        if [ -f env.example ]; then
            cp env.example .env
            print_message "Arquivo .env criado a partir do exemplo."
            print_warning "Por favor, edite o arquivo .env com suas configurações antes de continuar."
            read -p "Pressione Enter para continuar após editar o .env..."
        else
            print_error "Arquivo env.example não encontrado!"
            exit 1
        fi
    else
        print_message "Arquivo .env encontrado!"
    fi
}

# Parar containers existentes
stop_containers() {
    print_step "Parando containers existentes..."
    docker-compose down --remove-orphans || true
    print_message "Containers parados!"
}

# Construir e iniciar containers
build_and_start() {
    print_step "Construindo e iniciando containers..."
    docker-compose up --build -d
    
    print_message "Aguardando serviços iniciarem..."
    sleep 10
    
    # Verificar se os containers estão rodando
    if docker-compose ps | grep -q "Up"; then
        print_message "Containers iniciados com sucesso!"
    else
        print_error "Erro ao iniciar containers!"
        docker-compose logs
        exit 1
    fi
}

# Verificar saúde dos serviços
check_health() {
    print_step "Verificando saúde dos serviços..."
    
    # Aguardar PostgreSQL estar pronto
    print_message "Aguardando PostgreSQL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            print_message "PostgreSQL está pronto!"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "PostgreSQL não iniciou no tempo esperado!"
        exit 1
    fi
    
    # Verificar API
    print_message "Verificando API..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            print_message "API está funcionando!"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "API pode não estar totalmente pronta ainda."
    fi
}

# Mostrar informações finais
show_info() {
    print_step "Deploy concluído com sucesso!"
    echo ""
    echo "📊 Sistema de Gestão de Estoque"
    echo "================================"
    echo "🌐 Interface Web: http://localhost"
    echo "📚 Documentação API: http://localhost/docs"
    echo "🔧 API Direta: http://localhost:8000"
    echo "🗄️  Banco PostgreSQL: localhost:5432"
    echo ""
    echo "📋 Comandos úteis:"
    echo "  - Ver logs: docker-compose logs -f"
    echo "  - Parar: docker-compose down"
    echo "  - Reiniciar: docker-compose restart"
    echo "  - Backup DB: docker-compose exec postgres pg_dump -U postgres gestao_estoque > backup.sql"
    echo ""
}

# Função principal
main() {
    echo "=========================================="
    echo "  Sistema de Gestão de Estoque - Deploy"
    echo "=========================================="
    echo ""
    
    check_docker
    check_env_file
    stop_containers
    build_and_start
    check_health
    show_info
}

# Executar função principal
main "$@" 