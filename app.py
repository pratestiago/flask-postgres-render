from flask import Flask
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "4705"
}

@app.route("/")
def home():
    resposta = []

    # ✅ Verificação Flask
    resposta.append("Funcionou agora 😄 (Flask OK)")

    try:
        # 🔌 Conexão com PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        resposta.append("Flask conectado ao PostgreSQL 🐘 (DB OK)\n")

        # 📥 SELECT na tabela
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

if __name__ == "__main__":
    app.run(debug=True)
