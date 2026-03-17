import psycopg2
import os

# =========================
# AMBIENTE
# =========================

AMBIENTE = os.getenv("AMBIENTE", "PROD")

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================

DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "4705"
}

DATABASE_URL = os.getenv("DATABASE_URL")


# =========================
# CONEXÃO PRINCIPAL
# =========================

def get_connection():
    """
    Retorna uma conexão com o banco:
    - TESTE -> banco postgres_teste
    - DATABASE_URL -> Neon (produção online)
    - senão -> banco local (produção)
    """

    # 🧪 TESTE (PRIORIDADE MÁXIMA)
    if AMBIENTE == "TESTE":
        print("🧪 Conectado ao BANCO DE TESTE")
        return psycopg2.connect(
            host="localhost",
            database="postgres_teste",
            user="postgres",
            password="4705"
        )

    # 🌐 NEON (produção online)
    if DATABASE_URL:
        print("🌐 Conectado ao BANCO NEON")
        return psycopg2.connect(DATABASE_URL)

    # 💻 PRODUÇÃO LOCAL
    print("🚀 Conectado ao BANCO LOCAL")
    return psycopg2.connect(**DB_CONFIG)


# =========================
# INFORMAÇÕES DA CONEXÃO
# =========================

def get_info_conexao(conn):
    """
    Retorna informações da conexão para uso em aplicações (ex: Flask).
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            current_database(),
            current_user,
            inet_server_addr()
    """)

    banco, usuario, host = cursor.fetchone()

    cursor.close()

    return banco, usuario, host


def print_info_conexao(conn):
    """
    Imprime informações da conexão no terminal.
    """
    banco, usuario, host = get_info_conexao(conn)

    print("📡 INFORMAÇÕES DA CONEXÃO")
    print(f"Banco   : {banco}")
    print(f"Usuário : {usuario}")
    print(f"Host    : {host}")


# =========================
# TESTE DIRETO (OPCIONAL)
# =========================

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conectado ao banco com sucesso!\n")

        print_info_conexao(conn)

        conn.close()

    except Exception as e:
        print("❌ Erro ao conectar:", e)