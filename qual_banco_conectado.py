import psycopg2
import os

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


def get_connection():
    """
    Retorna uma conexão com o banco:
    - se existir DATABASE_URL -> usa Neon
    - senão -> usa banco local
    """
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


# =========================
# NOVA FUNÇÃO (RETORNA DADOS)
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


# =========================
# FUNÇÃO ANTIGA (TERMINAL)
# =========================

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
# TESTE DE CONEXÃO
# =========================

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conectado ao banco com sucesso!\n")

        print_info_conexao(conn)

        conn.close()

    except Exception as e:
        print("❌ Erro ao conectar:", e)
