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

        inicio = letras.index("N")  # começa no grupo N
        grupo = letras[(inicio + i) % 16]

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

    # =========================
    # RODADA 10
    # =========================
    if rodada == 10:
        
        limpar_copa_mundo(cursor, ano)

        resultado = rodada_10_classificacao(cursor, ano)

        if not resultado:
            return

        ranking, diretos = resultado

        # GRUPOS
        grupos = distribuir_diretos_em_grupos(ranking, diretos)

        print("\n--- GRUPOS (DIRETOS) ---")

        for grupo, times in grupos.items():
            print(f"\nGrupo {grupo}:")
            for t in times:
                print(f"- {t[1]}")

        salvar_grupos(cursor, ano, grupos)

        # REPESCAGEM
        confrontos = gerar_repescagem_com_grupos(ranking, diretos)

        print("\n--- REPESCAGEM (CONFRONTOS) ---")

        for c in confrontos:
            print(f"{c['time_a'][1]} x {c['time_b'][1]} → Grupo {c['grupo']}")

        salvar_repescagem(cursor, ano, confrontos)

    # =========================
    # RODADA 11 → SÓ REPESCAGEM
    # =========================
    elif rodada == 11:
        print("[Copa Mundo] Rodada 11 - Repescagem")
        rodada_11_repescagem(cursor, ano)

    # =========================
    # RODADA 12 → COMEÇA GRUPOS
    # =========================
    elif rodada == 12:
        print("[Copa Mundo] Rodada 12 - Início da Fase de Grupos")
        gerar_jogos_grupos(cursor, ano)
        resolver_jogos_grupos(cursor, ano, rodada)

    # =========================
    # RODADAS 13 e 14
    # =========================
    elif rodada in [13, 14]:
        resolver_jogos_grupos(cursor, ano, rodada)

        if rodada == 14:
            classificados = classificar_grupos(cursor, ano)
            print(classificados)

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

def rodada_11_repescagem(cursor, ano):

    print("[Copa Mundo] Rodada 11 - Repescagem")

    # =========================
    # BUSCAR CONFRONTOS
    # =========================

    cursor.execute("""
        SELECT grupo, time_a_id, time_b_id
        FROM copamundo_repescagem
        WHERE ano = %s
    """, (ano,))

    confrontos = cursor.fetchall()

    # =========================
    # BUSCAR PONTOS RODADA 11
    # =========================

    cursor.execute("""
        SELECT rr.time_id, rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE r.ano = %s
        AND r.numero = 11
    """, (ano,))

    resultados = cursor.fetchall()

    # transformar em dicionário
    pontos = {r[0]: r[1] for r in resultados}

    # =========================
    # DEFINIR VENCEDORES
    # =========================

    vencedores = []

    for grupo, time_a, time_b in confrontos:

        pontos_a = pontos.get(time_a, 0)
        pontos_b = pontos.get(time_b, 0)

        if pontos_a > pontos_b:
            vencedor = time_a

        elif pontos_b > pontos_a:
            vencedor = time_b

        else:
            # desempate → melhor ranking (menor id no ranking inicial)
            vencedor = min(time_a, time_b)

        vencedores.append((grupo, vencedor))

        print(f"Grupo {grupo}: {time_a} x {time_b} → vencedor: {vencedor}")

    # =========================
    # SALVAR NOS GRUPOS
    # =========================

    for grupo, vencedor in vencedores:

        cursor.execute("""
            INSERT INTO copamundo_grupos (ano, grupo, time_id, tipo)
            VALUES (%s, %s, %s, %s)
        """, (ano, grupo, vencedor, "repescagem"))
        
def gerar_jogos_grupos(cursor, ano):

    cursor.execute("""
        SELECT grupo, time_id
        FROM copamundo_grupos
        WHERE ano = %s
        ORDER BY grupo
    """, (ano,))

    dados = cursor.fetchall()

    # organizar por grupo
    grupos = {}

    for grupo, time_id in dados:
        grupos.setdefault(grupo, []).append(time_id)

    for grupo, times in grupos.items():

        if len(times) != 4:
            continue  # segurança

        a, b, c, d = times

        jogos = [
            (12, a, b),
            (12, c, d),
            (13, a, c),
            (13, b, d),
            (14, a, d),
            (14, b, c),
        ]

        for rodada, ta, tb in jogos:
            cursor.execute("""
                INSERT INTO copamundo_jogos
                (ano, grupo, rodada, time_a_id, time_b_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (ano, grupo, rodada, ta, tb))
            
def calcular_pontos(pa, pb):

    pa = pa or 0
    pb = pb or 0

    if pa > pb:
        if pa - pb <= 5:
            return 2, 0
        return 3, 0

    elif pb > pa:
        if pb - pa <= 5:
            return 0, 2
        return 0, 3

    else:
        return 1, 1
    
def resolver_jogos_grupos(cursor, ano, rodada):

    cursor.execute("""
        SELECT id, time_a_id, time_b_id
        FROM copamundo_jogos
        WHERE ano = %s AND rodada = %s
    """, (ano, rodada))

    jogos = cursor.fetchall()

    # buscar pontos da rodada
    cursor.execute("""
        SELECT rr.time_id, rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE r.ano = %s AND r.numero = %s
    """, (ano, rodada))

    resultados = dict(cursor.fetchall())

    for jogo_id, ta, tb in jogos:

        pa = float(resultados.get(ta, 0) or 0)
        pb = float(resultados.get(tb, 0) or 0)

        cursor.execute("""
            UPDATE copamundo_jogos
            SET pontos_a = %s,
                pontos_b = %s
            WHERE id = %s
        """, (pa, pb, jogo_id))
        
def classificar_grupos(cursor, ano):

    cursor.execute("""
        SELECT grupo, time_a_id, time_b_id, pontos_a, pontos_b
        FROM copamundo_jogos
        WHERE ano = %s
    """, (ano,))

    jogos = cursor.fetchall()

    tabela = {}

    for grupo, ta, tb, pa, pb in jogos:

        tabela.setdefault(grupo, {})
        tabela[grupo].setdefault(ta, 0)
        tabela[grupo].setdefault(tb, 0)

        pta, ptb = calcular_pontos(pa, pb)

        tabela[grupo][ta] += pta
        tabela[grupo][tb] += ptb

    classificados = {}

    for grupo, times in tabela.items():

        ranking = sorted(times.items(), key=lambda x: x[1], reverse=True)

        classificados[grupo] = ranking[:2]

    return classificados

def get_classificacao_grupos(cursor, ano):

    cursor.execute("""
        SELECT 
            cj.grupo,
            cj.time_a_id,
            cj.time_b_id,
            cj.pontos_a,
            cj.pontos_b
        FROM copamundo_jogos cj
        WHERE cj.ano = %s
    """, (ano,))

    jogos = cursor.fetchall()

    tabela = {}

    for grupo, ta, tb, pa, pb in jogos:

        tabela.setdefault(grupo, {})
        tabela[grupo].setdefault(ta, 0)
        tabela[grupo].setdefault(tb, 0)

    # só processa se ambos tiverem pontuação
    # ignora jogo não processado (ambos NULL)
        if pa is None and pb is None:
            continue

        # trata parcialmente (segurança)
        pa = pa or 0
        pb = pb or 0

        pta, ptb = calcular_pontos(pa, pb)

        tabela[grupo][ta] += pta
        tabela[grupo][tb] += ptb

    # pegar nomes dos times
    cursor.execute("SELECT id, nome_time FROM times")
    nomes = dict(cursor.fetchall())

    grupos = {}

    for grupo, times in tabela.items():

        ranking = sorted(times.items(), key=lambda x: x[1], reverse=True)

        grupos[grupo] = [
            {
                "time": nomes[tid],
                "pontos": pts,
                "classificado": i < 2
            }
            for i, (tid, pts) in enumerate(ranking)
        ]

    return grupos                                 

# =========================
# EXECUÇÃO DIRETA
# =========================

if __name__ == "__main__":

    from qual_banco_conectado import get_connection

    conn = get_connection()

    ano = 2026
    rodada = 12

    processar_copa_mundo(conn, ano, rodada)

    conn.close()