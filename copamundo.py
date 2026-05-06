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
        print("[Copa Mundo] Rodada 11 - Repescagem + gerar jogos")

        rodada_11_repescagem(cursor, ano)

        # evita duplicar
        cursor.execute("""
            SELECT COUNT(*)
            FROM copamundo_jogos
            WHERE ano = %s
        """, (ano,))

        if cursor.fetchone()[0] == 0:
            gerar_jogos_grupos(cursor, ano)

    # =========================
    # RODADA 12 → COMEÇA GRUPOS
    # =========================
    elif rodada == 12:
        resolver_jogos_grupos(cursor, ano, rodada)

    # =========================
    # RODADAS 13 e 14
    # =========================
    elif rodada in [13, 14]:
        resolver_jogos_grupos(cursor, ano, rodada)

        if rodada == 14:
            classificados = classificar_grupos(cursor, ano)
            criar_oitavas(cursor, ano)

    # =========================
    # RODADA 15 → MATA-MATA
    # =========================
    elif rodada == 15:
        resolver_confrontos(cursor, ano, rodada)

        # 🔥 CRIA OITAVAS
        criar_proxima_fase(cursor, ano, "Oitavas de Final", 2, 16)
        
    elif rodada == 16:
        resolver_confrontos(cursor, ano, rodada)
        criar_proxima_fase(cursor, ano, "Quartas de Final", 3, 17)   
        
    elif rodada == 17:
        resolver_confrontos(cursor, ano, rodada)
        criar_proxima_fase(cursor, ano, "Semifinal", 4, 18)     
        
    elif rodada == 18:
        resolver_confrontos(cursor, ano, rodada)
        criar_proxima_fase(cursor, ano, "Final", 5, 19)   
        
    elif rodada == 19:
        resolver_confrontos(cursor, ano, rodada)

        print("🏆 CAMPEÃO DEFINIDO")    
        
        

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
            return 2, 1  # ✅ mudou aqui
        return 3, 0

    elif pb > pa:
        if pb - pa <= 5:
            return 1, 2  # ✅ mudou aqui
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

        for t in [ta, tb]:
            tabela[grupo].setdefault(t, {
                "pts": 0,
                "pf": 0,
                "ps": 0
            })

        pa = pa or 0
        pb = pb or 0

        tabela[grupo][ta]["pf"] += pa
        tabela[grupo][ta]["ps"] += pb

        tabela[grupo][tb]["pf"] += pb
        tabela[grupo][tb]["ps"] += pa

        pta, ptb = calcular_pontos(pa, pb)

        tabela[grupo][ta]["pts"] += pta
        tabela[grupo][tb]["pts"] += ptb

    classificados = {}

    for grupo, times in tabela.items():

        ranking = sorted(
            times.items(),
            key=lambda x: (
                x[1]["pts"],
                x[1]["pf"] - x[1]["ps"],  # saldo
                x[1]["pf"]               # ataque
            ),
            reverse=True
        )

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
        
        for t in [ta, tb]:
            tabela[grupo].setdefault(t, {
                "pts": 0,
                "vitorias": 0,
                "empates": 0,
                "derrotas": 0,
                "pf": 0,
                "ps": 0
            })

        # ignora jogo não jogado
        if pa is None and pb is None:
            continue

        pa = pa or 0
        pb = pb or 0

        # soma gols/pontos feitos e sofridos
        tabela[grupo][ta]["pf"] += pa
        tabela[grupo][ta]["ps"] += pb

        tabela[grupo][tb]["pf"] += pb
        tabela[grupo][tb]["ps"] += pa

        # resultado
        if pa > pb:
            tabela[grupo][ta]["vitorias"] += 1
            tabela[grupo][tb]["derrotas"] += 1

        elif pb > pa:
            tabela[grupo][tb]["vitorias"] += 1
            tabela[grupo][ta]["derrotas"] += 1

        else:
            tabela[grupo][ta]["empates"] += 1
            tabela[grupo][tb]["empates"] += 1

        # pontos campeonato
        pta, ptb = calcular_pontos(pa, pb)

        tabela[grupo][ta]["pts"] += pta
        tabela[grupo][tb]["pts"] += ptb

    # nomes dos times
    cursor.execute("SELECT id, nome_time FROM times")
    nomes = dict(cursor.fetchall())

    grupos = {}

    for grupo, times in tabela.items():

        ranking = sorted(
            times.items(),
            key=lambda x: (
                x[1]["pts"],
                x[1]["pf"] - x[1]["ps"],  # saldo
                x[1]["pf"]               # ataque
            ),
            reverse=True
        )

        grupos[grupo] = [
            {
                "time": nomes[tid],
                "pontos": dados["pts"],
                "vitorias": dados["vitorias"],
                "empates": dados["empates"],
                "derrotas": dados["derrotas"],
                "pf": dados["pf"],
                "ps": dados["ps"],
                "saldo": dados["pf"] - dados["ps"],
                "classificado": i < 2
            }
            for i, (tid, dados) in enumerate(ranking)
        ]

    return grupos

def criar_oitavas(cursor, ano):
    
    cursor.execute("""
    SELECT COUNT(*)
    FROM competicao_confrontos
    WHERE competicao_id = 4
""")

    if cursor.fetchone()[0] > 0:
        print("[Copa Mundo] Oitavas já existem, pulando...")
        return

    print("[Copa Mundo] Criando Oitavas")

    classificados = classificar_grupos(cursor, ano)

    grupos = sorted(classificados.keys())

    pares = []

    for g in grupos:
        primeiro = classificados[g][0][0]
        segundo = classificados[g][1][0]

        pares.append({
            "grupo": g,
            "primeiro": primeiro,
            "segundo": segundo
        })

    confrontos = []

    for i in range(0, len(pares), 2):
        g1 = pares[i]
        g2 = pares[i + 1]

        confrontos.append((g1["primeiro"], g2["segundo"]))  # A1 x B2
        confrontos.append((g2["primeiro"], g1["segundo"]))  # B1 x A2

    # =========================
    # CRIAR FASE
    # =========================

    cursor.execute("""
        INSERT INTO competicao_fases (
            competicao_id,
            nome_fase,
            ordem,
            qtd_times_inicio,
            qtd_times_fim,
            rodada,
            status
        )
        VALUES (4, 'Segunda Fase', 1, 32, 16, 15, 'em_andamento')
        RETURNING id
    """)

    fase_id = cursor.fetchone()[0]

    # =========================
    # CRIAR CONFRONTOS COM LADO
    # =========================

    total = len(confrontos)

    for i, (a, b) in enumerate(confrontos):

        lado = "esquerda" if i < total / 2 else "direita"

        print(f"Oitavas {i+1}: {a} x {b} ({lado})")

        cursor.execute("""
            INSERT INTO competicao_confrontos (
                competicao_id,
                fase_id,
                rodada,
                ordem_na_fase,
                time_a_id,
                time_b_id,
                status,
                lado_chave
            )
            VALUES (4, %s, 15, %s, %s, %s, 'criado', %s)
        """, (fase_id, i+1, a, b, lado))     
                                   
def criar_proxima_fase(cursor, ano, nome_fase, ordem_fase, rodada_base):

    print(f"[Copa Mundo] Criando fase: {nome_fase}")

    # =========================
    # EVITAR DUPLICAÇÃO
    # =========================
    cursor.execute("""
        SELECT COUNT(*)
        FROM competicao_fases
        WHERE competicao_id = 4
        AND nome_fase = %s
    """, (nome_fase,))

    if cursor.fetchone()[0] > 0:
        print(f"[Copa Mundo] {nome_fase} já existe")
        return

    # =========================
    # BUSCAR ÚLTIMA FASE
    # =========================
    cursor.execute("""
        SELECT id
        FROM competicao_fases
        WHERE competicao_id = 4
        ORDER BY ordem DESC
        LIMIT 1
    """)
    fase_anterior_id = cursor.fetchone()[0]

    # =========================
    # BUSCAR CONFRONTOS
    # =========================
    cursor.execute("""
        SELECT 
            time_a_id,
            time_b_id,
            pontuacao_a,
            pontuacao_b,
            lado_chave,
            ordem_na_fase
        FROM competicao_confrontos
        WHERE fase_id = %s
        ORDER BY ordem_na_fase
    """, (fase_anterior_id,))

    confrontos = cursor.fetchall()

    vencedores_esq = []
    vencedores_dir = []

    # =========================
    # DEFINIR VENCEDORES
    # =========================
    for a, b, pa, pb, lado, ordem in confrontos:

        if pa is None or pb is None:
            print("⚠️ Ainda existem jogos sem resultado")
            return

        if pa > pb:
            vencedor = a
        elif pb > pa:
            vencedor = b
        else:
            print("⚠️ Empate não permitido no mata-mata")
            return

        if lado == "esquerda":
            vencedores_esq.append(vencedor)
        else:
            vencedores_dir.append(vencedor)

    # =========================
    # MONTAR CONFRONTOS
    # =========================
    def montar(times):
        jogos = []
        total = len(times)

        for i in range(total // 2):
            jogos.append((times[i], times[total - 1 - i]))

        return jogos

    jogos_esq = montar(vencedores_esq)
    jogos_dir = montar(vencedores_dir)

    # =========================
    # CRIAR NOVA FASE
    # =========================
    cursor.execute("""
        INSERT INTO competicao_fases (
            competicao_id,
            nome_fase,
            ordem,
            qtd_times_inicio,
            qtd_times_fim,
            rodada,
            status
        )
        VALUES (4, %s, %s, %s, %s, %s, 'criado')
        RETURNING id
    """, (
        nome_fase,
        ordem_fase,
        len(confrontos),
        len(confrontos)//2,
        rodada_base
    ))

    fase_id = cursor.fetchone()[0]

    # =========================
    # INSERIR NOVOS JOGOS
    # =========================
    ordem = 1

    for a, b in jogos_esq:
        cursor.execute("""
            INSERT INTO competicao_confrontos (
                competicao_id,
                fase_id,
                rodada,
                ordem_na_fase,
                time_a_id,
                time_b_id,
                status,
                lado_chave
            )
            VALUES (4, %s, %s, %s, %s, %s, 'criado', 'esquerda')
        """, (fase_id, rodada_base, ordem, a, b))
        ordem += 1

    for a, b in jogos_dir:
        cursor.execute("""
            INSERT INTO competicao_confrontos (
                competicao_id,
                fase_id,
                rodada,
                ordem_na_fase,
                time_a_id,
                time_b_id,
                status,
                lado_chave
            )
            VALUES (4, %s, %s, %s, %s, %s, 'criado', 'direita')
        """, (fase_id, rodada_base, ordem, a, b))
        ordem += 1

    print(f"[Copa Mundo] {nome_fase} criada com sucesso!")
    
    
def resolver_confrontos(cursor, ano, rodada):

    print(f"[Copa Mundo] Resolvendo confrontos - Rodada {rodada}")

    # =========================
    # PEGAR ID DA RODADA
    # =========================
    cursor.execute("""
        SELECT id
        FROM rodadas
        WHERE numero = %s AND ano = %s
    """, (rodada, ano))

    rodada_id = cursor.fetchone()[0]

    # =========================
    # RANKING GERAL (DESEMPATE)
    # =========================
    cursor.execute("""
        SELECT
            t.id,
            SUM(rr.pontos) AS total
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        WHERE r.ano = %s
        GROUP BY t.id
    """, (ano,))

    ranking = {row[0]: row[1] for row in cursor.fetchall()}

    # =========================
    # BUSCAR CONFRONTOS
    # =========================
    cursor.execute("""
        SELECT 
            id,
            time_a_id,
            time_b_id
        FROM competicao_confrontos
        WHERE rodada = %s
        AND competicao_id = 4
    """, (rodada,))

    confrontos = cursor.fetchall()

    # =========================
    # PROCESSAR CADA JOGO
    # =========================
    for confronto_id, time_a, time_b in confrontos:

        # -------- TIME A --------
        cursor.execute("""
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s AND time_id = %s
        """, (rodada_id, time_a))

        res_a = cursor.fetchone()
        pa = res_a[0] if res_a else 0

        # -------- TIME B --------
        cursor.execute("""
            SELECT pontos
            FROM resultado_rodada
            WHERE rodada_id = %s AND time_id = %s
        """, (rodada_id, time_b))

        res_b = cursor.fetchone()
        pb = res_b[0] if res_b else 0

        # =========================
        # DEFINIR VENCEDOR
        # =========================
        if pa > pb:
            vencedor = time_a
            perdedor = time_b

        elif pb > pa:
            vencedor = time_b
            perdedor = time_a

        else:
            # 🔥 DESEMPATE POR RANKING GERAL
            if ranking.get(time_a, 0) >= ranking.get(time_b, 0):
                vencedor = time_a
                perdedor = time_b
            else:
                vencedor = time_b
                perdedor = time_a

        # =========================
        # ATUALIZAR BANCO
        # =========================
        cursor.execute("""
            UPDATE competicao_confrontos
            SET 
                pontuacao_a = %s,
                pontuacao_b = %s,
                vencedor_id = %s,
                perdedor_id = %s,
                status = 'finalizado'
            WHERE id = %s
        """, (pa, pb, vencedor, perdedor, confronto_id))

    print("[Copa Mundo] Confrontos resolvidos!")    

# =========================
# EXECUÇÃO DIRETA
# =========================

if __name__ == "__main__":

    from qual_banco_conectado import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 pegar último ano
    cursor.execute("""
        SELECT MAX(ano)
        FROM rodadas
    """)
    ano = cursor.fetchone()[0]

    if not ano:
        print("⚠️ Nenhum ano encontrado")
        conn.close()
        exit()

    # 🔹 pegar última rodada desse ano
    cursor.execute("""
        SELECT MAX(numero)
        FROM rodadas
        WHERE ano = %s
    """, (ano,))
    rodada = cursor.fetchone()[0]

    if not rodada:
        print("⚠️ Nenhuma rodada encontrada")
    else:
        print(f"[AUTO] Ano {ano} - Rodada {rodada}")
        processar_copa_mundo(conn, ano, rodada)

    conn.close()