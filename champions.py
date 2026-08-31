# champions.py


def processar_champions(conn, ano, rodada):

    if rodada not in (20, 21, 22, 23, 24, 25, 26, 27, 28):
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

        elif rodada == 22:

            processar_volta_repescagem(
                cursor,
                ano
            )

            criar_grupos_champions(
                cursor,
                ano
            )

            criar_jogos_grupos_champions(
                cursor,
                ano
            )

        elif rodada in (23, 24, 25, 26, 27, 28):

            processar_rodada_grupos_champions(
                cursor,
                ano,
                rodada
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
    
    
def processar_volta_repescagem(cursor, ano):
    """
    Processa a volta da repescagem da Champions.

    Regras:
    - ida = rodada 21, ordem 1;
    - volta = rodada 22, ordem 2;
    - vencedor definido pela soma dos dois jogos;
    - em caso de empate, vence o melhor ranking da rodada 20.
    """

    print("[Champions] Processando volta da repescagem...")

    # =========================
    # LOCALIZAR COMPETIÇÃO E FASE
    # =========================
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

    # =========================
    # LOCALIZAR RODADA 22
    # =========================
    cursor.execute(
        """
        SELECT id
        FROM rodadas
        WHERE ano = %s
          AND numero = 22
        """,
        (ano,),
    )

    rodada = cursor.fetchone()

    if not rodada:
        raise RuntimeError(
            f"Rodada 22 do ano {ano} não encontrada."
        )

    rodada_id = rodada[0]

    # =========================
    # BUSCAR CONFRONTOS
    # =========================
    cursor.execute(
        """
        SELECT
            id,
            time_a_id,
            time_b_id,
            ranking_a,
            ranking_b
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

    # =========================
    # PROCESSAR CADA CONFRONTO
    # =========================
    for (
        confronto_id,
        time_a_id,
        time_b_id,
        ranking_a,
        ranking_b
    ) in confrontos:

        # Pontuação do time A na rodada 22
        cursor.execute(
            """
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s
              AND time_id = %s
            """,
            (rodada_id, time_a_id),
        )

        resultado_a = cursor.fetchone()

        if not resultado_a:
            raise RuntimeError(
                f"Pontuação da rodada 22 não encontrada "
                f"para o time {time_a_id}."
            )

        pontos_volta_a = resultado_a[0]

        # Pontuação do time B na rodada 22
        cursor.execute(
            """
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s
              AND time_id = %s
            """,
            (rodada_id, time_b_id),
        )

        resultado_b = cursor.fetchone()

        if not resultado_b:
            raise RuntimeError(
                f"Pontuação da rodada 22 não encontrada "
                f"para o time {time_b_id}."
            )

        pontos_volta_b = resultado_b[0]

        # =========================
        # GRAVAR JOGO DA VOLTA
        # =========================
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
            VALUES (%s, %s, 2, %s, %s, CURRENT_TIMESTAMP)
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
                pontos_volta_a,
                pontos_volta_b,
            ),
        )

        # =========================
        # BUSCAR JOGO DA IDA
        # =========================
        cursor.execute(
            """
            SELECT
                pontuacao_a,
                pontuacao_b
            FROM competicao_confronto_jogos
            WHERE confronto_id = %s
              AND ordem = 1
            """,
            (confronto_id,),
        )

        jogo_ida = cursor.fetchone()

        if not jogo_ida:
            raise RuntimeError(
                f"Jogo de ida não encontrado para o confronto "
                f"{confronto_id}."
            )

        pontos_ida_a, pontos_ida_b = jogo_ida

        # =========================
        # CALCULAR PLACAR AGREGADO
        # =========================
        total_a = pontos_ida_a + pontos_volta_a
        total_b = pontos_ida_b + pontos_volta_b

        # =========================
        # DEFINIR VENCEDOR
        # =========================
        if total_a > total_b:
            vencedor_id = time_a_id
            perdedor_id = time_b_id

        elif total_b > total_a:
            vencedor_id = time_b_id
            perdedor_id = time_a_id

        else:
            # Melhor posição na rodada 20.
            # Ranking menor significa posição melhor.
            if ranking_a < ranking_b:
                vencedor_id = time_a_id
                perdedor_id = time_b_id
            else:
                vencedor_id = time_b_id
                perdedor_id = time_a_id

        # =========================
        # FINALIZAR CONFRONTO
        # =========================
        cursor.execute(
            """
            UPDATE competicao_confrontos
            SET pontuacao_a = %s,
                pontuacao_b = %s,
                vencedor_id = %s,
                perdedor_id = %s,
                status = 'finalizado'
            WHERE id = %s
            """,
            (
                total_a,
                total_b,
                vencedor_id,
                perdedor_id,
                confronto_id,
            ),
        )

    print(
        "[Champions] 19 jogos da volta processados "
        "e classificados definidos."
    )    
    
def criar_grupos_champions(cursor, ano):
    """
    Cria os 16 grupos da Champions após o fim da repescagem.

    Regra:
    - 45 classificados diretamente pela rodada 20;
    - 19 vencedores da repescagem;
    - grupos A até P;
    - distribuição seguindo o ranking inicial da rodada 20.
    """

    print("[Champions] Criando fase de grupos...")

    # =========================
    # LOCALIZAR COMPETIÇÃO
    # =========================
    cursor.execute(
        """
        SELECT id
        FROM competicoes
        WHERE tipo = 'champions'
          AND ano = %s
        LIMIT 1
        """,
        (ano,),
    )

    competicao = cursor.fetchone()

    if not competicao:
        raise RuntimeError(
            f"Champions {ano} não encontrada."
        )

    competicao_id = competicao[0]

    # =========================
    # EVITAR DUPLICAÇÃO
    # =========================
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM champions_grupos
        WHERE competicao_id = %s
        """,
        (competicao_id,),
    )

    total_existente = cursor.fetchone()[0]

    if total_existente > 0:
        print(
            f"[Champions] Grupos já possuem "
            f"{total_existente} times cadastrados."
        )
        return

    # =========================
    # BUSCAR 45 DIRETOS
    # =========================
    cursor.execute(
        """
        SELECT
            time_id,
            ranking_inicial
        FROM competicao_times
        WHERE competicao_id = %s
          AND status = 'direto'
        ORDER BY ranking_inicial
        """,
        (competicao_id,),
    )

    diretos = cursor.fetchall()

    if len(diretos) != 45:
        raise RuntimeError(
            f"Esperados 45 classificados diretos, "
            f"encontrados {len(diretos)}."
        )

    # =========================
    # BUSCAR 19 VENCEDORES
    # =========================
    cursor.execute(
        """
        SELECT
            cc.vencedor_id,
            ct.ranking_inicial
        FROM competicao_confrontos cc
        JOIN competicao_fases cf
            ON cf.id = cc.fase_id
        JOIN competicao_times ct
            ON ct.competicao_id = cc.competicao_id
           AND ct.time_id = cc.vencedor_id
        WHERE cc.competicao_id = %s
          AND LOWER(cf.nome_fase) = 'repescagem'
          AND cc.status = 'finalizado'
          AND cc.vencedor_id IS NOT NULL
        ORDER BY cc.ordem_na_fase
        """,
        (competicao_id,),
    )

    vencedores = cursor.fetchall()

    if len(vencedores) != 19:
        raise RuntimeError(
            f"Esperados 19 vencedores da repescagem, "
            f"encontrados {len(vencedores)}."
        )

    letras = [
        chr(codigo)
        for codigo in range(ord("A"), ord("P") + 1)
    ]

    # =========================
    # DISTRIBUIR OS DIRETOS
    # =========================
    for indice, (time_id, ranking_inicial) in enumerate(diretos):

        grupo = letras[indice % 16]

        cursor.execute(
            """
            INSERT INTO champions_grupos (
                competicao_id,
                ano,
                grupo,
                time_id,
                origem,
                ranking_inicial
            )
            VALUES (%s, %s, %s, %s, 'direto', %s)
            """,
            (
                competicao_id,
                ano,
                grupo,
                time_id,
                ranking_inicial,
            ),
        )

    # =========================
    # DISTRIBUIR VENCEDORES
    # =========================
    #
    # Os 45 diretos deixam:
    #
    # A-M = 3 times
    # N-P = 2 times
    #
    # Portanto começamos a repescagem no grupo N,
    # exatamente como fizemos na Copa do Mundo.
    #
    inicio = letras.index("N")

    for indice, (time_id, ranking_inicial) in enumerate(vencedores):

        grupo = letras[(inicio + indice) % 16]

        cursor.execute(
            """
            INSERT INTO champions_grupos (
                competicao_id,
                ano,
                grupo,
                time_id,
                origem,
                ranking_inicial
            )
            VALUES (%s, %s, %s, %s, 'repescagem', %s)
            """,
            (
                competicao_id,
                ano,
                grupo,
                time_id,
                ranking_inicial,
            ),
        )

    # =========================
    # VALIDAR RESULTADO
    # =========================
    cursor.execute(
        """
        SELECT
            grupo,
            COUNT(*)
        FROM champions_grupos
        WHERE competicao_id = %s
        GROUP BY grupo
        ORDER BY grupo
        """,
        (competicao_id,),
    )

    grupos = cursor.fetchall()

    if len(grupos) != 16:
        raise RuntimeError(
            f"Esperados 16 grupos, encontrados {len(grupos)}."
        )

    for grupo, total in grupos:
        if total != 4:
            raise RuntimeError(
                f"Grupo {grupo} ficou com {total} times "
                "em vez de 4."
            )

    print(
        "[Champions] 16 grupos criados com "
        "4 times cada."
    )    

def criar_jogos_grupos_champions(cursor, ano):
    """
    Cria antecipadamente os jogos das rodadas 23 a 28.

    Cada grupo possui:
    - 4 times
    - 6 confrontos diferentes
    - ida e volta
    - 12 jogos no total
    """

    print("[Champions] Criando jogos da fase de grupos...")

    # Localizar competição
    cursor.execute("""
        SELECT id
        FROM competicoes
        WHERE tipo = 'champions'
          AND ano = %s
        LIMIT 1
    """, (ano,))

    competicao = cursor.fetchone()

    if not competicao:
        raise RuntimeError(
            f"Champions {ano} não encontrada."
        )

    competicao_id = competicao[0]

    # Evitar duplicação
    cursor.execute("""
        SELECT COUNT(*)
        FROM champions_grupo_jogos
        WHERE competicao_id = %s
    """, (competicao_id,))

    total_existente = cursor.fetchone()[0]

    if total_existente > 0:
        print(
            f"[Champions] Jogos dos grupos já existem "
            f"({total_existente} registros)."
        )
        return

    # Buscar os grupos
    cursor.execute("""
        SELECT
            grupo,
            time_id,
            ranking_inicial
        FROM champions_grupos
        WHERE competicao_id = %s
        ORDER BY grupo, ranking_inicial
    """, (competicao_id,))

    dados = cursor.fetchall()

    grupos = {}

    for grupo, time_id, ranking in dados:
        grupos.setdefault(grupo, []).append(time_id)

    if len(grupos) != 16:
        raise RuntimeError(
            f"Esperados 16 grupos, encontrados {len(grupos)}."
        )

    for grupo, times in grupos.items():

        if len(times) != 4:
            raise RuntimeError(
                f"Grupo {grupo} possui {len(times)} times."
            )

        a, b, c, d = times

        jogos = [
            # IDA
            (23, 1, a, b),
            (23, 2, c, d),

            (24, 1, a, c),
            (24, 2, b, d),

            (25, 1, a, d),
            (25, 2, b, c),

            # VOLTA
            (26, 1, b, a),
            (26, 2, d, c),

            (27, 1, c, a),
            (27, 2, d, b),

            (28, 1, d, a),
            (28, 2, c, b),
        ]

        for rodada, ordem, time_a, time_b in jogos:

            cursor.execute("""
                INSERT INTO champions_grupo_jogos (
                    competicao_id,
                    ano,
                    grupo,
                    rodada,
                    ordem_na_rodada,
                    time_a_id,
                    time_b_id,
                    pontuacao_a,
                    pontuacao_b,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    NULL, NULL,
                    'criado'
                )
            """, (
                competicao_id,
                ano,
                grupo,
                rodada,
                ordem,
                time_a,
                time_b
            ))

    print(
        "[Champions] 192 jogos da fase de grupos criados "
        "(16 grupos x 12 jogos)."
    )    
    
def processar_rodada_grupos_champions(cursor, ano, rodada):
    """
    Processa uma rodada da fase de grupos da Champions.

    Rodadas válidas:
    23, 24, 25, 26, 27 e 28.

    A função:
    - busca os jogos já criados em champions_grupo_jogos;
    - busca os pontos reais em resultado_rodada;
    - grava pontuacao_a e pontuacao_b;
    - marca o jogo como finalizado.
    """

    if rodada not in (23, 24, 25, 26, 27, 28):
        raise ValueError(
            f"Rodada {rodada} não pertence à fase de grupos."
        )

    print(
        f"[Champions] Processando fase de grupos - rodada {rodada}..."
    )

    # =========================
    # LOCALIZAR COMPETIÇÃO
    # =========================
    cursor.execute("""
        SELECT id
        FROM competicoes
        WHERE tipo = 'champions'
          AND ano = %s
        ORDER BY id
        LIMIT 1
    """, (ano,))

    competicao = cursor.fetchone()

    if not competicao:
        raise RuntimeError(
            f"Champions {ano} não encontrada."
        )

    competicao_id = competicao[0]

    # =========================
    # LOCALIZAR RODADA
    # =========================
    cursor.execute("""
        SELECT id
        FROM rodadas
        WHERE ano = %s
          AND numero = %s
    """, (ano, rodada))

    rodada_db = cursor.fetchone()

    if not rodada_db:
        raise RuntimeError(
            f"Rodada {rodada} do ano {ano} não encontrada."
        )

    rodada_id = rodada_db[0]

    # =========================
    # BUSCAR JOGOS
    # =========================
    cursor.execute("""
        SELECT
            id,
            grupo,
            ordem_na_rodada,
            time_a_id,
            time_b_id
        FROM champions_grupo_jogos
        WHERE competicao_id = %s
          AND ano = %s
          AND rodada = %s
        ORDER BY
            grupo,
            ordem_na_rodada
    """, (
        competicao_id,
        ano,
        rodada
    ))

    jogos = cursor.fetchall()

    # 16 grupos x 2 jogos = 32
    if len(jogos) != 32:
        raise RuntimeError(
            f"Esperados 32 jogos na rodada {rodada}, "
            f"mas foram encontrados {len(jogos)}."
        )

    # =========================
    # PROCESSAR JOGOS
    # =========================
    for (
        jogo_id,
        grupo,
        ordem,
        time_a_id,
        time_b_id
    ) in jogos:

        # Pontuação do time A
        cursor.execute("""
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s
              AND time_id = %s
        """, (
            rodada_id,
            time_a_id
        ))

        resultado_a = cursor.fetchone()

        if not resultado_a:
            raise RuntimeError(
                f"Pontuação não encontrada para o time "
                f"{time_a_id} na rodada {rodada}."
            )

        pontos_a = resultado_a[0]

        # Pontuação do time B
        cursor.execute("""
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s
              AND time_id = %s
        """, (
            rodada_id,
            time_b_id
        ))

        resultado_b = cursor.fetchone()

        if not resultado_b:
            raise RuntimeError(
                f"Pontuação não encontrada para o time "
                f"{time_b_id} na rodada {rodada}."
            )

        pontos_b = resultado_b[0]

        # Atualizar jogo
        cursor.execute("""
            UPDATE champions_grupo_jogos
            SET
                pontuacao_a = %s,
                pontuacao_b = %s,
                status = 'finalizado'
            WHERE id = %s
        """, (
            pontos_a,
            pontos_b,
            jogo_id
        ))

    print(
        f"[Champions] Rodada {rodada} da fase de grupos "
        f"processada: {len(jogos)} jogos atualizados."
    )    