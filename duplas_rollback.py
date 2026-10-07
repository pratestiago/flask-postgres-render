from qual_banco_conectado import get_connection


# =========================
# FUNÇÃO DE ROLLBACK DUPLAS
# =========================
def rollback_duplas(ano, rodada):

    # =========================
    # PROTEÇÃO
    # =========================
    if rodada < 20:
        print("❌ Rollback bloqueado.")
        print("Só é permitido fazer rollback da rodada 20 em diante.")
        return

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
            print(
                f"❌ Rodada {rodada} não existe. "
                f"Última rodada é {max_rodada}."
            )
            return

        rodada_limite = rodada - 1

        print("\n⚠️ ATENÇÃO!")
        print(f"Rodada atual: {max_rodada}")
        print(f"Vai apagar da rodada {rodada} até {max_rodada}")
        print(f"O sistema voltará para a rodada {rodada_limite}")

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
                SELECT id
                FROM rodadas_duplas
                WHERE ano = %s
                  AND numero >= %s
            )
        """, (ano, rodada))

        # =========================
        # 2. DELETAR RODADAS
        # =========================
        print("🧹 Removendo rodadas...")

        cursor.execute("""
            DELETE FROM rodadas_duplas
            WHERE ano = %s
              AND numero >= %s
        """, (ano, rodada))

        # =========================
        # FINALIZAR
        # =========================
        conn.commit()

        print("\n✅ Rollback de duplas realizado com sucesso!")
        print(f"📊 Sistema voltou para a rodada {rodada_limite}")

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