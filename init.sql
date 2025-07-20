-- Script de inicialização do banco de dados
-- Este script é executado automaticamente quando o container PostgreSQL é criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Comentário sobre o banco
COMMENT ON DATABASE gestao_estoque IS 'Banco de dados para API de Gestão de Estoque';

-- Verificar se as tabelas já existem (serão criadas pelo SQLAlchemy)
-- Este script serve principalmente para configurações iniciais 