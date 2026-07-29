# champions_duplas.py


# =========================
# PROCESSAMENTO PRINCIPAL
# =========================

def processar_champions_duplas(conn, ano, rodada_atual):
    """
    Reconstrói a Champions de Duplas até a rodada informada.
    Nada é gravado no banco.
    """

    if rodada_atual < 20:
        return {
            "ranking": [],
            "grupos": {},
            "fase_grupos": None,
            "oitavas": None,
            "quartas": None,
            "semifinais": None,
            "final": None,
            "campeao": None,
        }

    cursor = conn.cursor()

    try:
        ranking = buscar_ranking_duplas(
            cursor,
            ano,
            rodada=20
        )

        if len(ranking) != 32:
            raise RuntimeError(
                f"Esperadas 32 duplas na rodada 20, "
                f"mas foram encontradas {len(ranking)}."
            )

        grupos = criar_grupos(ranking)

        resultado = {
            "ranking": ranking,
            "grupos": grupos,
            "fase_grupos": None,
            "oitavas": None,
            "quartas": None,
            "semifinais": None,
            "final": None,
            "campeao": None,
        }

        return resultado

    finally:
        cursor.close()


# =========================
# BUSCAR RANKING
# =========================

def buscar_ranking_duplas(cursor, ano, rodada):
    """
    Retorna o ranking das duplas usando a soma dos pontos
    dos dois integrantes na rodada informada.
    """

    cursor.execute(
        """
        SELECT
            d.id AS dupla_id,
            d.nome AS dupla,
            STRING_AGG(
                t.nome,
                ' + '
                ORDER BY t.id
            ) AS integrantes,
            COALESCE(SUM(tp.pontos), 0) AS pontos

        FROM duplas d

        JOIN duplas_times_ligacao l
            ON l.dupla_id = d.id

        JOIN duplas_times t
            ON t.id = l.time_id

        JOIN duplas_times_pontuacoes tp
            ON tp.time_id = t.id

        JOIN rodadas_duplas r
            ON r.id = tp.rodada_id

        WHERE r.ano = %s
          AND r.numero = %s

        GROUP BY
            d.id,
            d.nome

        ORDER BY
            pontos DESC,
            d.id ASC
        """,
        (
            ano,
            rodada,
        ),
    )

    linhas = cursor.fetchall()

    ranking = []

    for posicao, linha in enumerate(linhas, start=1):
        dupla_id, nome_dupla, integrantes, pontos = linha

        ranking.append({
            "posicao": posicao,
            "id": dupla_id,
            "nome": nome_dupla,
            "times": integrantes,
            "pontos": float(pontos),
        })

    return ranking


# =========================
# CRIAR GRUPOS
# =========================

def criar_grupos(ranking):
    """
    Distribui as 32 duplas em 8 grupos, seguindo a posição
    do ranking:

    1º ao 8º   -> grupos A ao H
    9º ao 16º  -> grupos A ao H
    17º ao 24º -> grupos A ao H
    25º ao 32º -> grupos A ao H
    """

    if len(ranking) != 32:
        raise ValueError(
            f"Para criar os grupos são necessárias 32 duplas. "
            f"Foram recebidas {len(ranking)}."
        )

    letras_grupos = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
    ]

    grupos = {
        letra: []
        for letra in letras_grupos
    }

    for indice, dupla in enumerate(ranking):
        letra_grupo = letras_grupos[indice % 8]

        dupla_grupo = dupla.copy()
        dupla_grupo["grupo"] = letra_grupo

        grupos[letra_grupo].append(dupla_grupo)

    return grupos