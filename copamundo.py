# copamundo.py

# =========================
# FUNÇÕES AUXILIARES
# =========================

def calcular_base_grupos(total_times):
    base = 4

    while base * 2 <= total_times:
        base *= 2

    return base


def distribuir_diretos_em_grupos(ranking, diretos):

    grupos = {}

    letras = [chr(i) for i in range(65, 65 + 16)]

    for letra in letras:
        grupos[letra] = []

    for i in range(diretos):
        grupo = letras[i % 16]
        time = ranking[i]
        grupos[grupo].append(time)

    return grupos


def gerar_repescagem_com_grupos(ranking, diretos):

    repescagem = ranking[diretos:]

    confrontos = []

    letras = [chr(i) for i in range(65, 65 + 16)]

    total = len(repescagem)

    for i in range(total // 2):

        time_a = repescagem[i]
        time_b = repescagem[total - 1 - i]

        grupo = letras[i % 16]

        confrontos.append({
            "grupo": grupo,
            "time_a": time_a,
            "time_b": time_b
        })

    return confrontos


# =========================
# PROCESSADOR PRINCIPAL
# =========================

def processar_copa_mundo(conn, ano, rodada):

    cursor = conn.cursor()

    print(f"[Copa Mundo] Ano {ano} - Rodada {rodada}")

    if rodada < 10:
        print("[Copa Mundo] Rodada ignorada")
        return

    if rodada == 10:
        
        limpar_copa_mundo(cursor, ano)

        resultado = rodada_10_classificacao(cursor, ano)

        if not resultado:
            return

        ranking, diretos = resultado

        # =========================
        # GRUPOS (DIRETOS)
        # =========================

        grupos = distribuir_diretos_em_grupos(ranking, diretos)

        print("\n--- GRUPOS (DIRETOS) ---")

        for grupo, times in grupos.items():
            print(f"\nGrupo {grupo}:")
            for t in times:
                print(f"- {t[1]}")

        # 💾 SALVAR
        salvar_grupos(cursor, ano, grupos)

        # =========================
        # REPESCAGEM
        # =========================

        confrontos = gerar_repescagem_com_grupos(ranking, diretos)

        print("\n--- REPESCAGEM (CONFRONTOS) ---")

        for c in confrontos:
            print(f"{c['time_a'][1]} x {c['time_b'][1]} → Grupo {c['grupo']}")
            
        # 💾 SALVAR
        salvar_repescagem(cursor, ano, confrontos)    

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
        AND r.numero = 10  -- TESTE (depois mudar pra 10)
        ORDER BY rr.pontos DESC
    """, (ano,))

    ranking = cursor.fetchall()

    if not ranking:
        print("⚠️ Nenhum dado encontrado")
        return None

    total_times = len(ranking)

    print(f"Total de times: {total_times}")

    base = calcular_base_grupos(total_times)

    print(f"Base da fase de grupos: {base}")

    excedente = total_times - base

    repescagem_times = excedente * 2
    diretos = total_times - repescagem_times

    print(f"Times diretos: {diretos}")
    print(f"Times na repescagem: {repescagem_times}")

    print("\n--- DIRETOS ---")
    for i, time in enumerate(ranking[:diretos], start=1):
        print(f"{i}º - {time[1]}")

    print("\n--- REPESCAGEM ---")
    for i, time in enumerate(ranking[diretos:], start=diretos+1):
        print(f"{i}º - {time[1]}")

    return ranking, diretos

def salvar_grupos(cursor, ano, grupos):

    for grupo, times in grupos.items():
        for t in times:

            time_id = t[0]  # id do time

            cursor.execute("""
                INSERT INTO copamundo_grupos (ano, grupo, time_id, tipo)
                VALUES (%s, %s, %s, %s)
            """, (ano, grupo, time_id, "direto"))

def salvar_repescagem(cursor, ano, confrontos):

    for c in confrontos:

        cursor.execute("""
            INSERT INTO copamundo_repescagem (ano, grupo, time_a_id, time_b_id)
            VALUES (%s, %s, %s, %s)
        """, (
            ano,
            c["grupo"],
            c["time_a"][0],
            c["time_b"][0]
        ))
        
        
def limpar_copa_mundo(cursor, ano):

    cursor.execute("""
        DELETE FROM copamundo_grupos
        WHERE ano = %s
    """, (ano,))

    cursor.execute("""
        DELETE FROM copamundo_repescagem
        WHERE ano = %s
    """, (ano,))        


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