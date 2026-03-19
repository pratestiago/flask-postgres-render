# copabrasil_v2.py

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
# PROCESSADOR PRINCIPAL
# =========================

def processar_copa_brasil(conn, ano, rodada):

    cursor = conn.cursor()

    print(f"[Copa Brasil V2] Ano {ano} - Rodada {rodada}")

    # Copa Brasil começa na rodada 2
    if rodada < 2 or rodada > 9:
        print("[Copa Brasil V2] Rodada ignorada")
        return

    if rodada == 2:
        rodada_2_ranking(cursor, ano)

    elif rodada == 3:
        rodada_3_repescagem(cursor, ano)
        rodada_4_chaveamento(cursor, ano)

    elif rodada >= 4 and rodada <= 8:
        resolver_fase(cursor, ano)
        criar_proxima_fase(cursor, ano)

    elif rodada >= 5 and rodada <= 8:
        resolver_fase(cursor, ano)
        criar_proxima_fase(cursor, ano)

    elif rodada == 9:
        resolver_final(cursor, ano)

    conn.commit()


# =========================
# RODADA 2 - RANKING
# =========================

def rodada_2_ranking(cursor, ano):

    print("[Copa Brasil V2] Rodada 2 - Gerando ranking")

    ranking = buscar_ranking(cursor, ano)

    total_times = len(ranking)

    print(f"[Copa Brasil V2] Total de times: {total_times}")

    if eh_potencia_de_2(total_times):

        print("[Copa Brasil V2] Sem repescagem")

        criar_chaveamento_direto(cursor, ranking)

    else:

        print("[Copa Brasil V2] Com repescagem")

        criar_repescagem(cursor, ranking)


# =========================
# RODADA 3 - REPESCAGEM
# =========================

def rodada_3_repescagem(cursor, ano):

    print("[Copa Brasil V2] Rodada 3 - Resolvendo repescagem")

    cursor.execute("""
    SELECT
        id,
        time_a_id,
        time_b_id,
        ranking_a,
        ranking_b
    FROM competicao_confrontos
    WHERE rodada = 3
    AND vencedor_id IS NULL
    ORDER BY ordem_na_fase
    """)

    confrontos = cursor.fetchall()

    print(f"[Copa Brasil V2] Confrontos encontrados: {len(confrontos)}")

    for confronto in confrontos:

        confronto_id, time_a, time_b, rank_a, rank_b = confronto

        cursor.execute("""
        SELECT rr.time_id, rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE r.ano = %s
        AND r.numero = 3
        AND rr.time_id IN (%s, %s)
        """, (ano, time_a, time_b))

        resultados = cursor.fetchall()

        pontos = {t: p for t, p in resultados}

        pa = pontos.get(time_a, 0)
        pb = pontos.get(time_b, 0)

        if pa > pb:
            vencedor = time_a
        elif pb > pa:
            vencedor = time_b
        else:
            vencedor = time_a if rank_a < rank_b else time_b

        cursor.execute("""
        UPDATE competicao_confrontos
        SET pontuacao_a = %s,
            pontuacao_b = %s,
            vencedor_id = %s,
            status = 'finalizado'
        WHERE id = %s
        """, (pa, pb, vencedor, confronto_id))

    print("[Copa Brasil V2] Repescagem resolvida")
    print("[Copa Brasil V2] Criando chaveamento da rodada 4")


# =========================
# RODADA 4 - CHAVEAMENTO 64
# =========================

def rodada_4_chaveamento(cursor, ano):

    print("[Copa Brasil V2] Rodada 4 - Criando chaveamento principal")

    # ---------------------------------
    # BUSCAR RANKING DA RODADA 2
    # ---------------------------------

    cursor.execute("""
    SELECT
        t.id,
        rr.pontos
    FROM resultado_rodada rr
    JOIN rodadas r ON r.id = rr.rodada_id
    JOIN times t ON t.id = rr.time_id
    WHERE r.ano = %s
    AND r.numero = 2
    ORDER BY rr.pontos DESC
    """, (ano,))

    ranking = cursor.fetchall()

    total = len(ranking)

    alvo = maior_potencia_de_2(total)

    excedente = total - alvo

    repescagem_times = excedente * 2
    diretos = total - repescagem_times

    diretos_lista = ranking[:diretos]

    # ---------------------------------
    # BUSCAR VENCEDORES DA REPESCAGEM
    # ---------------------------------

    cursor.execute("""
    SELECT vencedor_id
    FROM competicao_confrontos
    WHERE rodada = 3
    ORDER BY ordem_na_fase
    """)

    vencedores_rep = [r[0] for r in cursor.fetchall()]

    vencedores_rep.reverse()

    classificados = [t[0] for t in diretos_lista] + vencedores_rep

    print(f"[Copa Brasil V2] Times classificados: {len(classificados)}")

    # ---------------------------------
    # CRIAR OU BUSCAR FASE DA RODADA 4
    # ---------------------------------

    cursor.execute("""
    SELECT id
    FROM competicao_fases
    WHERE competicao_id = 1
    AND rodada = 4
    """)

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
        VALUES (1, '16-avos', 2, 64, 32, 4, 'em_andamento')
        RETURNING id
        """)

        fase_id = cursor.fetchone()[0]

    # ---------------------------------
    # CRIAR CONFRONTOS
    # ---------------------------------

    ordem = 1
    total_class = len(classificados)

    for i in range(total_class // 2):

        time_a = classificados[i]
        time_b = classificados[total_class - 1 - i]

        print(f"Jogo {ordem}: {time_a} x {time_b}")

        cursor.execute("""
        INSERT INTO competicao_confrontos (
            competicao_id,
            fase_id,
            rodada,
            ordem_na_fase,
            time_a_id,
            time_b_id,
            status
        )
        VALUES (1, %s, 4, %s, %s, %s, 'criado')
        """, (
            fase_id,
            ordem,
            time_a,
            time_b
        ))

        ordem += 1

    # aqui vamos criar os 32 confrontos iniciais


# =========================
# FASES INTERMEDIÁRIAS
# =========================

def resolver_fase(cursor, ano):

    print("[Copa Brasil V2] Resolvendo confrontos da fase")

    cursor.execute("""
    SELECT MAX(rodada)
    FROM competicao_confrontos
    """)
    rodada_atual = cursor.fetchone()[0]

    cursor.execute("""
    SELECT id, time_a_id, time_b_id
    FROM competicao_confrontos
    WHERE rodada = %s
    AND status = 'criado'
    ORDER BY ordem_na_fase
    """, (rodada_atual,))

    confrontos = cursor.fetchall()

    print(f"[Copa Brasil V2] Confrontos encontrados: {len(confrontos)}")

    for confronto_id, time_a, time_b in confrontos:

        cursor.execute("""
        SELECT rr.time_id, rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE r.ano = %s
        AND rr.time_id IN (%s, %s)
        ORDER BY r.numero DESC
        LIMIT 2
        """, (ano, time_a, time_b))

        resultados = cursor.fetchall()

        pontos = {t: p for t, p in resultados}

        pa = pontos.get(time_a, 0)
        pb = pontos.get(time_b, 0)

        if pa >= pb:
            vencedor = time_a
        else:
            vencedor = time_b

        cursor.execute("""
        UPDATE competicao_confrontos
        SET pontuacao_a = %s,
            pontuacao_b = %s,
            vencedor_id = %s,
            status = 'finalizado'
        WHERE id = %s
        """, (pa, pb, vencedor, confronto_id))

    print("[Copa Brasil V2] Fase resolvida")

    # resolver confrontos da rodada atual


def criar_proxima_fase(cursor, ano):

    print("[Copa Brasil V2] Criando próxima fase")

    # descobrir qual foi a última rodada da copa
    cursor.execute("""
    SELECT MAX(rodada)
    FROM competicao_confrontos
    """)
    rodada_atual = cursor.fetchone()[0]

    # pegar apenas confrontos dessa rodada
    cursor.execute("""
    SELECT id, vencedor_id
    FROM competicao_confrontos
    WHERE rodada = %s
    AND status = 'finalizado'
    ORDER BY ordem_na_fase
    """, (rodada_atual,))

    confrontos = cursor.fetchall()

    vencedores = [c[1] for c in confrontos]

    total = len(vencedores)

    print(f"[Copa Brasil V2] Vencedores encontrados: {total}")

    if total <= 1:
        print("[Copa Brasil V2] Campeonato finalizado")
        return

    nova_rodada = rodada_atual + 1

    # ---------------------------------
    # CRIAR OU BUSCAR FASE
    # ---------------------------------

    cursor.execute("""
    SELECT id
    FROM competicao_fases
    WHERE competicao_id = 1
    AND rodada = %s
    """, (nova_rodada,))

    fase = cursor.fetchone()

    if fase:
        fase_id = fase[0]
    else:

        qtd_inicio = total
        qtd_fim = total // 2

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
        VALUES (1, 'mata-mata', %s, %s, %s, %s, 'em_andamento')
        RETURNING id
        """, (
            nova_rodada,
            qtd_inicio,
            qtd_fim,
            nova_rodada
        ))

        fase_id = cursor.fetchone()[0]

    # ---------------------------------
    # GERAR NOVOS CONFRONTOS
    # ---------------------------------

    ordem = 1

    for i in range(total // 2):

        time_a = vencedores[i]
        time_b = vencedores[total - 1 - i]

        print(f"Novo confronto {ordem}: {time_a} x {time_b}")

        cursor.execute("""
        INSERT INTO competicao_confrontos (
            competicao_id,
            fase_id,
            rodada,
            ordem_na_fase,
            time_a_id,
            time_b_id,
            status
        )
        VALUES (1, %s, %s, %s, %s, %s, 'criado')
        """, (
            fase_id,
            nova_rodada,
            ordem,
            time_a,
            time_b
        ))

        ordem += 1
    # gerar novo bracket


# =========================
# FINAL
# =========================

def resolver_final(cursor, ano):

    print("[Copa Brasil V2] Resolvendo finalíssima")

    cursor.execute("""
        SELECT id, time_a_id, time_b_id
        FROM competicao_confrontos
        WHERE rodada = 9
        AND status = 'criado'
    """)

    confronto = cursor.fetchone()

    if not confronto:
        print("[Copa Brasil V2] Final já resolvida ou não encontrada")
        return

    confronto_id, time_a, time_b = confronto

    cursor.execute("""
        SELECT rr.time_id, rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE r.ano = %s
        AND r.numero = 9
        AND rr.time_id IN (%s, %s)
    """, (ano, time_a, time_b))

    resultados = cursor.fetchall()

    pontos = {t: p for t, p in resultados}

    pa = pontos.get(time_a, 0)
    pb = pontos.get(time_b, 0)

    if pa >= pb:
        vencedor = time_a
    else:
        vencedor = time_b

    cursor.execute("""
        UPDATE competicao_confrontos
        SET pontuacao_a = %s,
            pontuacao_b = %s,
            vencedor_id = %s,
            status = 'finalizado'
        WHERE id = %s
    """, (pa, pb, vencedor, confronto_id))

    print("[Copa Brasil V2] Final resolvida com sucesso")


# =========================
# FUNÇÕES DE SUPORTE
# =========================

def buscar_ranking(cursor, ano):

    cursor.execute("""
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
        AND r.numero = 2
        ORDER BY rr.pontos DESC
    """, (ano,))

    ranking = cursor.fetchall()

    print("[Copa Brasil V2] Ranking da rodada 2:")

    pos = 1
    for _, nome, pontos in ranking:
        print(f"{pos:>3}º - {nome} ({pontos} pts)")
        pos += 1

    return ranking


def criar_repescagem(cursor, ranking):

    total = len(ranking)

    alvo = maior_potencia_de_2(total)

    excedente = total - alvo

    repescagem_times = excedente * 2
    diretos = total - repescagem_times

    print(f"[Copa Brasil V2] Alvo pós-repescagem: {alvo}")
    print(f"[Copa Brasil V2] Times na repescagem: {repescagem_times}")
    print(f"[Copa Brasil V2] Times que passam direto: {diretos}")

    # ---------------------------------
    # CRIAR OU BUSCAR A FASE REPESCAGEM
    # ---------------------------------

    cursor.execute("""
    SELECT id
    FROM competicao_fases
    WHERE competicao_id = 1
    AND rodada = 3
    """)

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
        VALUES (1, 'repescagem', 1, %s, %s, 3, 'em_andamento')
        RETURNING id
        """, (repescagem_times, excedente))

        fase_id = cursor.fetchone()[0]

    # ---------------------------------
    # DEFINIR TIMES DA REPESCAGEM
    # ---------------------------------

    repescagem = ranking[diretos:]

    total_rep = len(repescagem)

    ordem = 1

    for i in range(total_rep // 2):

        time_a = repescagem[i]
        time_b = repescagem[total_rep - 1 - i]

        time_a_id = time_a[0]
        time_b_id = time_b[0]

        ranking_a = diretos + i + 1
        ranking_b = total - i

        print(f"Repescagem {ordem}: {ranking_a} x {ranking_b}")

        cursor.execute("""
        INSERT INTO competicao_confrontos (
            competicao_id,
            fase_id,
            rodada,
            ordem_na_fase,
            time_a_id,
            time_b_id,
            ranking_a,
            ranking_b,
            status
        )
        VALUES (1, %s, 3, %s, %s, %s, %s, %s, 'criado')
        """, (
            fase_id,
            ordem,
            time_a_id,
            time_b_id,
            ranking_a,
            ranking_b
        ))

        ordem += 1
    


def criar_chaveamento_direto(cursor, ranking):

    # caso já seja potência de 2
    pass