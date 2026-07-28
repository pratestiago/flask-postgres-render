BEGIN;

CREATE TABLE IF NOT EXISTS competicao_confronto_jogos (
    id SERIAL PRIMARY KEY,

    confronto_id INTEGER NOT NULL,
    rodada_id INTEGER NOT NULL,

    ordem SMALLINT NOT NULL,

    pontuacao_a NUMERIC(6,2),
    pontuacao_b NUMERIC(6,2),

    processado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_confronto_jogo
        FOREIGN KEY (confronto_id)
        REFERENCES competicao_confrontos(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_rodada_confronto_jogo
        FOREIGN KEY (rodada_id)
        REFERENCES rodadas(id),

    CONSTRAINT ck_confronto_jogo_ordem
        CHECK (ordem IN (1, 2)),

    CONSTRAINT uq_confronto_jogo_ordem
        UNIQUE (confronto_id, ordem)
);

CREATE INDEX IF NOT EXISTS idx_confronto_jogos_rodada
    ON competicao_confronto_jogos (rodada_id);

INSERT INTO schema_migrations (
    versao,
    descricao
)
VALUES (
    '002',
    'Criação da tabela de jogos de ida e volta dos confrontos'
)
ON CONFLICT (versao) DO NOTHING;

COMMIT;