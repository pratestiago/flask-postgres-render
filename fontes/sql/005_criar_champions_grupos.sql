BEGIN;

CREATE TABLE IF NOT EXISTS champions_grupos (
    id SERIAL PRIMARY KEY,

    competicao_id INTEGER NOT NULL,
    ano INTEGER NOT NULL,

    grupo VARCHAR(1) NOT NULL,
    time_id INTEGER NOT NULL,

    origem VARCHAR(20) NOT NULL,
    ranking_inicial INTEGER NOT NULL,

    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_champions_grupos_competicao
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_champions_grupos_time
        FOREIGN KEY (time_id)
        REFERENCES times(id),

    CONSTRAINT uq_champions_grupo_time
        UNIQUE (competicao_id, time_id),

    CONSTRAINT ck_champions_grupo
        CHECK (grupo BETWEEN 'A' AND 'P'),

    CONSTRAINT ck_champions_grupos_origem
        CHECK (origem IN ('direto', 'repescagem'))
);

CREATE INDEX IF NOT EXISTS idx_champions_grupos_competicao
    ON champions_grupos (competicao_id);

CREATE INDEX IF NOT EXISTS idx_champions_grupos_ano_grupo
    ON champions_grupos (ano, grupo);

INSERT INTO schema_migrations (
    versao,
    descricao
)
VALUES (
    '005',
    'Criação da tabela de grupos da Champions'
)
ON CONFLICT (versao) DO NOTHING;

COMMIT;