BEGIN;

CREATE TABLE IF NOT EXISTS champions_grupo_jogos (
    id SERIAL PRIMARY KEY,

    competicao_id INTEGER NOT NULL,
    ano INTEGER NOT NULL,

    grupo VARCHAR(1) NOT NULL,
    rodada INTEGER NOT NULL,
    ordem_na_rodada SMALLINT NOT NULL,

    time_a_id INTEGER NOT NULL,
    time_b_id INTEGER NOT NULL,

    pontuacao_a NUMERIC,
    pontuacao_b NUMERIC,

    status VARCHAR(20) NOT NULL DEFAULT 'criado',

    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_champions_jogos_competicao
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_champions_jogos_time_a
        FOREIGN KEY (time_a_id)
        REFERENCES times(id),

    CONSTRAINT fk_champions_jogos_time_b
        FOREIGN KEY (time_b_id)
        REFERENCES times(id),

    CONSTRAINT uq_champions_grupo_rodada_ordem
        UNIQUE (
            competicao_id,
            grupo,
            rodada,
            ordem_na_rodada
        ),

    CONSTRAINT ck_champions_jogos_grupo
        CHECK (grupo BETWEEN 'A' AND 'P'),

    CONSTRAINT ck_champions_jogos_ordem
        CHECK (ordem_na_rodada IN (1, 2))
);

CREATE INDEX IF NOT EXISTS idx_champions_grupo_jogos
    ON champions_grupo_jogos (
        competicao_id,
        grupo,
        rodada
    );

INSERT INTO schema_migrations (
    versao,
    descricao
)
VALUES (
    '006',
    'Criação dos jogos da fase de grupos da Champions'
)
ON CONFLICT (versao) DO NOTHING;

COMMIT;