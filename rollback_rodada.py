from qual_banco_conectado import get_connection


# =========================
# FUNÇÃO DE ROLLBACK
# =========================
def rollback_rodada(ano, rodada):
    
    if rodada < 20:
        print("❌ Rollback bloqueado.")
        print("Só é permitido fazer rollback da rodada 20 em diante.")
        return    

    conn = get_connection()
    cursor = conn.cursor()

    try:
        print(f"\n⚠️ Iniciando rollback: Ano {ano} - Rodada {rodada}")

        # =========================
        # DEFINIR LIMITE REAL
        # =========================
        # Exemplo: rollback(21) → volta para a rodada 20
        rodada_limite = rodada - 1

        # =========================
        # VERIFICAR SITUAÇÃO ATUAL
        # =========================
        cursor.execute("""
            SELECT MAX(numero)
            FROM rodadas
            WHERE ano = %s
        """, (ano,))

        max_rodada = cursor.fetchone()[0]

        print(f"\n⚠️ ATENÇÃO!")
        print(f"Rodada atual no banco: {max_rodada}")
        print(f"O sistema voltará para a rodada {rodada_limite}")

        confirmacao = input("Digite 'SIM' para continuar: ")

        if confirmacao != "SIM":
            print("❌ Operação cancelada.")
            return

        # =========================
        # 1. LIMPAR MATA-MATA
        # =========================
        print("🧹 Limpando Mata-Matas...")

        cursor.execute("""
            DELETE FROM competicao_confrontos
            WHERE rodada > %s
            AND competicao_id NOT IN (
                SELECT id
                FROM competicoes
                WHERE tipo = 'champions'
                    AND ano = %s
            )
        """, (rodada_limite, ano))
        
        cursor.execute("""
            DELETE FROM competicao_fases
            WHERE rodada > %s
            AND competicao_id NOT IN (
                SELECT id
                FROM competicoes
                WHERE tipo = 'champions'
                    AND ano = %s
            )
        """, (rodada_limite, ano))
                
        
        # =========================
        # JOGOS DE IDA E VOLTA
        # =========================
        print("🧹 Limpando jogos de ida e volta...")

        cursor.execute("""
            DELETE FROM competicao_confronto_jogos
            WHERE rodada_id IN (
                SELECT id
                FROM rodadas
                WHERE ano = %s
                AND numero > %s
            )
        """, (ano, rodada_limite))


        # =========================
        # 2. LIMPAR RESULTADOS
        # =========================
        print("🧹 Limpando resultados...")

        cursor.execute("""
            DELETE FROM resultado_rodada
            WHERE rodada_id IN (
                SELECT id FROM rodadas
                WHERE ano = %s AND numero > %s
            )
        """, (ano, rodada_limite))

        # =========================
        # 3. LIMPAR RODADAS
        # =========================
        print("🧹 Removendo rodadas...")

        cursor.execute("""
            DELETE FROM rodadas
            WHERE ano = %s AND numero > %s
        """, (ano, rodada_limite))

        # =========================
        # 4. AJUSTAR COPA MUNDO
        # =========================
        print("🧹 Ajustando Copa Mundo...")

        # 🔴 Se voltou antes do mata-mata → remove tudo
        if rodada_limite <= 14:
            cursor.execute("""
                DELETE FROM competicao_confrontos
                WHERE competicao_id = 4
            """)
            cursor.execute("""
                DELETE FROM competicao_fases
                WHERE competicao_id = 4
            """)

        # 🔴 Se voltou antes do fim dos grupos → limpar resultados
        if rodada_limite <= 13:
            cursor.execute("""
                UPDATE copamundo_jogos
                SET pontos_a = NULL,
                    pontos_b = NULL
                WHERE ano = %s AND rodada > %s
            """, (ano, rodada_limite))

        # 🔴 Se voltou antes do início dos grupos → remover jogos
        if rodada_limite <= 11:
            cursor.execute("""
                DELETE FROM copamundo_jogos
                WHERE ano = %s
            """, (ano,))

        # 🔴 Se voltou antes da repescagem → remover tudo
        if rodada_limite <= 10:
            cursor.execute("""
                DELETE FROM copamundo_repescagem
                WHERE ano = %s
            """, (ano,))

            cursor.execute("""
                DELETE FROM copamundo_grupos
                WHERE ano = %s
            """, (ano,))
            
        # =========================
        # 5. AJUSTAR CHAMPIONS
        # =========================
        print("🧹 Ajustando Champions...")

        # Voltou para antes da volta da repescagem.
        # Mantém o jogo de ida, mas remove o agregado,
        # vencedor e perdedor definidos na rodada 22.
        if rodada_limite < 22:
            cursor.execute("""
                UPDATE competicao_confrontos
                SET status = 'em_andamento',
                    pontuacao_a = NULL,
                    pontuacao_b = NULL,
                    vencedor_id = NULL,
                    perdedor_id = NULL
                WHERE competicao_id IN (
                    SELECT id
                    FROM competicoes
                    WHERE tipo = 'champions'
                      AND ano = %s
                )
                  AND fase_id IN (
                    SELECT cf.id
                    FROM competicao_fases cf
                    JOIN competicoes c
                      ON c.id = cf.competicao_id
                    WHERE c.tipo = 'champions'
                      AND c.ano = %s
                      AND LOWER(cf.nome_fase) = 'repescagem'
                )
            """, (ano, ano))
            
            cursor.execute("""
                DELETE FROM champions_grupo_jogos
                WHERE competicao_id IN (
                    SELECT id
                    FROM competicoes
                    WHERE tipo = 'champions'
                    AND ano = %s
                )
            """, (ano,))

            cursor.execute("""
                DELETE FROM champions_grupos
                WHERE competicao_id IN (
                    SELECT id
                    FROM competicoes
                    WHERE tipo = 'champions'
                      AND ano = %s
                )
            """, (ano,))

            print("🧹 Volta, agregado e grupos da Champions removidos.")

        # Voltou para antes da ida da repescagem.
        # Mantém os confrontos, mas restaura o estado inicial.
        if rodada_limite < 21:
            cursor.execute("""
                UPDATE competicao_confrontos
                SET status = 'criado',
                    pontuacao_a = NULL,
                    pontuacao_b = NULL,
                    vencedor_id = NULL,
                    perdedor_id = NULL
                WHERE competicao_id IN (
                    SELECT id
                    FROM competicoes
                    WHERE tipo = 'champions'
                      AND ano = %s
                )
                  AND fase_id IN (
                    SELECT cf.id
                    FROM competicao_fases cf
                    JOIN competicoes c
                      ON c.id = cf.competicao_id
                    WHERE c.tipo = 'champions'
                      AND c.ano = %s
                      AND LOWER(cf.nome_fase) = 'repescagem'
                )
            """, (ano, ano))

        # Voltou para antes da classificação inicial.
        # Remove confrontos e participantes da Champions.
        if rodada_limite < 20:
            cursor.execute("""
                DELETE FROM competicao_confrontos
                WHERE competicao_id IN (
                    SELECT id
                    FROM competicoes
                    WHERE tipo = 'champions'
                      AND ano = %s
                )
            """, (ano,))

            cursor.execute("""
                DELETE FROM competicao_times
                WHERE competicao_id IN (
                    SELECT id
                    FROM competicoes
                    WHERE tipo = 'champions'
                      AND ano = %s
                )
            """, (ano,))

            print("🧹 Confrontos e participantes da Champions removidos.")

        # =========================
        # 6. BUSCAR ÚLTIMA RODADA
        # =========================
        cursor.execute("""
            SELECT MAX(numero)
            FROM rodadas
            WHERE ano = %s
        """, (ano,))

        ultima_rodada = cursor.fetchone()[0]
        
        

        # =========================
        # 7. REPROCESSAR
        # =========================
        if ultima_rodada:
            print(f"🔄 Reprocessando rodada {ultima_rodada}...")

            from copabrasil_v2 import processar_copa_brasil
            from copamundo import processar_copa_mundo

            processar_copa_brasil(conn, ano, ultima_rodada)
            processar_copa_mundo(conn, ano, ultima_rodada)

        # =========================
        # FINALIZAR
        # =========================
        conn.commit()

        print("\n✅ Rollback realizado com sucesso!")
        print(f"📊 Sistema voltou para a rodada {ultima_rodada}")

    except Exception as e:
        conn.rollback()
        print("\n❌ Erro durante rollback:")
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
        rodada = int(input("Rodada para rollback: "))

        rollback_rodada(ano, rodada)

    except ValueError:
        print("❌ Entrada inválida.")