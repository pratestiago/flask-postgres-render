from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

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

@app.route("/resultados/rodada")
def resultados_rodada():
    return render_template("resultados_rodada.html")


@app.route("/resultados/mensal")
def resultados_mensal():
    return render_template("resultados_mensal.html")


@app.route("/resultados/turno")
def resultados_turno():
    return render_template("resultados_turno.html")


@app.route("/resultados/cartoletas")
def resultados_cartoletas():
    return render_template("resultados_cartoletas.html")


@app.route("/resultados/maior-pontuador")
def resultados_maior_pontuador():
    return render_template("resultados_maior_pontuador.html")


@app.route("/resultados/rodada-a-rodada")
def resultados_rodada_a_rodada():
    return render_template("resultados_rodada_a_rodada.html")



if __name__ == "__main__":
    app.run(debug=True)
