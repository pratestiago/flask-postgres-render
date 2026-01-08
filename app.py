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
        GROUP BY r.mes, c.nome, t.nome_time
        ORDER BY r.mes, pontos_mes DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "resultados_mensal.html",
        resultados=resultados
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
    return render_template("em_desenvolvimento.html")


@app.route("/resultados/maior-pontuador")
def resultados_maior_pontuador():
    return render_template("em_desenvolvimento.html")


@app.route("/resultados/rodada-a-rodada")
def resultados_rodada_a_rodada():
    return render_template("em_desenvolvimento.html")

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
