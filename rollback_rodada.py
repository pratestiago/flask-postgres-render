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
# FUNÇÃO DE ROLLBACK
# =========================

def rollback_rodada(ano, rodada):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        print(f"\n⚠️ Iniciando rollback: Ano {ano} - Rodada {rodada}")

        # =========================
        # 🔍 VERIFICAR SITUAÇÃO ATUAL
        # =========================
        cursor.execute("""
            SELECT MAX(numero)
            FROM rodadas
            WHERE ano = %s
        """, (ano,))

        max_rodada = cursor.fetchone()[0]

        print(f"\n⚠️ ATENÇÃO!")
        print(f"Rodada atual no banco: {max_rodada}")
        print(f"O rollback vai apagar da rodada {rodada} até {max_rodada}")

        confirmacao = input("Digite 'SIM' para continuar: ")

        if confirmacao != "SIM":
            print("❌ Operação cancelada.")
            return

        # =========================
        # 1. DELETAR COPA BRASIL
        # =========================
        print("🧹 Limpando Copa Brasil...")

        cursor.execute("""
            DELETE FROM competicao_confrontos
            WHERE rodada >= %s
        """, (rodada,))

        cursor.execute("""
            DELETE FROM competicao_fases
            WHERE rodada >= %s
        """, (rodada,))

        # =========================
        # 2. DELETAR RESULTADOS
        # =========================
        print("🧹 Limpando resultados...")

        cursor.execute("""
            DELETE FROM resultado_rodada
            WHERE rodada_id IN (
                SELECT id FROM rodadas
                WHERE ano = %s AND numero >= %s
            )
        """, (ano, rodada))

        # =========================
        # 3. DELETAR RODADAS
        # =========================
        print("🧹 Removendo rodadas...")

        cursor.execute("""
            DELETE FROM rodadas
            WHERE ano = %s AND numero >= %s
        """, (ano, rodada))

        # =========================
        # 4. BUSCAR ÚLTIMA RODADA
        # =========================
        cursor2 = conn.cursor()

        cursor2.execute("""
            SELECT MAX(numero)
            FROM rodadas
            WHERE ano = %s
        """, (ano,))

        ultima_rodada = cursor2.fetchone()[0]
        cursor2.close()

        # =========================
        # 5. REPROCESSAR COPA
        # =========================
        if ultima_rodada:
            print(f"🔄 Reprocessando rodada {ultima_rodada}...")

            from copabrasil_v2 import processar_copa_brasil
            processar_copa_brasil(conn, ano, ultima_rodada)

        # =========================
        # FINALIZAR
        # =========================
        conn.commit()

        print("\n✅ Rollback realizado com sucesso!")

        if ultima_rodada:
            print(f"📊 Sistema voltou para a rodada {ultima_rodada}")
        else:
            print("📊 Nenhuma rodada restante no banco")

    except Exception as e:
        conn.rollback()
        print("\n❌ Erro durante rollback:")
        print(e)

    finally:
        cursor.close()
        conn.close()


# =========================
# EXECUÇÃO VIA TERMINAL
# =========================

if __name__ == "__main__":
    try:
        ano = int(input("Ano: "))
        rodada = int(input("Rodada para rollback: "))

        rollback_rodada(ano, rodada)

    except ValueError:
        print("❌ Entrada inválida. Digite números.")