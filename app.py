from flask import Flask, render_template, abort
import psycopg2
import os

app = Flask(__name__)

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
# ROTAS BÁSICAS
# =========================
@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()

    # Vencedor da rodada
    cursor.execute("""
        SELECT
            r.numero,
            c.nome,
            t.nome_time,
            rr.pontos
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2026
          )
        ORDER BY rr.pontos DESC
        LIMIT 1
    """)
    vencedor_rodada = cursor.fetchone()

    # Líder do mês
    cursor.execute("""
        SELECT
            r.mes,
            c.nome,
            t.nome_time,
            SUM(rr.pontos)
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
          AND r.mes = (
              SELECT MAX(mes)
              FROM rodadas
              WHERE ano = 2026
          )
        GROUP BY r.mes, c.nome, t.nome_time
        ORDER BY SUM(rr.pontos) DESC
        LIMIT 1
    """)
    lider_mes = cursor.fetchone()

    # Líder do turno
    cursor.execute("""
        SELECT
            turno,
            c.nome,
            t.nome_time,
            SUM(rr.pontos)
        FROM (
            SELECT
                rr.*,
                CASE
                    WHEN r.numero BETWEEN 1 AND 19 THEN 1
                    ELSE 2
                END AS turno
            FROM resultado_rodada rr
            JOIN rodadas r ON r.id = rr.rodada_id
            WHERE r.ano = 2026
        ) rr
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE turno = (
            SELECT
                CASE
                    WHEN MAX(numero) <= 19 THEN 1
                    ELSE 2
                END
            FROM rodadas
            WHERE ano = 2026
        )
        GROUP BY turno, c.nome, t.nome_time
        ORDER BY SUM(rr.pontos) DESC
        LIMIT 1
    """)
    lider_turno = cursor.fetchone()

        # Líder de cartoletas (rodada atual)
    cursor.execute("""
        SELECT
            r.numero,
            c.nome,
            t.nome_time,
            rr.patrimonio
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2026
          )
        ORDER BY rr.patrimonio DESC
        LIMIT 1
    """)
    lider_cartoletas = cursor.fetchone()


    # Líder do campeonato
    cursor.execute("""
        SELECT
            c.nome,
            t.nome_time,
            SUM(rr.pontos)
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
        GROUP BY c.nome, t.nome_time
        ORDER BY SUM(rr.pontos) DESC
        LIMIT 1
    """)
    lider_campeonato = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        vencedor_rodada=vencedor_rodada,
        lider_mes=lider_mes,
        lider_turno=lider_turno,
        lider_cartoletas=lider_cartoletas,
        lider_campeonato=lider_campeonato
    )

@app.route("/participantes")
def participantes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.nome AS cartoleiro,
            t.nome_time,
            COALESCE(d.nome, '—') AS divisao
        FROM cartoleiros c
        JOIN times t ON t.cartoleiro_id = c.id
        LEFT JOIN times_divisoes td ON td.time_id = t.id
        LEFT JOIN divisoes d ON d.id = td.divisao_id
        WHERE t.temporada = 2026
        ORDER BY d.id NULLS LAST, t.nome_time
    """)

    participantes = cursor.fetchall()

    cursor.close()
    conn.close()

    

    return render_template(
        "participantes.html",
        participantes=participantes
    )



# =========================
# RESULTADOS - RODADA ATUAL
# =========================

@app.route("/resultados/rodada")
def resultados_rodada():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.numero AS rodada,
            c.nome AS cartoleiro,
            t.nome_time,
            rr.pontos,
            rr.patrimonio,
            rr.posicao
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2026
          )
        ORDER BY rr.pontos DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    rodada_atual = resultados[0][0] if resultados else None

    return render_template(
    "resultados_rodada.html",
    rodada=rodada_atual,
    resultados=resultados
)


# =========================
# RESULTADOS - OUTROS (PLACEHOLDER)
# =========================

@app.route("/resultados/mensal")
def resultados_mensal():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.mes,
            c.nome AS cartoleiro,
            t.nome_time,
            SUM(rr.pontos) AS pontos_mes
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
          AND r.mes = (
              SELECT MAX(mes)
              FROM rodadas
              WHERE ano = 2026
          )
        GROUP BY r.mes, c.nome, t.nome_time
        ORDER BY pontos_mes DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    mes_atual = resultados[0][0] if resultados else None

    return render_template(
        "resultados_mensal.html",
        resultados=resultados,
        mes=mes_atual
    )




@app.route("/resultados/turno")
def resultados_turno():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            CASE
                WHEN r.numero BETWEEN 1 AND 19 THEN 1
                ELSE 2
            END AS turno,
            c.nome AS cartoleiro,
            t.nome_time,
            SUM(rr.pontos) AS pontos_turno
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
        GROUP BY turno, c.nome, t.nome_time
        ORDER BY turno, pontos_turno DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "resultados_turno.html",
        resultados=resultados
    )



@app.route("/resultados/cartoletas")
def resultados_cartoletas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.numero AS rodada,
            c.nome AS cartoleiro,
            t.nome_time,
            rr.patrimonio,
            rr.variacao_patrimonio
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2026
          )
        ORDER BY rr.patrimonio DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    rodada_atual = resultados[0][0] if resultados else None

    return render_template(
        "resultados_cartoletas.html",
        rodada=rodada_atual,
        resultados=resultados
    )



@app.route("/resultados/maior-pontuador")
def resultados_maior_pontuador():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.numero AS rodada,
            c.nome AS cartoleiro,
            t.nome_time,
            rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
        ORDER BY rr.pontos DESC
        LIMIT 10
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "resultados_maior_pontuador.html",
        resultados=resultados
    )



@app.route("/resultados/rodada-a-rodada")
def resultados_rodada_a_rodada():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.numero AS rodada,
            c.nome AS cartoleiro,
            t.nome_time,
            rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
        ORDER BY c.nome, r.numero
    """)

    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    # -------------------------
    # PROCESSAMENTO EM PYTHON
    # -------------------------

    rodadas_existentes = sorted({d[0] for d in dados})

    tabela = {}

    for rodada, cartoleiro, time, pontos in dados:
        chave = (cartoleiro, time)

        if chave not in tabela:
            tabela[chave] = {
                "cartoleiro": cartoleiro,
                "time": time,
                "rodadas": {},
                "total": 0
            }

        tabela[chave]["rodadas"][rodada] = pontos
        tabela[chave]["total"] += pontos

    # Converter para lista e ordenar por total
    ranking = list(tabela.values())
    ranking.sort(key=lambda x: x["total"], reverse=True)

    return render_template(
        "resultados_rodada_a_rodada.html",
        rodadas=rodadas_existentes,
        ranking=ranking
    )

@app.route("/classificacao")
def classificacao_geral():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.nome AS cartoleiro,
            t.nome_time,
            SUM(rr.pontos) AS total_pontos,

            -- diferença para o da frente
            SUM(rr.pontos)
              - LAG(SUM(rr.pontos)) OVER (ORDER BY SUM(rr.pontos) DESC)
              AS diff_frente,

            -- diferença para o líder
            SUM(rr.pontos)
              - MAX(SUM(rr.pontos)) OVER ()
              AS diff_lider

        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2026
        GROUP BY c.nome, t.nome_time
        ORDER BY total_pontos DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "classificacao.html",
        resultados=resultados
    )



@app.route("/series")
def series_home():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM divisoes
        ORDER BY nivel
    """)
    divisoes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "series_home.html",
        divisoes=divisoes
    )


@app.route("/series/<int:divisao_id>")
def series(divisao_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar nome da divisão
    cursor.execute("""
    SELECT nome
    FROM divisoes
    WHERE id = %s
    """, (divisao_id,))
    divisao = cursor.fetchone()


    if not divisao:
        cursor.close()
        conn.close()
        abort(404)

    # Classificação da série
    cursor.execute("""
        SELECT
            c.nome AS cartoleiro,
            t.nome_time,
            SUM(rr.pontos) AS total_pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        JOIN times_divisoes td 
            ON td.time_id = t.id
           AND td.temporada = 2026
        WHERE r.ano = 2026
          AND td.divisao_id = %s
        GROUP BY c.nome, t.nome_time
        ORDER BY total_pontos DESC
    """, (divisao_id,))

    classificacao = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "series.html",
        divisao_nome=divisao[0],
        classificacao=classificacao
    )


@app.route("/mata-matas")
def mata_matas_home():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM competicoes
        ORDER BY nome
    """)

    competicoes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "mata_matas_home.html",
        competicoes=competicoes
    )


@app.route("/mata-matas/<int:competicao_id>")
def mata_matas_competicao(competicao_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar competição
    cursor.execute("""
        SELECT id, nome
        FROM competicoes
        WHERE id = %s
    """, (competicao_id,))
    competicao = cursor.fetchone()

    if not competicao:
        cursor.close()
        conn.close()
        abort(404)

    # 🔹 MAPA FIXO DE FASES (visual)
    mapa_fases = [
        {"key": "repescagem", "nome": "Repescagem", "rodada": 3, "ordem": 1},
        {"key": "16-avos", "nome": "2ª Fase", "rodada": 4, "ordem": 2},
        {"key": "oitavas", "nome": "3ª Fase", "rodada": 5, "ordem": 3},
        {"key": "quartas", "nome": "Oitavas de Final", "rodada": 6, "ordem": 4},
        {"key": "semifinal", "nome": "Quartas de Final", "rodada": 7, "ordem": 5},
        {"key": "final", "nome": "Semifinal", "rodada": 8, "ordem": 6},
        {"key": "finalissima", "nome": "Final", "rodada": 9, "ordem": 7},
    ]



    # 🔹 Buscar fases que JÁ EXISTEM no banco
    cursor.execute("""
        SELECT id, nome_fase, rodada
        FROM competicao_fases
        WHERE competicao_id = %s
    """, (competicao_id,))

    fases_db = cursor.fetchall()

        # 🔹 Buscar confrontos da competição
    cursor.execute("""
SELECT
    cc.fase_id,
    cc.ordem_na_fase,
    ta.nome_time AS time_a,
    tb.nome_time AS time_b,
    origem.ordem_na_fase AS ordem_origem,
    tv.nome_time AS vencedor_origem,
    cc.pontuacao_a,
    cc.pontuacao_b,
    cc.vencedor_id,
    cc.ranking_a,
    cc.ranking_b

                 
    FROM competicao_confrontos cc

    JOIN times ta
      ON ta.id = cc.time_a_id

    LEFT JOIN times tb
      ON tb.id = cc.time_b_id

    LEFT JOIN competicao_confrontos origem
      ON origem.id = cc.origem_time_b_confronto_id
                   
                   LEFT JOIN times tv
  ON tv.id = origem.vencedor_id

    WHERE cc.competicao_id = %s
    ORDER BY cc.rodada, cc.ranking_a

    """, (competicao_id,))

    confrontos_db = cursor.fetchall()

        # Agrupar confrontos por fase_id
    confrontos_por_fase = {}

    for (
            fase_id,
            ordem_na_fase,
            time_a,
            time_b,
            ordem_origem,
            vencedor_origem,
            pontos_a,
            pontos_b,
            vencedor_id,
            ranking_a,
            ranking_b
    ) in confrontos_db:




        confrontos_por_fase.setdefault(fase_id, []).append({
            "time_a": time_a,
            "time_b": time_b,
            "ordem_origem": ordem_origem,
            "vencedor_origem": vencedor_origem,
            "pontos_a": pontos_a,
            "pontos_b": pontos_b,
            "vencedor_id": vencedor_id,
            "ranking_a": ranking_a,
            "ranking_b": ranking_b,
            "ordem_na_fase": ordem_na_fase,

        })




    # Transformar em dicionário por nome
    fases_existentes = {
        nome_fase.lower(): {
            "id": fase_id,
            "rodada": rodada
        }
        for fase_id, nome_fase, rodada in fases_db
    }

    # 🔹 Unir mapa fixo + banco


    fases = []

    for fase in mapa_fases:
        chave = fase["key"]
        existe = chave in fases_existentes

        fase_id = fases_existentes[chave]["id"] if existe else None

        fases.append({
            "nome": fase["nome"],
            "rodada": fase["rodada"],
            "existe": existe,
            "confrontos": confrontos_por_fase.get(fase_id, [])
        })




    cursor.close()
    conn.close()

    return render_template(
        "mata_matas_competicao.html",
        competicao=competicao,
        fases=fases
    )

@app.route("/resultados/duplas")
def duplas():
    return render_template("duplas.html")

@app.route("/resultados/duplas/rodada")
def duplas_rodada():
    ano = 2026

    conn = get_connection()
    cur = conn.cursor()

    # 🔹 pega a última rodada disponível do ano
    cur.execute("""
        SELECT MAX(numero)
        FROM rodadas_duplas
        WHERE ano = %s
    """, (ano,))

    rodada = cur.fetchone()[0]

    # se ainda não existir rodada (primeiro acesso)
    if rodada is None:
        cur.close()
        conn.close()
        return render_template(
            "duplas_rodada.html",
            rodada=0,
            resultados=[]
        )

    # 🔹 busca os resultados da última rodada
    cur.execute("""
        SELECT
            d.nome AS dupla,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times,
            SUM(tp.pontos) AS pontos
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
        GROUP BY d.id, d.nome
        ORDER BY pontos DESC
    """, (ano, rodada))

    resultados = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "duplas_rodada.html",
        rodada=rodada,
        resultados=resultados
    )

@app.route("/resultados/duplas/classificacao-geral")
def duplas_classificacao_geral():
    ano = 2026  # depois pode virar dinâmico

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.nome AS dupla,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times,
            SUM(tp.pontos) AS pontos
        FROM duplas d
        JOIN duplas_times_ligacao l ON l.dupla_id = d.id
        JOIN duplas_times t ON t.id = l.time_id
        JOIN duplas_times_pontuacoes tp ON tp.time_id = t.id
        JOIN rodadas_duplas r ON r.id = tp.rodada_id
        WHERE r.ano = %s
        GROUP BY d.id, d.nome
        ORDER BY pontos DESC
    """, (ano,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    resultados = []

    lider_pontos = rows[0][2] if rows else 0
    pontos_anterior = None

    for dupla, times, pontos in rows:
        diff_frente = None if pontos_anterior is None else pontos_anterior - pontos
        diff_lider = lider_pontos - pontos

        resultados.append((
            dupla,
            times,
            pontos,
            diff_frente,
            diff_lider
        ))

        pontos_anterior = pontos

    return render_template(
        "duplas_classificacao_geral.html",
        resultados=resultados
    )

@app.route("/resultados/duplas/mensal")
def duplas_mensal():
    ano = 2026

    conn = get_connection()
    cur = conn.cursor()

    # 🔹 pega o último mês com rodadas do ano
    cur.execute("""
        SELECT MAX(mes)
        FROM rodadas_duplas
        WHERE ano = %s
          AND mes IS NOT NULL
    """, (ano,))

    mes = cur.fetchone()[0]

    # se ainda não existir mês
    if mes is None:
        cur.close()
        conn.close()
        return render_template(
            "duplas_mensal.html",
            ano=ano,
            mes=0,
            resultados=[]
        )

    # 🔹 busca os resultados do mês
    cur.execute("""
        SELECT
            d.nome AS dupla,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times,
            SUM(tp.pontos) AS pontos
        FROM duplas d
        JOIN duplas_times_ligacao l ON l.dupla_id = d.id
        JOIN duplas_times t ON t.id = l.time_id
        JOIN duplas_times_pontuacoes tp ON tp.time_id = t.id
        JOIN rodadas_duplas r ON r.id = tp.rodada_id
        WHERE r.ano = %s
          AND r.mes = %s
        GROUP BY d.id, d.nome
        ORDER BY pontos DESC
    """, (ano, mes))

    resultados = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "duplas_mensal.html",
        ano=ano,
        mes=mes,
        resultados=resultados
    )


@app.route("/resultados/duplas/turno")
def duplas_turno():
    ano = 2026  # depois pode virar dinâmico

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            CASE
                WHEN r.numero BETWEEN 1 AND 19 THEN 1
                ELSE 2
            END AS turno,
            d.nome AS dupla,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times,
            SUM(tp.pontos) AS pontos
        FROM rodadas_duplas r
        JOIN duplas_times_pontuacoes tp ON tp.rodada_id = r.id
        JOIN duplas_times t ON t.id = tp.time_id
        JOIN duplas_times_ligacao l ON l.time_id = t.id
        JOIN duplas d ON d.id = l.dupla_id
        WHERE r.ano = %s
        GROUP BY turno, d.id, d.nome
        ORDER BY turno, pontos DESC
    """, (ano,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # separa por turno
    turno_1 = []
    turno_2 = []

    for turno, dupla, times, pontos in rows:
        if turno == 1:
            turno_1.append((dupla, times, pontos))
        else:
            turno_2.append((dupla, times, pontos))

    return render_template(
        "duplas_turno.html",
        ano=ano,
        turno_1=turno_1,
        turno_2=turno_2
    )

@app.route("/resultados/duplas/maior-pontuador")
def duplas_maior_pontuador():
    ano = 2026  # depois pode virar dinâmico

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.numero AS rodada,
            d.nome AS dupla,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times,
            SUM(tp.pontos) AS pontos
        FROM rodadas_duplas r
        JOIN duplas_times_pontuacoes tp ON tp.rodada_id = r.id
        JOIN duplas_times t ON t.id = tp.time_id
        JOIN duplas_times_ligacao l ON l.time_id = t.id
        JOIN duplas d ON d.id = l.dupla_id
        WHERE r.ano = %s
        GROUP BY r.numero, d.id, d.nome
        ORDER BY pontos DESC
        LIMIT 10
    """, (ano,))

    resultados = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "duplas_maior_pontuador.html",
        ano=ano,
        resultados=resultados
    )
@app.route("/resultados/duplas/rodada-a-rodada")
def duplas_rodada_a_rodada():
    ano = 2026  # depois pode dinamizar

    conn = get_connection()
    cur = conn.cursor()

    # 1) pontos da dupla por rodada
    cur.execute("""
        SELECT
            d.id AS dupla_id,
            d.nome AS dupla,
            r.numero AS rodada,
            SUM(tp.pontos) AS pontos
        FROM duplas d
        JOIN duplas_times_ligacao l ON l.dupla_id = d.id
        JOIN duplas_times_pontuacoes tp ON tp.time_id = l.time_id
        JOIN rodadas_duplas r ON r.id = tp.rodada_id
        WHERE r.ano = %s
        GROUP BY d.id, d.nome, r.numero
        ORDER BY d.nome, r.numero
    """, (ano,))

    dados = cur.fetchall()

    # 2) nomes dos times por dupla
    cur.execute("""
        SELECT
            d.id AS dupla_id,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times
        FROM duplas d
        JOIN duplas_times_ligacao l ON l.dupla_id = d.id
        JOIN duplas_times t ON t.id = l.time_id
        GROUP BY d.id
    """)

    times_duplas = {
        dupla_id: times
        for dupla_id, times in cur.fetchall()
    }

    cur.close()
    conn.close()

    # rodadas existentes
    rodadas = sorted({linha[2] for linha in dados})

    ranking = {}
    for dupla_id, dupla, rodada, pontos in dados:
        if dupla_id not in ranking:
            ranking[dupla_id] = {
                "dupla": dupla,
                "times": times_duplas.get(dupla_id, ""),
                "rodadas": {},
                "total": 0
            }

        ranking[dupla_id]["rodadas"][rodada] = pontos
        ranking[dupla_id]["total"] += pontos

    ranking_final = list(ranking.values())
    ranking_final.sort(key=lambda x: x["total"], reverse=True)

    return render_template(
        "duplas_rodada_a_rodada.html",
        rodadas=rodadas,
        ranking=ranking_final
    )

@app.route("/calendario")
def calendario():
    return render_template("calendario.html")

@app.route("/resultados/duplas/calendario_duplas")
def calendario_duplas():
    return render_template("calendario_duplas.html")
@app.route("/resultados/duplas/mata-mata")
def resultados_duplas_mata_mata():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            d.nome AS dupla,
            STRING_AGG(t.nome, ' + ' ORDER BY t.id) AS times,
            SUM(tp.pontos) AS pontos
        FROM duplas d
        JOIN duplas_times_ligacao l ON l.dupla_id = d.id
        JOIN duplas_times t ON t.id = l.time_id
        JOIN duplas_times_pontuacoes tp ON tp.time_id = t.id
        JOIN rodadas_duplas r ON r.id = tp.rodada_id
        WHERE r.ano = 2026
          AND r.numero = 2
        GROUP BY d.id, d.nome
        ORDER BY pontos DESC
    """)

    ranking = cursor.fetchall()
    cursor.close()
    conn.close()

    total = len(ranking)
    confrontos = []

    for i in range(total // 2):
        confrontos.append({
            "ordem": i + 1,
            "a": ranking[i],
            "b": ranking[total - 1 - i]
        })

    return render_template(
        "matamatadupla.html",
        confrontos=confrontos
    )

@app.route("/premiacao")
def premiacao():
    return render_template("premiacao.html")







# =========================
# PÁGINA GENÉRICA
# =========================

@app.route("/em-desenvolvimento")
def em_desenvolvimento():
    return render_template("em_desenvolvimento.html")

# =========================
# START
# =========================

if __name__ == "__main__":
    app.run(debug=True)
