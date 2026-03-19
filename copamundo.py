# copamundo.py

# =========================
# FUNÇÕES AUXILIARES
# =========================

def calcular_base_grupos(total_times):
    """
    Retorna o maior valor válido para fase de grupos:
    (4, 8, 16, 32, 64, 128...)
    """
    base = 4

    while base * 2 <= total_times:
        base *= 2

    return base


def distribuir_diretos_em_grupos(ranking, diretos):

    grupos = {}

    # criar grupos A até P (16 grupos)
    letras = [chr(i) for i in range(65, 65 + 16)]

    for letra in letras:
        grupos[letra] = []

    # distribuir
    for i in range(diretos):
        grupo = letras[i % 16]
        time = ranking[i]

        grupos[grupo].append(time)

    return grupos


# =========================
# PROCESSADOR PRINCIPAL
# =========================

def processar_copa_mundo(conn, ano, rodada):

    cursor = conn.cursor()

    print(f"[Copa Mundo] Ano {ano} - Rodada {rodada}")

    # Copa Mundo começa na rodada 10
    if rodada < 10:
        print("[Copa Mundo] Rodada ignorada")
        return

    if rodada == 10:

        resultado = rodada_10_classificacao(cursor, ano)

        if not resultado:
            return

        ranking, diretos = resultado

        # =========================
        # DISTRIBUIR DIRETOS NOS GRUPOS
        # =========================

        grupos = distribuir_diretos_em_grupos(ranking, diretos)

        print("\n--- GRUPOS (DIRETOS) ---")

        for grupo, times in grupos.items():
            print(f"\nGrupo {grupo}:")
            for t in times:
                print(f"- {t[1]}")

    elif rodada == 11:
        print("[Copa Mundo] Rodada 11 - (ainda vamos implementar)")

    elif rodada in [12, 13, 14]:
        print("[Copa Mundo] Fase de grupos (ainda vamos implementar)")

    elif rodada >= 15:
        print("[Copa Mundo] Mata-mata (ainda vamos implementar)")

    conn.commit()


# =========================
# RODADA 10
# =========================

def rodada_10_classificacao(cursor, ano):

    print("[Copa Mundo] Rodada 10 - Classificação")

    cursor.execute("""
        SELECT
            t.id,
            t.nome_time,
            rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        JOIN times t ON t.id = rr.time_id
        WHERE r.ano = %s
        AND r.numero = 6  -- <- TESTE (depois volta pra 10)
        ORDER BY rr.pontos DESC
    """, (ano,))

    ranking = cursor.fetchall()

    if not ranking:
        print("⚠️ Nenhum dado encontrado")
        return None

    total_times = len(ranking)

    print(f"Total de times: {total_times}")

    # =========================
    # CALCULAR BASE
    # =========================

    base = calcular_base_grupos(total_times)

    print(f"Base da fase de grupos: {base}")

    # =========================
    # DEFINIR DIRETOS E REPESCAGEM
    # =========================

    excedente = total_times - base

    repescagem_times = excedente * 2
    diretos = total_times - repescagem_times

    print(f"Times diretos: {diretos}")
    print(f"Times na repescagem: {repescagem_times}")

    # =========================
    # DEBUG
    # =========================

    print("\n--- DIRETOS ---")
    for i, time in enumerate(ranking[:diretos], start=1):
        print(f"{i}º - {time[1]}")

    print("\n--- REPESCAGEM ---")
    for i, time in enumerate(ranking[diretos:], start=diretos+1):
        print(f"{i}º - {time[1]}")

    return ranking, diretos


# =========================
# EXECUÇÃO DIRETA
# =========================

if __name__ == "__main__":

    from qual_banco_conectado import get_connection

    conn = get_connection()

    ano = 2026
    rodada = 10

    processar_copa_mundo(conn, ano, rodada)

    conn.close()