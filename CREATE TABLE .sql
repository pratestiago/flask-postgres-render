CREATE TABLE rodadas (
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    status VARCHAR(20),          -- aberta | encerrada | em_andamento
    inicio TIMESTAMP,
    fim TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT uq_rodadas_ano_numero UNIQUE (ano, numero)
);
-- Script — Tabela resultado_rodada
-- sql
-- Copiar código
CREATE TABLE resultado_rodada (
    id SERIAL PRIMARY KEY,

    time_id INTEGER NOT NULL,
    rodada_id INTEGER NOT NULL,

    pontos NUMERIC(6,2),
    patrimonio NUMERIC(10,2),
    variacao_patrimonio NUMERIC(10,2),
    posicao INTEGER,

    fonte VARCHAR(20),           -- csv | api_parcial | api_oficial
    json_dados_api JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    CONSTRAINT fk_resultado_time
        FOREIGN KEY (time_id) REFERENCES times(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_resultado_rodada
        FOREIGN KEY (rodada_id) REFERENCES rodadas(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_resultado_time_rodada
        UNIQUE (time_id, rodada_id)
);


CREATE TABLE divisoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,     -- Ex: Divisão A, B, C, D
    descricao TEXT
);

CREATE TABLE times_divisoes (
    id SERIAL PRIMARY KEY,
    time_id INTEGER NOT NULL REFERENCES times(id),
    divisao_id INTEGER NOT NULL REFERENCES divisoes(id),
    temporada INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (time_id, temporada)
);

INSERT INTO divisoes (nome, descricao) VALUES
('A', 'SERIE A'),
('B', 'SERIE B'),
('C', 'SERIE C'),
('D', 'SERIE D');


-- times ordenados aleatoriamente apenas pra testes 
WITH times_ordenados AS (
    SELECT
        id AS time_id,
        ROW_NUMBER() OVER (ORDER BY random()) AS rn
    FROM times
    WHERE temporada = 2025
    LIMIT 80
)
INSERT INTO times_divisoes (time_id, divisao_id, temporada)
SELECT
    time_id,
    CASE
        WHEN rn BETWEEN 1  AND 20 THEN 1  -- Divisão A
        WHEN rn BETWEEN 21 AND 40 THEN 2  -- Divisão B
        WHEN rn BETWEEN 41 AND 60 THEN 3  -- Divisão C
        WHEN rn BETWEEN 61 AND 80 THEN 4  -- Divisão D
    END AS divisao_id,
    2025
FROM times_ordenados;


-- select de consulta

SELECT
    d.nome AS divisao,
    COUNT(*) AS total_times
FROM times_divisoes td
JOIN divisoes d ON d.id = td.divisao_id
WHERE td.temporada = 2025
GROUP BY d.nome
ORDER BY d.nome;

SELECT t.id, t.nome_time
FROM times t
WHERE t.temporada = 2025
  AND NOT EXISTS (
      SELECT 1
      FROM times_divisoes td
      WHERE td.time_id = t.id
        AND td.temporada = 2025
  );



CREATE TABLE competicoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativa BOOLEAN DEFAULT TRUE
);




-- 1. Competições
CREATE TABLE competicoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativa BOOLEAN DEFAULT TRUE
);

-- 2. Competição por temporada
CREATE TABLE competicoes_temporadas (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER NOT NULL REFERENCES competicoes(id),
    temporada INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (competicao_id, temporada)
);

-- 3. Participantes
CREATE TABLE competicoes_participantes (
    id SERIAL PRIMARY KEY,
    competicao_temporada_id INTEGER NOT NULL REFERENCES competicoes_temporadas(id),
    time_id INTEGER NOT NULL REFERENCES times(id),
    seed INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (competicao_temporada_id, time_id)
);

-- 4. Fases
CREATE TABLE competicoes_fases (
    id SERIAL PRIMARY KEY,
    competicao_temporada_id INTEGER NOT NULL REFERENCES competicoes_temporadas(id),
    nome VARCHAR(50) NOT NULL,
    ordem INTEGER NOT NULL,
    qtd_times INTEGER NOT NULL
);

-- 5. Confrontos
CREATE TABLE competicoes_confrontos (
    id SERIAL PRIMARY KEY,
    fase_id INTEGER NOT NULL REFERENCES competicoes_fases(id),
    time_a_id INTEGER NOT NULL REFERENCES times(id),
    time_b_id INTEGER NOT NULL REFERENCES times(id),
    vencedor_id INTEGER REFERENCES times(id),
    rodada INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Regras extras
ALTER TABLE competicoes_fases
ADD CONSTRAINT uq_fase_ordem UNIQUE (competicao_temporada_id, ordem);

ALTER TABLE competicoes_confrontos
ADD CONSTRAINT chk_times_diferentes CHECK (time_a_id <> time_b_id);
