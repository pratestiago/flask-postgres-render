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
# ROTA PRINCIPAL
# =========================

@app.route("/")
def home():
    flask_ok = True
    db_ok = False

    try:
        conn = get_connection()
        conn.close()
        db_ok = True
    except:
        db_ok = False

    return render_template(
        "index.html",
        flask_ok=flask_ok,
        db_ok=db_ok
    )


# =========================
# START DA APLICAÇÃO
# =========================

if __name__ == "__main__":
    app.run(debug=True)
