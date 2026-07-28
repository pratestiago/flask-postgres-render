BEGIN;

CREATE TABLE IF NOT EXISTS schema_migrations (
    id BIGSERIAL PRIMARY KEY,
    versao VARCHAR(20) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL,
    executado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (
    versao,
    descricao
)
VALUES (
    '001',
    'Criação da tabela de controle de migrações'
)
ON CONFLICT (versao) DO NOTHING;

COMMIT;