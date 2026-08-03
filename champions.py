# champions.py


def processar_champions(conn, ano, rodada):

    if rodada not in (20, 21):
        return

    cursor = conn.cursor()

    try:

        if rodada == 20:

            ranking = buscar_ranking(cursor, ano, rodada)

            if len(ranking) != 83:
                raise RuntimeError(
                    f"Esperados 83 times, mas foram encontrados {len(ranking)}."
                )

            diretos = ranking[:45]
            repescagem = ranking[45:]

            print(f"[Champions] Classificados diretamente: {len(diretos)}")
            print(f"[Champions] Times na repescagem: {len(repescagem)}")

            gravar_classificacao_inicial(
                cursor,
                ano,
                diretos,
                repescagem
            )

            criar_repescagem(
                cursor,
                ano
            )

        elif rodada == 21:

            processar_ida_repescagem(
                cursor,
                ano
            )

    finally:
        cursor.close()


def buscar_ranking(cursor, ano, rodada):
    """
    Retorna o ranking usando somente os pontos da rodada informada.
    """

    cursor.execute(
        """
        SELECT
            t.id AS time_id,
            t.nome_time,
            rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r
            ON r.id = rr.rodada_id
        JOIN times t
            ON t.id = rr.time_id
        WHERE r.ano = %s
          AND r.numero = %s
          AND t.temporada = %s
        ORDER BY
            rr.pontos DESC,
            t.id
        """,
        (ano, rodada, ano),
    )

    return cursor.fetchall()


def gravar_classificacao_inicial(cursor, ano, diretos, repescagem):
    """
    Grava os 83 participantes da Champions em competicao_times.
    """

    cursor.execute(
        """
        SELECT id
        FROM competicoes
        WHERE tipo = 'champions'
          AND ano = %s
        ORDER BY id
        LIMIT 1
        """,
        (ano,),
    )

    competicao = cursor.fetchone()

    if not competicao:
        raise RuntimeError(
            f"Champions do ano {ano} não encontrada."
        )

    competicao_id = competicao[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM competicao_times
        WHERE competicao_id = %s
        """,
        (competicao_id,),
    )

    total_existente = cursor.fetchone()[0]

    if total_existente > 0:
        raise RuntimeError(
            f"A Champions {ano} já possui "
            f"{total_existente} times cadastrados."
        )

    for posicao, time in enumerate(diretos, start=1):
        time_id, nome_time, pontos = time

        cursor.execute(
            """
            INSERT INTO competicao_times (
                competicao_id,
                time_id,
                ranking_inicial,
                status,
                rodada_eliminacao,
                classificacao_final
            )
            VALUES (%s, %s, %s, 'direto', NULL, NULL)
            """,
            (
                competicao_id,
                time_id,
                posicao,
            ),
        )

    for posicao, time in enumerate(repescagem, start=46):
        time_id, nome_time, pontos = time

        cursor.execute(
            """
            INSERT INTO competicao_times (
                competicao_id,
                time_id,
                ranking_inicial,
                status,
                rodada_eliminacao,
                classificacao_final
            )
            VALUES (%s, %s, %s, 'repescagem', NULL, NULL)
            """,
            (
                competicao_id,
                time_id,
                posicao,
            ),
        )

    print("[Champions] 83 participantes gravados em competicao_times.")
    
    
    
def criar_repescagem(cursor, ano):
    """
    Cria os 19 confrontos da repescagem da Champions.
    """

    cursor.execute(
        """
        SELECT
            c.id,
            cf.id,
            cf.rodada
        FROM competicoes c
        JOIN competicao_fases cf
            ON cf.competicao_id = c.id
        WHERE c.tipo = 'champions'
        AND c.ano = %s
        AND LOWER(cf.nome_fase) = 'repescagem'
        ORDER BY c.id, cf.id
        LIMIT 1
        """,
        (ano,),
    )

    dados = cursor.fetchone()

    if not dados:
        raise RuntimeError(
            f"Fase repescagem da Champions {ano} não encontrada."
        )

    competicao_id, fase_id, rodada_repescagem = dados

    cursor.execute(
        """
        SELECT
            ct.time_id,
            ct.ranking_inicial
        FROM competicao_times ct
        WHERE ct.competicao_id = %s
          AND ct.status = 'repescagem'
        ORDER BY ct.ranking_inicial
        """,
        (competicao_id,),
    )

    times = cursor.fetchall()

    if len(times) != 38:
        raise RuntimeError(
            "Esperados 38 times para a repescagem, "
            f"mas foram encontrados {len(times)}."
        )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM competicao_confrontos
        WHERE competicao_id = %s
          AND fase_id = %s
        """,
        (competicao_id, fase_id),
    )

    total_existente = cursor.fetchone()[0]

    if total_existente > 0:
        raise RuntimeError(
            f"A repescagem já possui {total_existente} confrontos."
        )

    for indice in range(19):
        time_a_id, ranking_a = times[indice]
        time_b_id, ranking_b = times[-(indice + 1)]

        cursor.execute(
            """
            INSERT INTO competicao_confrontos (
                competicao_id,
                fase_id,
                rodada,
                time_a_id,
                time_b_id,
                ranking_a,
                ranking_b,
                pontuacao_a,
                pontuacao_b,
                vencedor_id,
                perdedor_id,
                status,
                origem_time_a_confronto_id,
                origem_time_b_confronto_id,
                ordem_na_fase,
                lado_chave
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                NULL, NULL, NULL, NULL,
                'criado',
                NULL, NULL,
                %s,
                NULL
            )
            """,
            (
                competicao_id,
                fase_id,
                rodada_repescagem,
                time_a_id,
                time_b_id,
                ranking_a,
                ranking_b,
                indice + 1,
            ),
        )

    print("[Champions] 19 confrontos da repescagem criados.")
    
def processar_ida_repescagem(cursor, ano):
    """
    Processa a ida da repescagem da Champions.
    """

    print("[Champions] Processando ida da repescagem...")

    # Localiza a competição e a fase da repescagem
    cursor.execute(
        """
        SELECT
            c.id,
            cf.id
        FROM competicoes c
        JOIN competicao_fases cf
            ON cf.competicao_id = c.id
        WHERE c.tipo = 'champions'
          AND c.ano = %s
          AND LOWER(cf.nome_fase) = 'repescagem'
        LIMIT 1
        """,
        (ano,),
    )

    dados = cursor.fetchone()

    if not dados:
        raise RuntimeError(
            f"Repescagem da Champions {ano} não encontrada."
        )

    competicao_id, fase_id = dados

    # Busca a rodada 21
    cursor.execute(
        """
        SELECT id
        FROM rodadas
        WHERE ano = %s
          AND numero = 21
        """,
        (ano,),
    )

    rodada = cursor.fetchone()

    if not rodada:
        raise RuntimeError(
            f"Rodada 21 do ano {ano} não encontrada."
        )

    rodada_id = rodada[0]

    # Busca os 19 confrontos da repescagem
    cursor.execute(
        """
        SELECT
            id,
            time_a_id,
            time_b_id
        FROM competicao_confrontos
        WHERE competicao_id = %s
          AND fase_id = %s
        ORDER BY ordem_na_fase
        """,
        (competicao_id, fase_id),
    )

    confrontos = cursor.fetchall()

    if len(confrontos) != 19:
        raise RuntimeError(
            f"Esperados 19 confrontos, encontrados {len(confrontos)}."
        )

    # Grava a pontuação da ida de cada confronto
    for confronto_id, time_a_id, time_b_id in confrontos:

        cursor.execute(
            """
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s
              AND time_id = %s
            """,
            (rodada_id, time_a_id),
        )

        pontos_a = cursor.fetchone()

        if not pontos_a:
            raise RuntimeError(
                f"Pontuação não encontrada para o time {time_a_id}."
            )

        cursor.execute(
            """
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s
              AND time_id = %s
            """,
            (rodada_id, time_b_id),
        )

        pontos_b = cursor.fetchone()

        if not pontos_b:
            raise RuntimeError(
                f"Pontuação não encontrada para o time {time_b_id}."
            )

        cursor.execute(
            """
            INSERT INTO competicao_confronto_jogos (
                confronto_id,
                rodada_id,
                ordem,
                pontuacao_a,
                pontuacao_b,
                processado_em
            )
            VALUES (%s, %s, 1, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (confronto_id, ordem)
            DO UPDATE SET
                rodada_id = EXCLUDED.rodada_id,
                pontuacao_a = EXCLUDED.pontuacao_a,
                pontuacao_b = EXCLUDED.pontuacao_b,
                processado_em = CURRENT_TIMESTAMP
            """,
            (
                confronto_id,
                rodada_id,
                pontos_a[0],
                pontos_b[0],
            ),
        )

    # Marca todos os confrontos como em andamento
    cursor.execute(
        """
        UPDATE competicao_confrontos
        SET status = 'em_andamento'
        WHERE competicao_id = %s
          AND fase_id = %s
        """,
        (competicao_id, fase_id),
    )

    print("[Champions] Ida da repescagem processada.")