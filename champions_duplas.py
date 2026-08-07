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

        fase_grupos = None

        if rodada_atual >= 20:
            fase_grupos = processar_fase_grupos(
                cursor,
                ano,
                grupos,
                rodada_atual
            )

        resultado = {
            "ranking": ranking,
            "grupos": grupos,
            "fase_grupos": fase_grupos,
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

# =========================
# CALENDÁRIO DA FASE DE GRUPOS
# =========================

CALENDARIO_GRUPOS = {

    # Rodada 22
    22: [
        (0, 3),
        (1, 2),
    ],

    # Rodada 23
    23: [
        (0, 2),
        (1, 3),
    ],

    # Rodada 24
    24: [
        (0, 1),
        (2, 3),
    ],

    # Rodada 25 (volta)
    25: [
        (3, 0),
        (2, 1),
    ],

    # Rodada 26 (volta)
    26: [
        (2, 0),
        (3, 1),
    ],

    # Rodada 27 (volta)
    27: [
        (1, 0),
        (3, 2),
    ],
}

# =========================
# ATUALIZAR CLASSIFICAÇÃO
# =========================

def atualizar_classificacao(
    dupla_a,
    dupla_b,
    pontos_a,
    pontos_b
):
    """
    Atualiza a classificação das duas duplas após um confronto.

    Regras:
    - vitória por diferença de 10 pontos ou mais:
      vencedor recebe 3 e perdedor recebe 0;
    - vitória por diferença menor que 10 pontos:
      vencedor recebe 2 e perdedor recebe 1;
    - empate:
      cada dupla recebe 1 ponto.
    """

    # Garante que os campos existam
    for dupla in (dupla_a, dupla_b):
        dupla.setdefault("pg", 0)
        dupla.setdefault("j", 0)
        dupla.setdefault("v", 0)
        dupla.setdefault("e", 0)
        dupla.setdefault("d", 0)
        dupla.setdefault("gp", 0.0)
        dupla.setdefault("gc", 0.0)
        dupla.setdefault("saldo", 0.0)

    pontos_a = float(pontos_a)
    pontos_b = float(pontos_b)

    # Jogos disputados
    dupla_a["j"] += 1
    dupla_b["j"] += 1

    # Pontos marcados e sofridos
    dupla_a["gp"] += pontos_a
    dupla_a["gc"] += pontos_b

    dupla_b["gp"] += pontos_b
    dupla_b["gc"] += pontos_a

    # Empate
    if pontos_a == pontos_b:
        dupla_a["e"] += 1
        dupla_b["e"] += 1

        dupla_a["pg"] += 1
        dupla_b["pg"] += 1

    else:
        diferenca = abs(pontos_a - pontos_b)

        if pontos_a > pontos_b:
            vencedora = dupla_a
            perdedora = dupla_b
        else:
            vencedora = dupla_b
            perdedora = dupla_a

        vencedora["v"] += 1
        perdedora["d"] += 1

        if diferenca >= 10:
            vencedora["pg"] += 3
        else:
            vencedora["pg"] += 2
            perdedora["pg"] += 1

    # Atualiza o saldo
    dupla_a["saldo"] = dupla_a["gp"] - dupla_a["gc"]
    dupla_b["saldo"] = dupla_b["gp"] - dupla_b["gc"]
    
    
    # =========================
# BUSCAR PONTOS DA RODADA
# =========================

def buscar_pontos_rodada_duplas(cursor, ano, rodada):
    """
    Retorna um dicionário no formato:

    {
        dupla_id: pontos_da_dupla
    }

    A pontuação da dupla é a soma dos dois integrantes.
    """

    cursor.execute(
        """
        SELECT
            d.id AS dupla_id,
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
            d.id
        """,
        (
            ano,
            rodada,
        ),
    )

    linhas = cursor.fetchall()

    return {
        dupla_id: float(pontos)
        for dupla_id, pontos in linhas
    }
    
# =========================
# PROCESSAR RODADA DE UM GRUPO
# =========================

def processar_rodada_grupo(
    grupo,
    pontos_rodada,
    rodada
):
    """
    Processa os dois confrontos de um grupo em uma rodada.

    Retorna uma lista de confrontos pronta para o front.
    """

    confrontos_calendario = CALENDARIO_GRUPOS.get(rodada)

    if confrontos_calendario is None:
        raise ValueError(
            f"A rodada {rodada} não pertence à fase de grupos."
        )

    if len(grupo) != 4:
        raise ValueError(
            f"Esperadas 4 duplas no grupo, "
            f"mas foram recebidas {len(grupo)}."
        )

    confrontos = []

    for ordem, (indice_a, indice_b) in enumerate(
        confrontos_calendario,
        start=1
    ):
        dupla_a = grupo[indice_a]
        dupla_b = grupo[indice_b]

        pontos_a = pontos_rodada.get(dupla_a["id"])
        pontos_b = pontos_rodada.get(dupla_b["id"])

        # A rodada ainda não possui resultado completo
        if pontos_a is None or pontos_b is None:
            confrontos.append({
                "ordem": ordem,
                "rodada": rodada,
                "dupla_a": dupla_a,
                "dupla_b": dupla_b,
                "pontos_a": pontos_a,
                "pontos_b": pontos_b,
                "pontos_tabela_a": None,
                "pontos_tabela_b": None,
                "resultado_tabela": None,
                "status": "aguardando",
            })

            continue

        pontos_tabela_a, pontos_tabela_b = calcular_pontos_tabela(
            pontos_a,
            pontos_b
        )

        atualizar_classificacao(
            dupla_a,
            dupla_b,
            pontos_a,
            pontos_b
        )

        confrontos.append({
            "ordem": ordem,
            "rodada": rodada,
            "dupla_a": dupla_a,
            "dupla_b": dupla_b,
            "pontos_a": pontos_a,
            "pontos_b": pontos_b,
            "pontos_tabela_a": pontos_tabela_a,
            "pontos_tabela_b": pontos_tabela_b,
            "resultado_tabela": (
                f"{pontos_tabela_a} x {pontos_tabela_b}"
            ),
            "status": "encerrado",
        })

    return confrontos    

# =========================
# CALCULAR PONTOS DA TABELA
# =========================

def calcular_pontos_tabela(pontos_a, pontos_b):
    """
    Retorna os pontos conquistados pelas duas duplas
    na classificação do grupo.
    """

    pontos_a = float(pontos_a)
    pontos_b = float(pontos_b)

    if pontos_a == pontos_b:
        return 1, 1

    diferenca = abs(pontos_a - pontos_b)

    if pontos_a > pontos_b:
        if diferenca >= 10:
            return 3, 0

        return 2, 1

    if diferenca >= 10:
        return 0, 3

    return 1, 2

# =========================
# PROCESSAR FASE DE GRUPOS
# =========================

def processar_fase_grupos(
    cursor,
    ano,
    grupos,
    rodada_atual
):
    """
    Monta toda a fase de grupos das rodadas 22 a 27.

    - Todos os confrontos aparecem no front desde o início.
    - Rodadas já disputadas recebem pontuação.
    - Rodadas futuras ficam com status "aguardando".
    - A classificação acumula somente jogos já realizados.
    """

    confrontos = {
        letra: []
        for letra in grupos
    }

    # Processa o calendário inteiro
    for rodada in range(22, 28):

        # Só busca pontos se a rodada já aconteceu
        if rodada <= rodada_atual:
            pontos_rodada = buscar_pontos_rodada_duplas(
                cursor,
                ano,
                rodada
            )
        else:
            pontos_rodada = {}

        for letra, grupo in grupos.items():

            confrontos_rodada = processar_rodada_grupo(
                grupo,
                pontos_rodada,
                rodada
            )

            confrontos[letra].extend(
                confrontos_rodada
            )

    return confrontos
    