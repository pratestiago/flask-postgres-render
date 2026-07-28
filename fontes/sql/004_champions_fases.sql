-- 004_champions_fases.sql
-- Cadastra as fases da Champions 2026.
-- Seguro para executar mais de uma vez: não duplica fases já existentes.

DO $$
DECLARE
    v_competicao_id INTEGER;
BEGIN
    SELECT id
      INTO v_competicao_id
      FROM competicoes
     WHERE tipo = 'champions'
       AND ano = 2026
     ORDER BY id
     LIMIT 1;

    IF v_competicao_id IS NULL THEN
        RAISE EXCEPTION 'Champions 2026 não encontrada na tabela competicoes.';
    END IF;

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
        fase.nome_fase,
        fase.ordem,
        fase.qtd_times_inicio,
        fase.qtd_times_fim,
        fase.rodada,
        fase.status
    FROM (
        VALUES
            ('repescagem',    1, 38, 19, 21, 'criado'),
            ('Fase de Grupos',2, 64, 32, 23, 'criado'),
            ('16-avos',       3, 32, 16, 29, 'criado'),
            ('Oitavas de Final', 4, 16, 8, 31, 'criado'),
            ('Quartas de Final', 5, 8, 4, 33, 'criado'),
            ('Semifinal',     6, 4, 2, 35, 'criado'),
            ('Final',         7, 2, 1, 37, 'criado')
    ) AS fase(
        nome_fase,
        ordem,
        qtd_times_inicio,
        qtd_times_fim,
        rodada,
        status
    )
    WHERE NOT EXISTS (
        SELECT 1
          FROM competicao_fases cf
         WHERE cf.competicao_id = v_competicao_id
           AND LOWER(cf.nome_fase) = LOWER(fase.nome_fase)
    );
END
$$;

-- Conferência
SELECT
    c.id AS competicao_id,
    c.tipo,
    c.ano,
    cf.id AS fase_id,
    cf.nome_fase,
    cf.ordem,
    cf.qtd_times_inicio,
    cf.qtd_times_fim,
    cf.rodada,
    cf.status
FROM competicoes c
JOIN competicao_fases cf
  ON cf.competicao_id = c.id
WHERE c.tipo = 'champions'
  AND c.ano = 2026
ORDER BY cf.ordem;
