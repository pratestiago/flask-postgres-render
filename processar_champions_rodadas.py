from qual_banco_conectado import get_connection, print_info_conexao
from champions import processar_champions


conn = get_connection()

try:
    print_info_conexao(conn)

    processar_champions(conn, 2026, 23)
    conn.commit()

    processar_champions(conn, 2026, 24)
    conn.commit()

    print("✅ Rodadas 23 e 24 processadas com sucesso.")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()