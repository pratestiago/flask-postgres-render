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
    """
    Retorna conexão com o banco:
    - DATABASE_URL -> Neon
    - senão -> Local
    """
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


def print_info_conexao(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            current_database(),
            current_user,
            inet_server_addr()
    """)
    banco, usuario, host = cursor.fetchone()
    print("📡 INFORMAÇÕES DA CONEXÃO")
    print(f"Banco   : {banco}")
    print(f"Usuário : {usuario}")
    print(f"Host    : {host}")
    cursor.close()


# =========================
# FUNÇÕES DA COPA BRASIL
# =========================

def get_or_create_competicao(cursor, nome, descricao=None):
    cursor.execute(
        """
        SELECT id
        FROM competicoes
        WHERE nome = %s
        """,
        (nome,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO competicoes (nome, descricao)
        VALUES (%s, %s)
        RETURNING id
        """,
        (nome, descricao)
    )
    return cursor.fetchone()[0]


def get_or_create_competicao_temporada(cursor, competicao_id, temporada):
    cursor.execute(
        """
        SELECT id
        FROM competicoes_temporadas
        WHERE competicao_id = %s
          AND temporada = %s
        """,
        (competicao_id, temporada)
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO competicoes_temporadas (competicao_id, temporada)
        VALUES (%s, %s)
        RETURNING id
        """,
        (competicao_id, temporada)
    )
    return cursor.fetchone()[0]


def buscar_ranking_rodada(cursor, temporada, numero_rodada):
    cursor.execute(
        """
        SELECT
            t.id AS time_id,
            t.nome_time,
            rr.posicao AS ranking
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        JOIN times t ON t.id = rr.time_id
        WHERE r.ano = %s
          AND r.numero = %s
        ORDER BY rr.posicao
        """,
        (temporada, numero_rodada)
    )

    rows = cursor.fetchall()

    ranking = []
    for row in rows:
        ranking.append({
            "id": row[0],
            "nome": row[1],
            "ranking": row[2]
        })

    return ranking


def inserir_participantes(cursor, competicao_temporada_id, ranking):
    """
    Insere os participantes da Copa Brasil
    usando o ranking como seed.
    """
    inseridos = 0

    for t in ranking:
        cursor.execute(
            """
            INSERT INTO competicoes_participantes
                (competicao_temporada_id, time_id, seed)
            VALUES (%s, %s, %s)
            ON CONFLICT (competicao_temporada_id, time_id)
            DO NOTHING
            """,
            (competicao_temporada_id, t["id"], t["ranking"])
        )
        inseridos += 1

    return inseridos

def maior_potencia_de_2(n):
    potencia = 1
    while potencia * 2 <= n:
        potencia *= 2
    return potencia


def nome_da_fase(qtd_times):
    if qtd_times == 2:
        return "FINAL"
    elif qtd_times == 4:
        return "SEMIFINAL"
    elif qtd_times == 8:
        return "QUARTAS DE FINAL"
    else:
        return f"FASE DE {qtd_times}"
    
def gerar_fases_copa_brasil(cursor, competicao_temporada_id):
    """
    Gera as fases da Copa Brasil dinamicamente.
    Remove confrontos e fases existentes antes de recriar.
    """

    # 0. Apagar confrontos primeiro (ordem correta)
    cursor.execute(
        """
        DELETE FROM competicoes_confrontos
        WHERE fase_id IN (
            SELECT id
            FROM competicoes_fases
            WHERE competicao_temporada_id = %s
        )
        """,
        (competicao_temporada_id,)
    )

    # 1. Apagar fases
    cursor.execute(
        """
        DELETE FROM competicoes_fases
        WHERE competicao_temporada_id = %s
        """,
        (competicao_temporada_id,)
    )

    # 1. Quantos participantes existem?
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM competicoes_participantes
        WHERE competicao_temporada_id = %s
        """,
        (competicao_temporada_id,)
    )
    total_times = cursor.fetchone()[0]

    P = maior_potencia_de_2(total_times)

    fases = []
    ordem = 1

    # 2. Repescagem (se necessário)
    if total_times != P:
        qtd_repescagem = 2 * (total_times - P)
        fases.append({
            "nome": "REPESCAGEM",
            "ordem": ordem,
            "qtd_times": qtd_repescagem
        })
        ordem += 1

    # 3. Fases principais
    qtd = P
    while qtd >= 2:
        fases.append({
            "nome": nome_da_fase(qtd),
            "ordem": ordem,
            "qtd_times": qtd
        })
        ordem += 1
        qtd //= 2

    # 4. Inserir no banco
    for fase in fases:
        cursor.execute(
            """
            INSERT INTO competicoes_fases
                (competicao_temporada_id, nome, ordem, qtd_times)
            VALUES (%s, %s, %s, %s)
            """,
            (
                competicao_temporada_id,
                fase["nome"],
                fase["ordem"],
                fase["qtd_times"]
            )
        )

    return fases


def buscar_fase_repescagem(cursor, competicao_temporada_id):
    cursor.execute(
        """
        SELECT id
        FROM competicoes_fases
        WHERE competicao_temporada_id = %s
          AND nome = 'REPESCAGEM'
        """,
        (competicao_temporada_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise Exception("Fase REPESCAGEM não encontrada")
    return row[0]

def buscar_times_repescagem(cursor, competicao_temporada_id):
    """
    Retorna os times da repescagem ordenados por seed.
    """
    cursor.execute(
        """
        SELECT
            cp.time_id,
            cp.seed
        FROM competicoes_participantes cp
        WHERE cp.competicao_temporada_id = %s
          AND cp.seed > 47
        ORDER BY cp.seed
        """,
        (competicao_temporada_id,)
    )

    return cursor.fetchall()

def gerar_confrontos_repescagem(cursor, competicao_temporada_id):
    fase_id = buscar_fase_repescagem(cursor, competicao_temporada_id)
    times = buscar_times_repescagem(cursor, competicao_temporada_id)

    confrontos = []

    while len(times) > 1:
        time_a = times.pop(0)
        time_b = times.pop(-1)

        confrontos.append((time_a, time_b))

        cursor.execute(
            """
            INSERT INTO competicoes_confrontos
                (fase_id, time_a_id, time_b_id)
            VALUES (%s, %s, %s)
            """,
            (fase_id, time_a[0], time_b[0])
        )

    return confrontos

def buscar_pontos_rodada(cursor, time_id, ano, numero_rodada):
    cursor.execute(
        """
        SELECT rr.pontos
        FROM resultado_rodada rr
        JOIN rodadas r ON r.id = rr.rodada_id
        WHERE rr.time_id = %s
          AND r.ano = %s
          AND r.numero = %s
        """,
        (time_id, ano, numero_rodada)
    )
    row = cursor.fetchone()
    if not row:
        raise Exception(f"Pontos não encontrados para time_id={time_id} na rodada {numero_rodada}")
    return float(row[0])

def buscar_seed(cursor, competicao_temporada_id, time_id):
    cursor.execute(
        """
        SELECT seed
        FROM competicoes_participantes
        WHERE competicao_temporada_id = %s
          AND time_id = %s
        """,
        (competicao_temporada_id, time_id)
    )
    row = cursor.fetchone()
    if not row:
        raise Exception(f"Seed não encontrada para time_id={time_id}")
    return row[0]

def decidir_vencedores_repescagem(cursor, competicao_temporada_id, ano, numero_rodada):
    """
    Decide os vencedores da Repescagem usando os pontos da rodada informada.
    Atualiza vencedor_id em competicoes_confrontos.
    Retorna lista de time_id vencedores.
    """
    # Buscar a fase de repescagem
    cursor.execute(
        """
        SELECT id
        FROM competicoes_fases
        WHERE competicao_temporada_id = %s
          AND nome = 'REPESCAGEM'
        """,
        (competicao_temporada_id,)
    )
    fase_id = cursor.fetchone()[0]

    # Buscar confrontos da repescagem
    cursor.execute(
        """
        SELECT id, time_a_id, time_b_id
        FROM competicoes_confrontos
        WHERE fase_id = %s
        """,
        (fase_id,)
    )
    confrontos = cursor.fetchall()

    vencedores = []

    for confronto_id, time_a, time_b in confrontos:
        pontos_a = buscar_pontos_rodada(cursor, time_a, ano, numero_rodada)
        pontos_b = buscar_pontos_rodada(cursor, time_b, ano, numero_rodada)

        if pontos_a > pontos_b:
            vencedor = time_a
        elif pontos_b > pontos_a:
            vencedor = time_b
        else:
            # desempate por seed (menor seed vence)
            seed_a = buscar_seed(cursor, competicao_temporada_id, time_a)
            seed_b = buscar_seed(cursor, competicao_temporada_id, time_b)
            vencedor = time_a if seed_a < seed_b else time_b

        # Atualiza vencedor no banco
        cursor.execute(
            """
            UPDATE competicoes_confrontos
            SET vencedor_id = %s
            WHERE id = %s
            """,
            (vencedor, confronto_id)
        )

        vencedores.append(vencedor)

    return vencedores

def buscar_vencedores_repescagem(cursor, competicao_temporada_id):
    cursor.execute(
        """
        SELECT DISTINCT vencedor_id
        FROM competicoes_confrontos cc
        JOIN competicoes_fases cf ON cf.id = cc.fase_id
        WHERE cf.competicao_temporada_id = %s
          AND cf.nome = 'REPESCAGEM'
        """,
        (competicao_temporada_id,)
    )
    return [row[0] for row in cursor.fetchall()]

def buscar_times_diretos(cursor, competicao_temporada_id):
    cursor.execute(
        """
        SELECT time_id
        FROM competicoes_participantes
        WHERE competicao_temporada_id = %s
          AND seed <= 47
        ORDER BY seed
        """,
        (competicao_temporada_id,)
    )
    return [row[0] for row in cursor.fetchall()]

def buscar_fase_64(cursor, competicao_temporada_id):
    cursor.execute(
        """
        SELECT id
        FROM competicoes_fases
        WHERE competicao_temporada_id = %s
          AND nome = 'FASE DE 64'
        """,
        (competicao_temporada_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise Exception("Fase de 64 não encontrada")
    return row[0]

def gerar_confrontos_fase_64(cursor, competicao_temporada_id):
    fase_id = buscar_fase_64(cursor, competicao_temporada_id)

    diretos = buscar_times_diretos(cursor, competicao_temporada_id)
    vencedores_repescagem = buscar_vencedores_repescagem(cursor, competicao_temporada_id)

    todos = diretos + vencedores_repescagem

    if len(todos) != 64:
        raise Exception(f"Quantidade inválida de times para Fase de 64: {len(todos)}")

    # ordenar todos por seed
    cursor.execute(
        """
        SELECT time_id, seed
        FROM competicoes_participantes
        WHERE competicao_temporada_id = %s
          AND time_id = ANY(%s)
        ORDER BY seed
        """,
        (competicao_temporada_id, todos)
    )
    ordenados = [row[0] for row in cursor.fetchall()]

    confrontos = []
    while len(ordenados) > 1:
        a = ordenados.pop(0)
        b = ordenados.pop(-1)

        confrontos.append((a, b))

        cursor.execute(
            """
            INSERT INTO competicoes_confrontos
                (fase_id, time_a_id, time_b_id)
            VALUES (%s, %s, %s)
            """,
            (fase_id, a, b)
        )

    return confrontos










# =========================
# TESTE CONTROLADO
# =========================
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conectado ao banco com sucesso!\n")
        print_info_conexao(conn)

        cursor = conn.cursor()

        # 1. Buscar ranking
        print("\n📊 Buscando ranking da rodada 1...")
        ranking = buscar_ranking_rodada(cursor, temporada=2025, numero_rodada=1)

        print(f"Total de times no ranking: {len(ranking)}")

        print("\nTop 10 da rodada 1:")
        for t in ranking[:10]:
            print(f"{t['ranking']}º - {t['nome']} (ID {t['id']})")

        # 2. Criar / buscar competição
        print("\n🏆 Criando/Buscando COPA BRASIL...")
        competicao_id = get_or_create_competicao(
            cursor,
            nome="COPA BRASIL",
            descricao="Competição mata-mata com repescagem dinâmica"
        )
        print(f"ID da competição: {competicao_id}")

        # 3. Criar / buscar temporada
        print("\n📅 Criando/Buscando temporada 2025...")
        competicao_temporada_id = get_or_create_competicao_temporada(
            cursor,
            competicao_id=competicao_id,
            temporada=2025
        )
        print(f"ID da competição_temporada: {competicao_temporada_id}")

        # 4. Inserir participantes
        print("\n👥 Inserindo participantes da Copa Brasil...")
        total_inseridos = inserir_participantes(
            cursor,
            competicao_temporada_id,
            ranking
        )
        print(f"Participantes processados: {total_inseridos}")

        # 5. Gerar fases
        print("\n📐 Gerando fases da Copa Brasil...")
        fases = gerar_fases_copa_brasil(cursor, competicao_temporada_id)

        print("Fases criadas:")
        for f in fases:
            print(f"Ordem {f['ordem']} - {f['nome']} ({f['qtd_times']} times)")

        # 6. Gerar confrontos da repescagem
        print("\n⚔️ Gerando confrontos da REPESCAGEM...")
        confrontos = gerar_confrontos_repescagem(cursor, competicao_temporada_id)

        print(f"Total de confrontos criados: {len(confrontos)}")

        # 7. Decidir vencedores da repescagem (Rodada 2)
        print("\n🏁 Decidindo vencedores da REPESCAGEM (Rodada 2)...")
        vencedores_repescagem = decidir_vencedores_repescagem(
            cursor,
            competicao_temporada_id,
            ano=2025,
            numero_rodada=2
        )

        print(f"Vencedores da repescagem: {len(vencedores_repescagem)}")


        # 8. Gerar confrontos da Fase de 64
        print("\n⚔️ Gerando confrontos da FASE DE 64...")
        confrontos_64 = gerar_confrontos_fase_64(cursor, competicao_temporada_id)
        print(f"Confrontos criados na Fase de 64: {len(confrontos_64)}")





        # 6. Commit FINAL
        conn.commit()

        cursor.close()
        conn.close()

        print("\n✅ PASSO 3.4 CONCLUÍDO COM SUCESSO")

    except Exception as e:
        conn.rollback()
        print("❌ Erro:", e)
