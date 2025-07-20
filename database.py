from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Configuração do banco de dados PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Criar engine do SQLAlchemy para PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=300,    # Recicla conexões a cada 5 minutos
    echo=settings.DEBUG  # Log SQL em modo debug
)

# Criar sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Função para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar todas as tabelas
def create_tables():
    Base.metadata.create_all(bind=engine)

# Função para verificar conexão com o banco
def test_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Erro na conexão com o banco: {e}")
        return False 