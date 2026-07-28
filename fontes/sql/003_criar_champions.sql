BEGIN;

DO $$
DECLARE
    v_competicao_id INTEGER;
BEGIN
    -- Busca a Champions 2026, caso ela já exista
    SELECT id
    INTO v_competicao_id
    FROM competicoes
    WHERE nome = 'Champions'
      AND ano = 2026
    ORDER BY id
    LIMIT 1;

    -- Cria a competição somente se ainda não existir
    IF v_competicao_id IS NULL THEN
        INSERT INTO competicoes (
            nome,
            ano,
            tipo,
            rodada_inicio,
            status,
            rodada_atual
        )
        VALUES (
            'Champions',
            2026,
            'champions',
            20,
            'ativa',
            20
        )
        RETURNING id INTO v_competicao_id;
    END IF;

    -- Repescagem: ida nas 21 e volta na 22
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        'Repescagem',
        1,
        38,
        19,
        21,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 1
    );

    -- Grupos: rodadas 23 a 28
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        'Fase de Grupos',
        2,
        64,
        32,
        23,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 2
    );

    -- 16-avos: ida na 29 e volta na 30
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        '16-avos',
        3,
        32,
        16,
        29,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 3
    );

    -- Oitavas: ida na 31 e volta na 32
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        'Oitavas de Final',
        4,
        16,
        8,
        31,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 4
    );

    -- Quartas: ida na 33 e volta na 34
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        'Quartas de Final',
        5,
        8,
        4,
        33,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 5
    );

    -- Semifinal: ida na 35 e volta na 36
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        'Semifinal',
        6,
        4,
        2,
        35,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 6
    );

    -- Final: jogo único na rodada 37
    INSERT INTO competicao_fases (
        competicao_id,
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    SELECT
        v_competicao_id,
        'Final',
        7,
        2,
        1,
        37,
        'criado'
    WHERE NOT EXISTS (
        SELECT 1
        FROM competicao_fases
        WHERE competicao_id = v_competicao_id
          AND ordem = 7
    );
END
$$;

INSERT INTO schema_migrations (
    versao,
    descricao
)
VALUES (
    '003',
    'Criação da Champions 2026 e de suas fases'
)
ON CONFLICT (versao) DO NOTHING;

COMMIT;