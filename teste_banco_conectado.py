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


def print_info_conexao(conn):
    """
    Imprime informações para SABER em qual banco estamos conectados.
    Isso é essencial antes de inserir ou apagar dados.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            current_database(),
            current_user,
            inet_server_addr()
    """)
    banco, usuario, host = cursor.fetchone()

    print("📡 INFORMAÇÕES DA CONEXÃO")
    print(f"Banco   : {banco}")
    print(f"Usuário : {usuario}")
    print(f"Host    : {host}")

    cursor.close()


# =========================
# TESTE DE CONEXÃO
# =========================

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conectado ao banco com sucesso!\n")

        # >>> AQUI entra a função nova <<<
        print_info_conexao(conn)

        conn.close()
    except Exception as e:
        print("❌ Erro ao conectar:", e)
