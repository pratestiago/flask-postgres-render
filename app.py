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
        WHERE r.ano = 2025
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2025
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
        WHERE r.ano = 2025
          AND r.mes = (
              SELECT MAX(mes)
              FROM rodadas
              WHERE ano = 2025
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
            WHERE r.ano = 2025
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
            WHERE ano = 2025
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
        WHERE r.ano = 2025
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2025
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
        WHERE r.ano = 2025
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
            t.nome_time
        FROM cartoleiros c
        JOIN times t ON t.cartoleiro_id = c.id
        WHERE t.temporada = 2026
        ORDER BY c.nome, t.nome_time
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
        WHERE r.ano = 2025
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2025
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
        WHERE r.ano = 2025
          AND r.mes = (
              SELECT MAX(mes)
              FROM rodadas
              WHERE ano = 2025
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
        WHERE r.ano = 2025
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
        WHERE r.ano = 2025
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2025
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
        WHERE r.ano = 2025
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
        WHERE r.ano = 2025
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
            SUM(rr.pontos) AS total_pontos
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2025
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
           AND td.temporada = 2025
        WHERE r.ano = 2025
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
        ta.nome_time AS time_a,
        tb.nome_time AS time_b,
        origem.ordem_na_fase AS ordem_origem,
                     tv.nome_time AS vencedor_origem,
        cc.pontuacao_a,
        cc.pontuacao_b,
        cc.vencedor_id
                 
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
    ORDER BY cc.rodada, cc.ordem_na_fase
    """, (competicao_id,))

    confrontos_db = cursor.fetchall()

        # Agrupar confrontos por fase_id
    confrontos_por_fase = {}

    for (
            fase_id,
            time_a,
            time_b,
            ordem_origem,
            vencedor_origem,
            pontos_a,
            pontos_b,
    vencedor_id
    ) in confrontos_db:

        confrontos_por_fase.setdefault(fase_id, []).append({
            "time_a": time_a,
            "time_b": time_b,
            "ordem_origem": ordem_origem,
            "vencedor_origem": vencedor_origem,
            "pontos_a": pontos_a,
            "pontos_b": pontos_b,
            "vencedor_id": vencedor_id
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
