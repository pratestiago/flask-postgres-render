import csv
import psycopg2
import os

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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "arquivos", "duplas_times_rodada.csv")


# =========================
# INPUT DO USUÁRIO
# =========================

mes_referencia = int(input("Digite o mês da rodada (1-12): "))

if mes_referencia < 1 or mes_referencia > 12:
    raise ValueError("Mês inválido. Use um valor entre 1 e 12.")

# =========================
# FUNÇÕES AUXILIARES
# =========================

def get_or_create_rodada(cursor, ano, numero, mes):
    cursor.execute("""
        SELECT id, mes
        FROM rodadas_duplas
        WHERE ano = %s AND numero = %s
    """, (ano, numero))

    row = cursor.fetchone()

    if row:
        rodada_id, mes_atual = row

        if mes_atual != mes:
            cursor.execute("""
                UPDATE rodadas_duplas
                SET mes = %s
                WHERE id = %s
            """, (mes, rodada_id))

        return rodada_id

    cursor.execute("""
        INSERT INTO rodadas_duplas (ano, numero, mes, status)
        VALUES (%s, %s, %s, 'encerrada')
        RETURNING id
    """, (ano, numero, mes))

    return cursor.fetchone()[0]


def validar_time(cursor, time_id):
    cursor.execute("""
        SELECT id
        FROM duplas_times
        WHERE id = %s
    """, (time_id,))
    if not cursor.fetchone():
        raise Exception(f"Time não encontrado: id={time_id}")


def inserir_pontuacao(cursor, time_id, rodada_id, pontos):
    cursor.execute("""
        INSERT INTO duplas_times_pontuacoes (
            time_id,
            rodada_id,
            pontos
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (time_id, rodada_id)
        DO UPDATE SET
            pontos = EXCLUDED.pontos
    """, (time_id, rodada_id, pontos))


# =========================
# SCRIPT PRINCIPAL
# =========================

def importar_csv():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)

            ano_importado = None
            rodada_importada = None

            


            for linha in leitor:
                # normaliza chaves do CSV (BOM, espaços, maiúsculas)
                linha = {
                    k.strip().lower().replace('\ufeff', ''): v
                    for k, v in linha.items()
                }

                ano = int(linha["ano"])
                rodada = int(linha["rodada"])
                time_id = int(linha["time_id"])
                pontos = float(linha["pontos"])

                ano_importado = ano
                rodada_importada = rodada

                rodada_id = get_or_create_rodada(
                    cursor,
                    ano,
                    rodada,
                    mes_referencia
                )

                validar_time(cursor, time_id)

                inserir_pontuacao(
                    cursor,
                    time_id,
                    rodada_id,
                    pontos
                )

        conn.commit()
        print("✅ CSV importado com sucesso!")
        print(f"Ano importado: {ano_importado}")
        print(f"Rodada importada: {rodada_importada}")

    except Exception as erro:
        conn.rollback()
        print("❌ Erro:", erro)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    importar_csv()
