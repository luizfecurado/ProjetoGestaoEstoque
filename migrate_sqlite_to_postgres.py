#!/usr/bin/env python3
"""
Script de Migração: SQLite para PostgreSQL
Este script migra dados de um banco SQLite para PostgreSQL
"""

import sqlite3
import psycopg2
import os
from datetime import datetime
from config import settings

def conectar_sqlite():
    """Conecta ao banco SQLite"""
    try:
        conn = sqlite3.connect('estoque.db')
        print("✅ Conectado ao SQLite")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao SQLite: {e}")
        return None

def conectar_postgres():
    """Conecta ao banco PostgreSQL"""
    try:
        # Extrair parâmetros da URL do banco
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', '')
        
        # Parse da URL
        if '@' in db_url:
            auth, rest = db_url.split('@')
            user, password = auth.split(':')
            host_port_db = rest.split('/')
            host_port = host_port_db[0].split(':')
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else '5432'
            database = host_port_db[1]
        else:
            user = settings.POSTGRES_USER
            password = settings.POSTGRES_PASSWORD
            host = settings.POSTGRES_HOST
            port = settings.POSTGRES_PORT
            database = settings.POSTGRES_DB
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print("✅ Conectado ao PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return None

def migrar_produtos(sqlite_conn, postgres_conn):
    """Migra dados da tabela produtos"""
    try:
        # Buscar dados do SQLite
        cursor_sqlite = sqlite_conn.cursor()
        cursor_sqlite.execute("SELECT id, nome, descricao, preco, quantidade_estoque FROM produtos")
        produtos = cursor_sqlite.fetchall()
        
        if not produtos:
            print("ℹ️  Nenhum produto encontrado no SQLite")
            return
        
        # Inserir no PostgreSQL
        cursor_postgres = postgres_conn.cursor()
        
        # Limpar tabela produtos (se existir)
        cursor_postgres.execute("DELETE FROM produtos")
        
        # Inserir produtos
        for produto in produtos:
            cursor_postgres.execute("""
                INSERT INTO produtos (id, nome, descricao, preco, quantidade_estoque)
                VALUES (%s, %s, %s, %s, %s)
            """, produto)
        
        postgres_conn.commit()
        print(f"✅ {len(produtos)} produtos migrados com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao migrar produtos: {e}")
        postgres_conn.rollback()

def migrar_pedidos(sqlite_conn, postgres_conn):
    """Migra dados das tabelas pedidos e itens_pedido"""
    try:
        cursor_sqlite = sqlite_conn.cursor()
        cursor_postgres = postgres_conn.cursor()
        
        # Migrar pedidos
        cursor_sqlite.execute("SELECT id, cliente, valorTotalPedido, dataPedido FROM pedidos")
        pedidos = cursor_sqlite.fetchall()
        
        if not pedidos:
            print("ℹ️  Nenhum pedido encontrado no SQLite")
            return
        
        # Limpar tabelas
        cursor_postgres.execute("DELETE FROM itens_pedido")
        cursor_postgres.execute("DELETE FROM pedidos")
        
        # Inserir pedidos
        for pedido in pedidos:
            cursor_postgres.execute("""
                INSERT INTO pedidos (id, cliente, valorTotalPedido, dataPedido)
                VALUES (%s, %s, %s, %s)
            """, pedido)
        
        # Migrar itens de pedido
        cursor_sqlite.execute("""
            SELECT id, pedido_id, produto_id, nome_produto, quantidade, 
                   preco_unitario, valor_total_item 
            FROM itens_pedido
        """)
        itens = cursor_sqlite.fetchall()
        
        for item in itens:
            cursor_postgres.execute("""
                INSERT INTO itens_pedido 
                (id, pedido_id, produto_id, nome_produto, quantidade, preco_unitario, valor_total_item)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, item)
        
        postgres_conn.commit()
        print(f"✅ {len(pedidos)} pedidos e {len(itens)} itens migrados com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao migrar pedidos: {e}")
        postgres_conn.rollback()

def verificar_migracao(postgres_conn):
    """Verifica se a migração foi bem-sucedida"""
    try:
        cursor = postgres_conn.cursor()
        
        # Contar produtos
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]
        
        # Contar pedidos
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]
        
        # Contar itens
        cursor.execute("SELECT COUNT(*) FROM itens_pedido")
        total_itens = cursor.fetchone()[0]
        
        print("\n📊 Resumo da Migração:")
        print(f"   Produtos: {total_produtos}")
        print(f"   Pedidos: {total_pedidos}")
        print(f"   Itens de Pedido: {total_itens}")
        
        if total_produtos > 0 or total_pedidos > 0:
            print("✅ Migração concluída com sucesso!")
        else:
            print("⚠️  Nenhum dado foi migrado")
            
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")

def main():
    """Função principal de migração"""
    print("🔄 Iniciando migração de SQLite para PostgreSQL")
    print("=" * 50)
    
    # Conectar aos bancos
    sqlite_conn = conectar_sqlite()
    if not sqlite_conn:
        return
    
    postgres_conn = conectar_postgres()
    if not postgres_conn:
        sqlite_conn.close()
        return
    
    try:
        # Verificar se o arquivo SQLite existe
        if not os.path.exists('estoque.db'):
            print("❌ Arquivo estoque.db não encontrado")
            return
        
        # Executar migração
        print("\n📦 Migrando produtos...")
        migrar_produtos(sqlite_conn, postgres_conn)
        
        print("\n🛒 Migrando pedidos...")
        migrar_pedidos(sqlite_conn, postgres_conn)
        
        print("\n🔍 Verificando migração...")
        verificar_migracao(postgres_conn)
        
        print("\n🎉 Migração concluída!")
        print("\n💡 Próximos passos:")
        print("   1. Teste a aplicação com o novo banco")
        print("   2. Faça backup do banco PostgreSQL")
        print("   3. Remova o arquivo estoque.db se não for mais necessário")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
    
    finally:
        # Fechar conexões
        sqlite_conn.close()
        postgres_conn.close()
        print("\n🔒 Conexões fechadas")

if __name__ == "__main__":
    main() 