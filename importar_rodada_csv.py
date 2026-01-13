import csv
import psycopg2
import os
from copa_brasil import processar_copa_brasil

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


CSV_PATH = "resuldado_rodada.csv"

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
        FROM rodadas
        WHERE ano = %s AND numero = %s
    """, (ano, numero))

    row = cursor.fetchone()

    if row:
        rodada_id, mes_atual = row

        # Atualiza o mês se for diferente
        if mes_atual != mes:
            cursor.execute("""
                UPDATE rodadas
                SET mes = %s
                WHERE id = %s
            """, (mes, rodada_id))

        return rodada_id

    cursor.execute("""
        INSERT INTO rodadas (ano, numero, mes, status)
        VALUES (%s, %s, %s, 'encerrada')
        RETURNING id
    """, (ano, numero, mes))

    return cursor.fetchone()[0]



def get_time_id(cursor, time_id, temporada):
    cursor.execute(
        """
        SELECT id
        FROM times
        WHERE id = %s
          AND temporada = %s
        """,
        (time_id, temporada)
    )
    row = cursor.fetchone()
    if not row:
        raise Exception(
            f"Time não encontrado: id={time_id}, temporada={temporada}"
        )
    return row[0]


def inserir_resultado(cursor, time_id, rodada_id, pontos, patrimonio, posicao):
    cursor.execute(
        """
        INSERT INTO resultado_rodada (
            time_id,
            rodada_id,
            pontos,
            patrimonio,
            posicao,
            fonte
        )
        VALUES (%s, %s, %s, %s, %s, 'csv')
        ON CONFLICT (time_id, rodada_id)
        DO UPDATE SET
            pontos = EXCLUDED.pontos,
            patrimonio = EXCLUDED.patrimonio,
            posicao = EXCLUDED.posicao,
            fonte = 'csv'
        """,
        (time_id, rodada_id, pontos, patrimonio, posicao)
    )

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
                ano = int(linha["ano"])
                rodada = int(linha["rodada"])

                ano_importado = ano
                rodada_importada = rodada

                time_id_csv = int(linha["cartola_time_id"])
                pontos = float(linha["pontos"])
                patrimonio = float(linha["patrimonio"])
                posicao = int(linha["posicao"])

                rodada_id = get_or_create_rodada(
                    cursor,
                    ano,
                    rodada,
                    mes_referencia
                )

                time_id = get_time_id(cursor, time_id_csv, ano)

                inserir_resultado(
                    cursor,
                    time_id,
                    rodada_id,
                    pontos,
                    patrimonio,
                    posicao
                )

        conn.commit()
        print("✅ CSV importado com sucesso!")
        print(f"Ano importado: {ano_importado}")
        print(f"Rodada importada: {rodada_importada}")

        processar_copa_brasil(conn, ano_importado, rodada_importada)



    except Exception as erro:
        conn.rollback()
        print("❌ Erro:", erro)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    importar_csv()
