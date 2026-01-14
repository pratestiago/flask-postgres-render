# =========================
# FUNÇÕES AUXILIARES
# =========================

def eh_potencia_de_2(n):
    return n > 0 and (n & (n - 1)) == 0


def maior_potencia_de_2(n):
    p = 1
    while p * 2 <= n:
        p *= 2
    return p
# =========================
# MAPA DAS FASES PRINCIPAIS
# =========================

def obter_fase_principal(numero_rodada):
    """
    Retorna informações da fase principal da Copa Brasil
    com base no número da rodada.
    """
    fases = {
        4: ('16-avos', 64, 32, 2),
        5: ('oitavas', 32, 16, 3),
        6: ('quartas', 16, 8, 4),
        7: ('semifinal', 8, 4, 5),
        8: ('final', 4, 2, 6)
    }

    return fases.get(numero_rodada)

# =========================
# CRIAR CONFRONTOS DA FASE PRINCIPAL
# =========================

def criar_confrontos_fase_principal(
    cursor,
    competicao_id,
    nome_fase,
    rodada,
    qtd_times_inicio,
    qtd_times_fim,
    ordem_fase
):
    print(f'[Copa Brasil] Criando confrontos da fase {nome_fase}')

    # 1️⃣ Buscar times vivos ordenados pelo ranking
    cursor.execute("""
        SELECT
            ct.time_id,
            ct.ranking_inicial,
            t.nome_time
        FROM competicao_times ct
        JOIN times t ON t.id = ct.time_id
        WHERE ct.competicao_id = %s
          AND ct.status = 'vivo'
        ORDER BY ct.ranking_inicial
    """, (competicao_id,))

    times = cursor.fetchall()

    if len(times) != qtd_times_inicio:
        raise Exception(
            f'[Copa Brasil] Esperado {qtd_times_inicio} times vivos, '
            f'mas encontrei {len(times)}'
        )

    # 2️⃣ Criar a fase
    cursor.execute("""
        INSERT INTO competicao_fases (
            competicao_id,
            nome_fase,
            ordem,
            qtd_times_inicio,
            qtd_times_fim,
            rodada,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'em_andamento')
        RETURNING id
    """, (
        competicao_id,
        nome_fase,
        ordem_fase,
        qtd_times_inicio,
        qtd_times_fim,
        rodada
    ))

    fase_id = cursor.fetchone()[0]

    # 3️⃣ Criar os confrontos (1 x último)
    total = len(times)

    for i in range(total // 2):
        time_a = times[i]
        time_b = times[total - 1 - i]

        time_a_id, ranking_a, nome_a = time_a
        time_b_id, ranking_b, nome_b = time_b

        print(
            f'  Confronto: '
            f'[{ranking_a}] {nome_a} x '
            f'[{ranking_b}] {nome_b}'
        )

        cursor.execute("""
            INSERT INTO competicao_confrontos (
                competicao_id,
                fase_id,
                rodada,
                time_a_id,
                time_b_id,
                ranking_a,
                ranking_b,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'criado')
        """, (
            competicao_id,
            fase_id,
            rodada,
            time_a_id,
            time_b_id,
            ranking_a,
            ranking_b
        ))

# =========================
# RESOLVER FASE PRINCIPAL
# =========================

def resolver_fase_principal(
    cursor,
    competicao_id,
    nome_fase,
    rodada,
    ano
):
    print(f'[Copa Brasil] Resolvendo fase {nome_fase}')

    cursor.execute("""
        SELECT
            cc.id,
            cc.time_a_id,
            cc.time_b_id,
            cc.ranking_a,
            cc.ranking_b
        FROM competicao_confrontos cc
        JOIN competicao_fases cf ON cf.id = cc.fase_id
        WHERE cc.competicao_id = %s
          AND cc.rodada = %s
          AND cf.nome_fase = %s
          AND cc.status = 'criado'
    """, (competicao_id, rodada, nome_fase))

    confrontos = cursor.fetchall()

    for (
        confronto_id,
        time_a_id,
        time_b_id,
        ranking_a,
        ranking_b
    ) in confrontos:

        cursor.execute("""
            SELECT rr.time_id, rr.pontos
            FROM resultado_rodada rr
            JOIN rodadas r ON r.id = rr.rodada_id
            WHERE r.ano = %s
              AND r.numero = %s
              AND rr.time_id IN (%s, %s)
        """, (ano, rodada, time_a_id, time_b_id))

        resultados = dict(cursor.fetchall())

        pa = resultados.get(time_a_id, 0)
        pb = resultados.get(time_b_id, 0)

        if pa > pb:
            vencedor, perdedor = time_a_id, time_b_id
        elif pb > pa:
            vencedor, perdedor = time_b_id, time_a_id
        else:
            vencedor = (
                time_a_id
                if ranking_a < ranking_b
                else time_b_id
            )
            perdedor = (
                time_b_id
                if vencedor == time_a_id
                else time_a_id
            )

        cursor.execute("""
            UPDATE competicao_confrontos
            SET
                pontuacao_a = %s,
                pontuacao_b = %s,
                vencedor_id = %s,
                perdedor_id = %s,
                status = 'finalizado'
            WHERE id = %s
        """, (pa, pb, vencedor, perdedor, confronto_id))

        cursor.execute("""
            UPDATE competicao_times
            SET
                status = 'eliminado',
                rodada_eliminacao = %s
            WHERE competicao_id = %s
              AND time_id = %s
        """, (rodada, competicao_id, perdedor))

    print(f'[Copa Brasil] Fase {nome_fase} resolvida com sucesso')

    # =========================
# CRIAR FINALÍSSIMA (RODADA 9)
# =========================

def criar_finalissima(cursor, competicao_id):
    print('[Copa Brasil] Criando FINALÍSSIMA (rodada 9)')

    # Buscar os 2 times vivos
    cursor.execute("""
        SELECT
            ct.time_id,
            ct.ranking_inicial,
            t.nome_time
        FROM competicao_times ct
        JOIN times t ON t.id = ct.time_id
        WHERE ct.competicao_id = %s
          AND ct.status = 'vivo'
        ORDER BY ct.ranking_inicial
    """, (competicao_id,))

    times = cursor.fetchall()

    if len(times) != 2:
        raise Exception(
            f'[Copa Brasil] Finalíssima exige 2 times vivos, '
            f'mas encontrei {len(times)}'
        )

    (time_a_id, ranking_a, nome_a), (time_b_id, ranking_b, nome_b) = times

    print(f'  Final: [{ranking_a}] {nome_a} x [{ranking_b}] {nome_b}')

    # Criar fase finalíssima
    cursor.execute("""
        INSERT INTO competicao_fases (
            competicao_id,
            nome_fase,
            ordem,
            qtd_times_inicio,
            qtd_times_fim,
            rodada,
            status
        )
        VALUES (%s, 'finalissima', 7, 2, 1, 9, 'em_andamento')
        RETURNING id
    """, (competicao_id,))

    fase_id = cursor.fetchone()[0]

    # Criar confronto único
    cursor.execute("""
        INSERT INTO competicao_confrontos (
            competicao_id,
            fase_id,
            rodada,
            time_a_id,
            time_b_id,
            ranking_a,
            ranking_b,
            status
        )
        VALUES (%s, %s, 9, %s, %s, %s, %s, 'criado')
    """, (
        competicao_id,
        fase_id,
        time_a_id,
        time_b_id,
        ranking_a,
        ranking_b
    ))

# =========================
# RESOLVER FINALÍSSIMA (RODADA 9)
# =========================

def resolver_finalissima(cursor, competicao_id, ano):
    print('[Copa Brasil] Resolvendo FINALÍSSIMA (rodada 9)')

    cursor.execute("""
        SELECT
            cc.id,
            cc.time_a_id,
            cc.time_b_id,
            cc.ranking_a,
            cc.ranking_b
        FROM competicao_confrontos cc
        JOIN competicao_fases cf ON cf.id = cc.fase_id
        WHERE cc.competicao_id = %s
          AND cc.rodada = 9
          AND cf.nome_fase = 'finalissima'
          AND cc.status = 'criado'
    """, (competicao_id,))

    confronto = cursor.fetchone()

    if not confronto:
        print('[Copa Brasil] Nenhuma finalíssima pendente')
        return

    confronto_id, time_a_id, time_b_id, ranking_a, ranking_b = confronto

    # Buscar pontuação da FINALÍSSIMA (rodada 9)
    cursor.execute("""
        SELECT rr.time_id, rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE r.ano = %s
          AND r.numero = 9
          AND rr.time_id IN (%s, %s)
    """, (ano, time_a_id, time_b_id))


    resultados = dict(cursor.fetchall())

    pa = resultados.get(time_a_id, 0)
    pb = resultados.get(time_b_id, 0)

    if pa > pb:
        campeao, vice = time_a_id, time_b_id
    elif pb > pa:
        campeao, vice = time_b_id, time_a_id
    else:
        campeao = time_a_id if ranking_a < ranking_b else time_b_id
        vice = time_b_id if campeao == time_a_id else time_a_id

    # Atualizar confronto
    cursor.execute("""
        UPDATE competicao_confrontos
        SET
            pontuacao_a = %s,
            pontuacao_b = %s,
            vencedor_id = %s,
            perdedor_id = %s,
            status = 'finalizado'
        WHERE id = %s
    """, (pa, pb, campeao, vice, confronto_id))

    # Atualizar times
    cursor.execute("""
        UPDATE competicao_times
        SET status = 'campeao'
        WHERE competicao_id = %s
          AND time_id = %s
    """, (competicao_id, campeao))

    cursor.execute("""
        UPDATE competicao_times
        SET status = 'vice'
        WHERE competicao_id = %s
          AND time_id = %s
    """, (competicao_id, vice))

    # Atualizar competição
    cursor.execute("""
        UPDATE competicoes
        SET status = 'finalizada'
        WHERE id = %s
    """, (competicao_id,))

    print('[Copa Brasil] CAMPEÃO e VICE definidos com sucesso')




# =========================
# PROCESSADOR DA COPA BRASIL
# =========================

def processar_copa_brasil(conn, ano, numero_rodada):
    cursor = conn.cursor()

    print(f'[Copa Brasil] Ano {ano} - Rodada {numero_rodada}')

    # Copa Brasil começa na rodada 2
    if numero_rodada < 2:
        print('[Copa Brasil] Rodada ignorada (Copa Brasil começa na rodada 2)')
        return

    # Verificar se existe Copa Brasil para o ano
    cursor.execute("""
        SELECT id, status
        FROM competicoes
        WHERE nome = 'Copa Brasil'
          AND ano = %s
    """, (ano,))
    row = cursor.fetchone()

    if not row:
        print('[Copa Brasil] Não existe Copa Brasil para esse ano')
        return

    competicao_id, status = row

    # Verificar se a rodada já foi processada
    cursor.execute("""
        SELECT 1
        FROM competicao_rodadas_processadas
        WHERE competicao_id = %s
          AND rodada = %s
    """, (competicao_id, numero_rodada))

    if cursor.fetchone():
        print('[Copa Brasil] Rodada já processada')
        return

    # ======================================================
    # RODADA 2 — RANKING + REPESCAGEM + CONFRONTOS
    # ======================================================
    if numero_rodada == 2:

        # -----------------------------
        # BUSCAR RANKING DA RODADA 2
        # -----------------------------
        cursor.execute("""
            SELECT
                t.id AS time_id,
                t.nome_time,
                rr.pontos
            FROM resultado_rodada rr
            JOIN rodadas r ON r.id = rr.rodada_id
            JOIN times t ON t.id = rr.time_id
            WHERE r.ano = %s
              AND r.numero = 2
              AND t.temporada = %s
            ORDER BY rr.pontos DESC
        """, (ano, ano))

        resultados = cursor.fetchall()

        print('[Copa Brasil] Ranking da Rodada 2:')
        posicao = 1
        for _, nome_time, pontos in resultados:
            print(f'{posicao:>3}º - {nome_time} ({pontos} pts)')
            posicao += 1

        # -----------------------------
        # SALVAR RANKING NO BANCO
        # -----------------------------
        posicao = 1
        for time_id, _, pontos in resultados:
            cursor.execute("""
                INSERT INTO competicao_ranking_snapshot (
                    competicao_id,
                    rodada,
                    time_id,
                    pontuacao,
                    posicao
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (competicao_id, 2, time_id, pontos, posicao))

            cursor.execute("""
                INSERT INTO competicao_times (
                    competicao_id,
                    time_id,
                    ranking_inicial,
                    status
                )
                VALUES (%s, %s, %s, 'vivo')
            """, (competicao_id, time_id, posicao))

            posicao += 1

        # Atualizar competição
        cursor.execute("""
            UPDATE competicoes
            SET status = 'ranking_definido',
                rodada_atual = 2
            WHERE id = %s
        """, (competicao_id,))

        # Marcar rodada como processada
        cursor.execute("""
            INSERT INTO competicao_rodadas_processadas (
                competicao_id,
                rodada
            )
            VALUES (%s, %s)
        """, (competicao_id, numero_rodada))

        conn.commit()
        print('[Copa Brasil] Ranking da rodada 2 SALVO com sucesso')

        # -----------------------------
        # DECIDIR REPESCAGEM
        # -----------------------------
        cursor.execute("""
            SELECT COUNT(*)
            FROM competicao_times
            WHERE competicao_id = %s
        """, (competicao_id,))

        total_times = cursor.fetchone()[0]
        print(f'[Copa Brasil] Total de times: {total_times}')

        if eh_potencia_de_2(total_times):
            print('[Copa Brasil] Quantidade é potência de 2 — sem repescagem')
            return

        print('[Copa Brasil] Quantidade NÃO é potência de 2 — haverá repescagem')

        alvo = maior_potencia_de_2(total_times)
        excedente = total_times - alvo
        times_repescagem = excedente * 2
        times_direto = total_times - times_repescagem

        print(f'[Copa Brasil] Alvo pós-repescagem: {alvo} times')
        print(f'[Copa Brasil] Times na repescagem: {times_repescagem}')
        print(f'[Copa Brasil] Times que passam direto: {times_direto}')

        # -----------------------------
        # DEFINIR TIMES DA REPESCAGEM
        # -----------------------------
        cursor.execute("""
            SELECT
                ct.time_id,
                ct.ranking_inicial,
                t.nome_time
            FROM competicao_times ct
            JOIN times t ON t.id = ct.time_id
            WHERE ct.competicao_id = %s
            ORDER BY ct.ranking_inicial DESC
            LIMIT %s
        """, (competicao_id, times_repescagem))

        times_repescagem_lista = cursor.fetchall()

        print('[Copa Brasil] Times na REPESCAGEM:')
        for _, ranking, nome in times_repescagem_lista:
            print(f'  Ranking {ranking:>3} - {nome}')

        # -----------------------------
        # CRIAR CONFRONTOS DA REPESCAGEM (RODADA 3)
        # -----------------------------
        print('[Copa Brasil] Criando confrontos da REPESCAGEM (Rodada 3)')

        total_rep = len(times_repescagem_lista)

        for i in range(total_rep // 2):
            time_a = times_repescagem_lista[i]
            time_b = times_repescagem_lista[total_rep - 1 - i]

            time_a_id, ranking_a, _ = time_a
            time_b_id, ranking_b, _ = time_b

            # Criar fase se não existir
            cursor.execute("""
                SELECT id
                FROM competicao_fases
                WHERE competicao_id = %s
                  AND nome_fase = 'repescagem'
            """, (competicao_id,))
            fase = cursor.fetchone()

            if fase:
                fase_id = fase[0]
            else:
                cursor.execute("""
                    INSERT INTO competicao_fases (
                        competicao_id,
                        nome_fase,
                        ordem,
                        qtd_times_inicio,
                        qtd_times_fim,
                        rodada,
                        status
                    )
                    VALUES (%s, 'repescagem', 1, %s, %s, 3, 'em_andamento')
                    RETURNING id
                """, (
                    competicao_id,
                    times_repescagem,
                    times_repescagem // 2
                ))
                fase_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO competicao_confrontos (
                    competicao_id,
                    fase_id,
                    rodada,
                    time_a_id,
                    time_b_id,
                    ranking_a,
                    ranking_b,
                    status
                )
                VALUES (%s, %s, 3, %s, %s, %s, %s, 'criado')
            """, (
                competicao_id,
                fase_id,
                time_a_id,
                time_b_id,
                ranking_a,
                ranking_b
            ))

        conn.commit()
        print('[Copa Brasil] Confrontos da REPESCAGEM criados com sucesso')

    # ======================================================
    # RODADA 3 — RESOLVER REPESCAGEM
    # ======================================================
    elif numero_rodada == 3:

        print('[Copa Brasil] Resolvendo REPESCAGEM (Rodada 3)')

        cursor.execute("""
            SELECT
                cc.id,
                cc.time_a_id,
                cc.time_b_id,
                cc.ranking_a,
                cc.ranking_b
            FROM competicao_confrontos cc
            JOIN competicao_fases cf ON cf.id = cc.fase_id
            WHERE cc.competicao_id = %s
              AND cc.rodada = 3
              AND cf.nome_fase = 'repescagem'
              AND cc.status = 'criado'
        """, (competicao_id,))

        confrontos = cursor.fetchall()

        for confronto_id, time_a_id, time_b_id, ranking_a, ranking_b in confrontos:

            cursor.execute("""
                SELECT rr.time_id, rr.pontos
                FROM resultado_rodada rr
                JOIN rodadas r ON r.id = rr.rodada_id
                WHERE r.ano = %s
                  AND r.numero = 3
                  AND rr.time_id IN (%s, %s)
            """, (ano, time_a_id, time_b_id))

            resultados = cursor.fetchall()
            pontos = {t: p for t, p in resultados}

            pa = pontos.get(time_a_id, 0)
            pb = pontos.get(time_b_id, 0)

            if pa > pb:
                vencedor, perdedor = time_a_id, time_b_id
            elif pb > pa:
                vencedor, perdedor = time_b_id, time_a_id
            else:
                vencedor = time_a_id if ranking_a < ranking_b else time_b_id
                perdedor = time_b_id if vencedor == time_a_id else time_a_id

            cursor.execute("""
                UPDATE competicao_confrontos
                SET pontuacao_a = %s,
                    pontuacao_b = %s,
                    vencedor_id = %s,
                    perdedor_id = %s,
                    status = 'finalizado'
                WHERE id = %s
            """, (pa, pb, vencedor, perdedor, confronto_id))

            cursor.execute("""
                UPDATE competicao_times
                SET status = 'eliminado',
                    rodada_eliminacao = 3
                WHERE competicao_id = %s
                  AND time_id = %s
            """, (competicao_id, perdedor))

        conn.commit()
        print('[Copa Brasil] Repescagem RESOLVIDA com sucesso')

         # ======================================================
    # RODADA 4 — 16-AVOS (CRIAR + RESOLVER)
    # ======================================================
    elif numero_rodada == 4:
        print('[Copa Brasil] Fase 16-avos — criando e resolvendo')

        fase = obter_fase_principal(numero_rodada)
        nome_fase, qtd_ini, qtd_fim, ordem = fase

        criar_confrontos_fase_principal(
            cursor,
            competicao_id,
            nome_fase,
            numero_rodada,
            qtd_ini,
            qtd_fim,
            ordem
        )

        resolver_fase_principal(
            cursor,
            competicao_id,
            nome_fase,
            numero_rodada,
            ano
        )

        cursor.execute("""
            INSERT INTO competicao_rodadas_processadas (
                competicao_id,
                rodada
            )
            VALUES (%s, %s)
        """, (competicao_id, numero_rodada))

        cursor.execute("""
            UPDATE competicoes
            SET rodada_atual = %s
            WHERE id = %s
        """, (numero_rodada, competicao_id))

        conn.commit()
        print('[Copa Brasil] Fase 16-avos concluída (64 → 32)')
        return
    
        # ======================================================
    # RODADA 9 — FINALÍSSIMA (CAMPEÃO E VICE)
    # ======================================================
    elif numero_rodada == 9:

        print('[Copa Brasil] Rodada 9 — FINALÍSSIMA')

        resolver_finalissima(
            cursor,
            competicao_id,
            ano
        )

        # Marcar rodada como processada
        cursor.execute("""
            INSERT INTO competicao_rodadas_processadas (
                competicao_id,
                rodada
            )
            VALUES (%s, %s)
        """, (competicao_id, numero_rodada))

        # Atualizar rodada atual
        cursor.execute("""
            UPDATE competicoes
            SET rodada_atual = %s
            WHERE id = %s
        """, (numero_rodada, competicao_id))

        conn.commit()

        print('[Copa Brasil] Copa Brasil FINALIZADA 🏆')
        return


    # ======================================================
    # FASES PRINCIPAIS AUTOMÁTICAS (RODADAS 5+)
    # ======================================================
    fase = obter_fase_principal(numero_rodada)

    if fase:
        nome_fase, qtd_ini, qtd_fim, ordem = fase

        print(f'[Copa Brasil] Fase {nome_fase} — rodada {numero_rodada}')

        criar_confrontos_fase_principal(
            cursor,
            competicao_id,
            nome_fase,
            numero_rodada,
            qtd_ini,
            qtd_fim,
            ordem
        )

        resolver_fase_principal(
            cursor,
            competicao_id,
            nome_fase,
            numero_rodada,
            ano
        )

        cursor.execute("""
            INSERT INTO competicao_rodadas_processadas (
                competicao_id,
                rodada
            )
            VALUES (%s, %s)
        """, (competicao_id, numero_rodada))

        cursor.execute("""
            UPDATE competicoes
            SET rodada_atual = %s
            WHERE id = %s
        """, (numero_rodada, competicao_id))

        conn.commit()

        print(f'[Copa Brasil] Fase {nome_fase} concluída')

                # 🏆 Se for a FINAL (rodada 8), criar FINALÍSSIMA
        if numero_rodada == 8:
            criar_finalissima(cursor, competicao_id)
            conn.commit()
            print('[Copa Brasil] Finalíssima (rodada 9) criada')

        return

    print('[Copa Brasil] Rodada ignorada pela Copa Brasil')
