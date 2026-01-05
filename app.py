from flask import Flask
import psycopg2
import os

app = Flask(__name__)

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================

# 🔹 Banco LOCAL (PostgreSQL do seu PC)
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "4705"
}

# 🔹 Banco do Render (vem automaticamente no ambiente)
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# ROTA PRINCIPAL
# =========================

@app.route("/")
def home():
    resposta = []

    # ✅ Verificação Flask
    resposta.append("Funcionou agora 😄 (Flask OK)")

    try:
        # 🔀 Decide qual banco usar
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
        else:
            conn = psycopg2.connect(**DB_CONFIG)

        cursor = conn.cursor()

        # ✅ Verificação Banco
        resposta.append("Flask conectado ao PostgreSQL 🐘 (DB OK)\n")

        # 📥 Consulta
        cursor.execute("SELECT * FROM public.placar")
        registros = cursor.fetchall()

        for r in registros:
            resposta.append(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")

        cursor.close()
        conn.close()

    except Exception as e:
        resposta.append(f"Erro no banco ❌: {e}")

    # Exibe tudo na página
    return "<br>".join(resposta)

# =========================
# START DA APLICAÇÃO
# =========================

if __name__ == "__main__":
    app.run(debug=True)
