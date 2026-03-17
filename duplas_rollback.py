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
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


# =========================
# FUNÇÃO DE ROLLBACK DUPLAS
# =========================

def rollback_duplas(ano, rodada):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        print(f"\n⚠️ Iniciando rollback DUPLAS: Ano {ano} - Rodada {rodada}")

        # =========================
        # VERIFICAR SITUAÇÃO
        # =========================
        cursor.execute("""
            SELECT MAX(numero)
            FROM rodadas_duplas
            WHERE ano = %s
        """, (ano,))

        max_rodada = cursor.fetchone()[0]

        if max_rodada is None:
            print("❌ Nenhuma rodada de duplas encontrada.")
            return

        if rodada > max_rodada:
            print(f"❌ Rodada {rodada} não existe. Última rodada é {max_rodada}.")
            return

        print(f"\n⚠️ ATENÇÃO!")
        print(f"Rodada atual: {max_rodada}")
        print(f"Vai apagar da rodada {rodada} até {max_rodada}")

        confirmacao = input("Digite 'SIM' para continuar: ")

        if confirmacao != "SIM":
            print("❌ Operação cancelada.")
            return

        # =========================
        # 1. DELETAR PONTUAÇÕES
        # =========================
        print("🧹 Removendo pontuações...")

        cursor.execute("""
            DELETE FROM duplas_times_pontuacoes
            WHERE rodada_id IN (
                SELECT id FROM rodadas_duplas
                WHERE ano = %s AND numero >= %s
            )
        """, (ano, rodada))

        # =========================
        # 2. DELETAR RODADAS
        # =========================
        print("🧹 Removendo rodadas...")

        cursor.execute("""
            DELETE FROM rodadas_duplas
            WHERE ano = %s AND numero >= %s
        """, (ano, rodada))

        conn.commit()

        print("\n✅ Rollback de duplas realizado com sucesso!")

    except Exception as e:
        conn.rollback()
        print("\n❌ Erro:")
        print(e)

    finally:
        cursor.close()
        conn.close()


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    try:
        ano = int(input("Ano: "))
        rodada = int(input("Rodada para rollback (duplas): "))

        rollback_duplas(ano, rodada)

    except ValueError:
        print("❌ Entrada inválida.")