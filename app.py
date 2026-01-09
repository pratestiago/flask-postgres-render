from flask import Flask, render_template
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
    return render_template("index.html")


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
        WHERE t.temporada = 2025
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
