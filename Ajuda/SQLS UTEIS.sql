select * from divisoes;

select * from times_divisoes;

SELECT * FROM divisoes ORDER BY nivel;

CREATE UNIQUE INDEX unique_time_temporada
ON times_divisoes (time_id, temporada)
WHERE ativo = TRUE;

select * from times;

insert into divisoes (nome, nivel, descricao) values
('SERIE A',1,'ELITE DA LIGA'),
('SERIE B',2,'EM BUSCA DA GLORIA'),
('SERIE C',3,'UM DIA CHEGAMOS LÁ '),
('SERIE D',4,'DESAFIO AO GALO'),
('SERIE E',5,'DEEP LIGA');


INSERT INTO times_divisoes (time_id, divisao_id, temporada) VALUES
(1, 1, 2025),(2, 1, 2025),(3, 1, 2025),(4, 1, 2025),(5, 1, 2025),
(6, 1, 2025),(7, 1, 2025),(8, 1, 2025),(9, 1, 2025),(10, 1, 2025),
(11, 1, 2025),(12, 1, 2025),(13, 1, 2025),(14, 1, 2025),(15, 1, 2025),
(16, 1, 2025),(17, 1, 2025),(18, 1, 2025),(19, 1, 2025),(20, 1, 2025);

INSERT INTO times_divisoes (time_id, divisao_id, temporada) VALUES
(21, 2, 2025),(22, 2, 2025),(23, 2, 2025),(24, 2, 2025),(25, 2, 2025),
(26, 2, 2025),(27, 2, 2025),(28, 2, 2025),(29, 2, 2025),(30, 2, 2025),
(31, 2, 2025),(32, 2, 2025),(33, 2, 2025),(34, 2, 2025),(35, 2, 2025),
(36, 2, 2025),(37, 2, 2025),(38, 2, 2025),(39, 2, 2025),(40, 2, 2025);

INSERT INTO times_divisoes (time_id, divisao_id, temporada) VALUES
(41, 3, 2025),(42, 3, 2025),(43, 3, 2025),(44, 3, 2025),(45, 3, 2025),
(46, 3, 2025),(47, 3, 2025),(48, 3, 2025),(49, 3, 2025),(50, 3, 2025),
(51, 3, 2025),(52, 3, 2025),(53, 3, 2025),(54, 3, 2025),(55, 3, 2025),
(56, 3, 2025),(57, 3, 2025),(58, 3, 2025),(59, 3, 2025),(60, 3, 2025);

INSERT INTO times_divisoes (time_id, divisao_id, temporada) VALUES
(61, 4, 2025),(62, 4, 2025),(63, 4, 2025),(64, 4, 2025),(65, 4, 2025),
(66, 4, 2025),(67, 4, 2025),(68, 4, 2025),(69, 4, 2025),(70, 4, 2025),
(71, 4, 2025),(72, 4, 2025),(73, 4, 2025),(74, 4, 2025),(75, 4, 2025),
(76, 4, 2025),(77, 4, 2025),(78, 4, 2025),(79, 4, 2025),(80, 4, 2025),
(81, 4, 2025);

SELECT
  d.nome,
  d.nivel,
  COUNT(*) AS total
FROM times_divisoes td
JOIN divisoes d ON d.id = td.divisao_id
WHERE td.temporada = 2025
GROUP BY d.nome, d.nivel
ORDER BY d.nivel;


CREATE TABLE competicoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ano INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    rodada_inicio INTEGER NOT NULL DEFAULT 2,
    status VARCHAR(50) NOT NULL,
    rodada_atual INTEGER,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nome, ano)
);

CREATE TABLE competicao_times (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER NOT NULL,
    time_id INTEGER NOT NULL,
    ranking_inicial INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'vivo',
    rodada_eliminacao INTEGER,
    classificacao_final INTEGER,
    CONSTRAINT fk_competicao
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_time
        FOREIGN KEY (time_id)
        REFERENCES times (id),
    UNIQUE (competicao_id, time_id)
);

CREATE TABLE competicao_ranking_snapshot (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER NOT NULL,
    rodada INTEGER NOT NULL,
    time_id INTEGER NOT NULL,
    pontuacao NUMERIC(6,2) NOT NULL,
    posicao INTEGER NOT NULL,
    CONSTRAINT fk_competicao_snapshot
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_time_snapshot
        FOREIGN KEY (time_id)
        REFERENCES times (id),
    UNIQUE (competicao_id, time_id)
);

CREATE TABLE competicao_fases (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER NOT NULL,
    nome_fase VARCHAR(50) NOT NULL,
    ordem INTEGER NOT NULL,
    qtd_times_inicio INTEGER NOT NULL,
    qtd_times_fim INTEGER NOT NULL,
    rodada INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    CONSTRAINT fk_competicao_fase
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes (id)
        ON DELETE CASCADE
);

CREATE TABLE competicao_confrontos (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER NOT NULL,
    fase_id INTEGER NOT NULL,
    rodada INTEGER NOT NULL,
    time_a_id INTEGER NOT NULL,
    time_b_id INTEGER NOT NULL,
    ranking_a INTEGER NOT NULL,
    ranking_b INTEGER NOT NULL,
    pontuacao_a NUMERIC(6,2),
    pontuacao_b NUMERIC(6,2),
    vencedor_id INTEGER,
    perdedor_id INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'criado',
    CONSTRAINT fk_competicao_confronto
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_fase
        FOREIGN KEY (fase_id)
        REFERENCES competicao_fases (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_time_a
        FOREIGN KEY (time_a_id)
        REFERENCES times (id),
    CONSTRAINT fk_time_b
        FOREIGN KEY (time_b_id)
        REFERENCES times (id)
);

CREATE TABLE competicao_rodadas_processadas (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER NOT NULL,
    rodada INTEGER NOT NULL,
    processada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_competicao_processada
        FOREIGN KEY (competicao_id)
        REFERENCES competicoes (id)
        ON DELETE CASCADE,
    UNIQUE (competicao_id, rodada)
);



INSERT INTO competicoes (
    nome,
    ano,
    tipo,
    rodada_inicio,
    status
)
VALUES (
    'Copa Brasil',
    2025,
    'mata_morre',
    2,
    'aguardando_rodada_2'
);

TRUNCATE TABLE rodadas RESTART IDENTITY CASCADE;

select * from rodadas;

select * from competicoes;
SELECT * 
FROM competicoes
WHERE nome = 'Copa Brasil'
  AND ano = 2025;


SELECT * FROM competicao_ranking_snapshot WHERE competicao_id = 1 ORDER BY posicao;
SELECT * FROM competicao_times WHERE competicao_id = 1 ORDER BY ranking_inicial;
SELECT status, rodada_atual FROM competicoes WHERE id = 1;

TRUNCATE competicao_confrontos CASCADE;
TRUNCATE competicao_fases CASCADE;
TRUNCATE competicao_ranking_snapshot CASCADE;
TRUNCATE competicao_times CASCADE;
TRUNCATE competicao_rodadas_processadas CASCADE;

UPDATE competicoes
SET status = 'aguardando_rodada_2',
    rodada_atual = NULL
WHERE id = 1;

SELECT COUNT(*)
FROM competicao_times
WHERE competicao_id = 1
  AND status = 'vivo';

  SELECT COUNT(*)
FROM competicao_times
WHERE competicao_id = 1
  AND status = 'eliminado';



  TRUNCATE TABLE rodadas RESTART IDENTITY CASCADE;

select * from rodadas;

select * from competicoes;
SELECT * 
FROM competicoes
WHERE nome = 'Copa Brasil'
  AND ano = 2025;


SELECT * FROM competicao_ranking_snapshot WHERE competicao_id = 1 ORDER BY posicao;
SELECT * FROM competicao_times WHERE competicao_id = 1 ORDER BY ranking_inicial;
SELECT status, rodada_atual FROM competicoes WHERE id = 1;

TRUNCATE competicao_confrontos RESTART IDENTITY  CASCADE;
TRUNCATE competicao_fases RESTART IDENTITY CASCADE;
TRUNCATE competicao_ranking_snapshot RESTART IDENTITY CASCADE;
TRUNCATE competicao_times RESTART IDENTITY CASCADE;
TRUNCATE competicao_rodadas_processadas RESTART IDENTITY  CASCADE;

UPDATE competicoes
SET status = 'aguardando_rodada_2',
    rodada_atual = NULL
WHERE id = 1;

SELECT COUNT(*)
FROM competicao_times
WHERE competicao_id = 1
  AND status = 'vivo';

  SELECT COUNT(*)
FROM competicao_times
WHERE competicao_id = 1
  AND status = 'eliminado';

select * from competicao_confrontos

DELETE FROM competicao_rodadas_processadas
WHERE rodada = 4;


SELECT COUNT(*)
FROM competicao_times
WHERE status = 'vivo';




ALTER TABLE competicao_confrontos
    ALTER COLUMN time_a_id DROP NOT NULL,
    ALTER COLUMN time_b_id DROP NOT NULL,
    ALTER COLUMN ranking_a DROP NOT NULL,
    ALTER COLUMN ranking_b DROP NOT NULL;

	ALTER TABLE competicao_confrontos
ADD COLUMN origem_time_a_confronto_id INTEGER,
ADD COLUMN origem_time_b_confronto_id INTEGER;

ALTER TABLE competicao_confrontos
ADD COLUMN ordem_na_fase INTEGER;

ALTER TABLE competicao_confrontos
ADD CONSTRAINT fk_origem_time_a_confronto
FOREIGN KEY (origem_time_a_confronto_id)
REFERENCES competicao_confrontos (id);

ALTER TABLE competicao_confrontos
ADD CONSTRAINT fk_origem_time_b_confronto
FOREIGN KEY (origem_time_b_confronto_id)
REFERENCES competicao_confrontos (id);

ALTER TABLE competicao_confrontos
ADD CONSTRAINT chk_lado_a_origem
CHECK (
    (time_a_id IS NOT NULL AND origem_time_a_confronto_id IS NULL)
 OR (time_a_id IS NULL AND origem_time_a_confronto_id IS NOT NULL)
);

ALTER TABLE competicao_confrontos
ADD CONSTRAINT chk_lado_b_origem
CHECK (
    (time_b_id IS NOT NULL AND origem_time_b_confronto_id IS NULL)
 OR (time_b_id IS NULL AND origem_time_b_confronto_id IS NOT NULL)
);

ALTER TABLE competicao_confrontos
ADD CONSTRAINT uq_confronto_fase_ordem
UNIQUE (fase_id, ordem_na_fase);


select * from cartoleiros;
select * from competicoes;
select * from divisoes;
select * from times;
select * from times_divisoes

select * from cartoleiros_detalhes;
select * from competicao_confrontos;
select * from competicao_fases;
select * from competicao_ranking_snapshot;
select * from competicao_times;
select * from resultado_rodada;
select * from rodadas;

    SELECT
            r.numero AS rodada,
            c.nome AS cartoleiro,
            t.nome_time,
            rr.patrimonio,
            rr.variacao_patrimonio
        FROM rodadas r
        JOIN resultado_rodada rr ON rr.rodada_id = r.id
        JOIN times t ON t.id = rr.time_id
        JOIN cartoleiros c ON c.id = t.cartoleiro_id
        WHERE r.ano = 2025
          AND r.numero = (
              SELECT MAX(numero)
              FROM rodadas
              WHERE ano = 2025
          )
        ORDER BY rr.patrimonio DESC


TRUNCATE competicao_confrontos RESTART IDENTITY  CASCADE;
TRUNCATE competicao_fases RESTART IDENTITY CASCADE;
TRUNCATE competicao_ranking_snapshot RESTART IDENTITY CASCADE;
TRUNCATE competicao_times RESTART IDENTITY CASCADE;
TRUNCATE competicao_rodadas_processadas RESTART IDENTITY  CASCADE;

TRUNCATE TABLE rodadas RESTART IDENTITY CASCADE;


select * from cartoleiros;
select * from cartoleiros_detalhes;
select * from competicao_confrontos;
select * from competicao_fases;
select * from competicao_ranking_snapshot;
select * from competicao_rodadas_processadas;
select * from competicao_times;
select * from competicoes;
select * from divisoes;
select * from resultado_rodada;
select * from rodadas;
select * from times;
select * from times_divisoes;




insert into cartoleiros (nome)
values
('MAT WM'),
('G VASCONCELOS');

insert into times (cartoleiro_id,nome_time,temporada,ativo)
values 
(76,'WMM United',2026,true),
(77,'sccpguifc',2026,true);

insert into times_divisoes (time_id,divisao_id,temporada,ativo)
values
(81,4,2026,true),
(82,4,2026,true);

####################### duplas ######################

CREATE TABLE IF NOT EXISTS .cartoleiros_duplas
(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS duplas
(
    id SERIAL PRIMARY KEY,
    ano INT NOT NULL,
    nome VARCHAR(100),
    criada_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS duplas_cartoleiros_ligacao
(
    id SERIAL PRIMARY KEY,
    dupla_id INTEGER NOT NULL,
    cartoleiro_id INTEGER NOT NULL,

    CONSTRAINT fk_lig_dupla
        FOREIGN KEY (dupla_id)
        REFERENCES duplas (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_lig_cartoleiro
        FOREIGN KEY (cartoleiro_id)
        REFERENCES duplas_cartoleiros (id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS rodadas_duplas
(
    id SERIAL PRIMARY KEY,
    ano integer NOT NULL,
    numero integer NOT NULL,
    status character varying(20),
    inicio timestamp without time zone,
    fim timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    mes integer,

    CONSTRAINT uq_rodadas_duplas_ano_numero UNIQUE (ano, numero),
    CONSTRAINT chk_rodadas_duplas_mes_valido CHECK (mes >= 1 AND mes <= 12)
);


CREATE TABLE IF NOT EXISTS duplas_pontuacoes
(
    id SERIAL PRIMARY KEY,
    dupla_id INTEGER NOT NULL,
    rodada_id INTEGER NOT NULL,

    pontos NUMERIC(6,2) NOT NULL,

    fonte VARCHAR(20),
    json_dados_api JSONB,

    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE,

    CONSTRAINT uq_dupla_rodada UNIQUE (dupla_id, rodada_id),

    CONSTRAINT fk_dp_dupla
        FOREIGN KEY (dupla_id)
        REFERENCES duplas (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_dp_rodada
        FOREIGN KEY (rodada_id)
        REFERENCES rodadas_duplas (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS duplas_cartoleiros
(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);



CREATE TABLE IF NOT EXISTS duplas_times
(
    id SERIAL PRIMARY KEY,
    cartoleiro_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,

    CONSTRAINT fk_time_cartoleiro
        FOREIGN KEY (cartoleiro_id)
        REFERENCES duplas_cartoleiros (id)
        ON DELETE CASCADE
);



DROP TABLE IF EXISTS
    duplas_pontuacoes,
    duplas_cartoleiros_ligacao,
    duplas_times_ligacao,
    duplas,
    rodadas_duplas,
    duplas_times,
    duplas_cartoleiros
CASCADE;

############################# DUPLAS NOVO ##########################


CREATE TABLE IF NOT EXISTS duplas_cartoleiros
(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);


CREATE TABLE IF NOT EXISTS duplas_times
(
    id SERIAL PRIMARY KEY,
    cartoleiro_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,

    CONSTRAINT fk_time_cartoleiro
        FOREIGN KEY (cartoleiro_id)
        REFERENCES duplas_cartoleiros (id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS duplas
(
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,
    nome VARCHAR(100),
    criada_em TIMESTAMP DEFAULT now()
);


CREATE TABLE IF NOT EXISTS duplas_times_ligacao
(
    id SERIAL PRIMARY KEY,
    dupla_id INTEGER NOT NULL,
    time_id INTEGER NOT NULL,

    CONSTRAINT fk_lig_dupla
        FOREIGN KEY (dupla_id)
        REFERENCES duplas (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_lig_time
        FOREIGN KEY (time_id)
        REFERENCES duplas_times (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rodadas_duplas
(
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    status VARCHAR(20),
    inicio TIMESTAMP WITHOUT TIME ZONE,
    fim TIMESTAMP WITHOUT TIME ZONE,
    mes INTEGER,

    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE,

    CONSTRAINT uq_rodadas_duplas_ano_numero UNIQUE (ano, numero),
    CONSTRAINT chk_rodadas_duplas_mes CHECK (mes >= 1 AND mes <= 12)
);



CREATE TABLE IF NOT EXISTS duplas_pontuacoes
(
    id SERIAL PRIMARY KEY,
    dupla_id INTEGER NOT NULL,
    rodada_id INTEGER NOT NULL,
    pontos NUMERIC(6,2) NOT NULL,

    created_at TIMESTAMP DEFAULT now(),

    CONSTRAINT uq_dupla_rodada UNIQUE (dupla_id, rodada_id),

    CONSTRAINT fk_pont_dupla
        FOREIGN KEY (dupla_id)
        REFERENCES duplas (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_pont_rodada
        FOREIGN KEY (rodada_id)
        REFERENCES rodadas_duplas (id)
        ON DELETE CASCADE
);


DROP TABLE IF EXISTS duplas_pontuacoes CASCADE;

CREATE TABLE IF NOT EXISTS public.duplas_times_pontuacoes
(
    id SERIAL PRIMARY KEY,
    time_id INTEGER NOT NULL,
    rodada_id INTEGER NOT NULL,
    pontos NUMERIC(6,2) NOT NULL,

    created_at TIMESTAMP DEFAULT now(),

    CONSTRAINT uq_time_rodada UNIQUE (time_id, rodada_id),

    CONSTRAINT fk_tp_time
        FOREIGN KEY (time_id)
        REFERENCES public.duplas_times (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_tp_rodada
        FOREIGN KEY (rodada_id)
        REFERENCES public.rodadas_duplas (id)
        ON DELETE CASCADE
);
/*
duplas_cartoleiros   → pessoa
duplas_times         → times (entidades reais)
duplas               → competidor (ano)
duplas_times_ligacao → quais times formam a dupla
rodadas_duplas       → tempo
duplas_times_pontuacoes → DADO BRUTO (CSV)
*/

SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE '%duplas%';


/*
duplas_cartoleiros   → pessoa
duplas_times         → times (entidades reais)
duplas               → competidor (ano)
duplas_times_ligacao → quais times formam a dupla
rodadas_duplas       → tempo
duplas_times_pontuacoes → DADO BRUTO (CSV)
*/

SELECT
    d.ano,
    d.nome AS dupla,
    string_agg(
        c.nome || ' (' || t.nome || ')',
        '  +  '
        ORDER BY t.id
    ) AS composicao
FROM duplas d
JOIN duplas_times_ligacao l ON l.dupla_id = d.id
JOIN duplas_times t ON t.id = l.time_id
JOIN duplas_cartoleiros c ON c.id = t.cartoleiro_id
GROUP BY d.ano, d.nome
ORDER BY d.ano, d.nome;






select * from duplas_times_ligacao;


select * from duplas_times_pontuacoes;



select * from rodadas_duplas;

insert into duplas_times_ligacao (dupla_id,time_id)
values
(1,16),
(1,20),
(2,22),
(2,45),
(3,26),
(3,39),
(4,28),
(4,34),
(5,57),
(5,58),
(6,23),
(6,31),
(7,1),
(7,32),
(8,6),
(8,9),
(9,18),
(9,46),
(10,8),
(10,33),
(11,3),
(11,29),
(12,2),
(12,4),
(13,35),
(13,51),
(14,13),
(14,14),
(15,38),
(15,50),
(16,36),
(16,40),
(17,17),
(17,47),
(18,8),
(18,52),
(19,41),
(19,55),
(20,56),
(20,59),
(21,11),
(21,12),
(22,5),
(22,30),
(23,15),
(23,19),
(24,21),
(24,37),
(25,24),
(25,25),
(26,44),
(26,48),
(27,10),
(27,51),
(28,41),
(28,42),
(29,42),
(29,55),
(30,7),
(30,27),
(31,53),
(31,54),
(32,43),
(32,49);

insert into duplas (ano,nome) values

(2026,'O Nascimento do Dibre'),
(2026,'Mosby na Midola'),
(2026,'Machadada no Mengo'),
(2026,'Rattaria Máxima'),
(2026,'Geja o Gol'),
(2026,'Pano no Inferno'),
(2026,'Cala e Finja'),
(2026,'Burzandico'),
(2026,'Tranquilidade Zicada'),
(2026,'Globetrotters Frios e Calculistas'),
(2026,'AdShottta '),
(2026,'Garota de Marília'),
(2026,'Pelicano do Egito'),
(2026,'Porcos Parrudos'),
(2026,'Silas Mitagens'),
(2026,'Ocram Wanderes'),
(2026,'Sobrou o Dinizismo'),
(2026,'Chulé de Globetrotter'),
(2026,'Laranja Imensa'),
(2026,'A Bala do Allejo'),
(2026,'Tupis de Grajaú'),
(2026,'Almirobense'),
(2026,'Reclame Aqui no Boteco'),
(2026,'Restos de Sanlutty'),
(2026,'FeliSEP'),
(2026,'A Maleta de Dez Real'),
(2026,'Lovers'),
(2026,'O gordo e o tonto'),
(2026,'O véio e o vesgo'),
(2026,'Rato de Mala'),
(2026,'Marco Enferrujado'),
(2026,'Debi e Loide');

)

insert into duplas_times (cartoleiro_id,nome) values
(1,'CalazansTeam'),
(2,'Mariliense F.C'),
(3,'Adshow17 F.C'),
(4,'Ipanema13'),
(5,'Almi Jr. FC'),
(6,'Andico F.C'),
(7,'mala03fc'),
(8,'Brabo Globetrotters'),
(9,'Burza F C'),
(10,'Xuchélides'),
(11,'Grajaux City F.C.'),
(11,'Tupinianos FC'),
(12,'PALM£IRAS S.E.P.'),
(13,'ParrudoS Team'),
(14,'Olimpingas Sport Club'),
(15,'Didibre FC'),
(16,'Diniz Santastico1'),
(17,'Joga Tranquilo F.S.'),
(18,'Miss Procon Futebol Clube'),
(19,'nascimento124'),
(20,'FOI O QUE SOBROU'),
(21,'Mosby'),
(22,'Botafogo Hell'),
(23,'Tua mãe SEP'),
(24,'F.C Felicio F.C'),
(25,'Machadotti1972'),
(26,'08 Ratto FC'),
(26,'Real Rattaria FC'),
(27,'Sobottka FC 633'),
(28,'Gabirobense'),
(29,'Hpano FC'),
(30,'J.V.Finhani'),
(31,'A D Peaky Blinders'),
(32,'Massiminismo FC'),
(33,'Al Ahly Ecc'),
(34,'Luket Wanderes fc'),
(35,'Sanlutty FC'),
(36,'Mitinga`s F.C'),
(37,'Realmengo07 Fc'),
(38,'E.C. Ocram 5.6'),
(39,'SC Ornaghi Paulista'),
(40,'ZAGO PRATIS FC'),
(41,'TIMAO R.F.G'),
(42,'Maletinhas F.C.'),
(43,'Na Midola FC'),
(44,'SAY ZIKA'),
(44,'SÓRRESTO'),
(41,'Deizão Futebol Clube'),
(45,'Gigantes Morumbi F.C'),
(46,'Silasbrs FC'),
(47,'Pelicano Papada F.C'),
(47,'Schuletroll'),
(48,'Ferrugem Ultimate'),
(48,'Marco-FSA'),
(49,'Bike Cristo'),
(50,'Juquitas FC'),
(51,'GEJA'),
(51,'Wedgol'),
(52,'Allejo Team F.C');

insert into duplas_cartoleiros (nome) values 
('A CALAZANS'),
('A CARLOS'),
('ADSON'),
('ALE CHINELO'),
('ALMI'),
('ANDICO'),
('B DUCATI'),
('BRABO'),
('BURZA'),
('C TEIXEIRA'),
('D FERREIRA'),
('D LONGO'),
('D PARRUDO'),
('D QUIRINO'),
('D VALADARES'),
('DINIZ '),
('DREXX'),
('E GADELHA'),
('E NASCIMENTO'),
('EDIPO'),
('F ROSSI'),
('G BOTAFOGO'),
('G CASTRO'),
('G FELICIO'),
('G MACHADO'),
('G RATTO'),
('G SOBOTTKA'),
('GABI CADE'),
('H PANOBIANCO'),
('J FINHANI'),
('KAJURU'),
('L MASSIMINI'),
('LUCAT'),
('LUKET'),
('LUTTY'),
('M CANTALEGO'),
('M COIMBRA'),
('M OCRAM'),
('ORNAGHI'),
('PRATIS'),
('R CUNHA'),
('R MALETA'),
('R SHOJI'),
('R TRIPAO'),
('S GARCIA'),
('S SIQUEIRA'),
('SCHULETA'),
('T RIBAS'),
('VEIO DA LARANJA'),
('W SILVA'),
('WED'),
('Y ALLEJO');



CREATE TABLE duplas_fases (
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,

    nome VARCHAR(50) NOT NULL,
    ordem INTEGER NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ajuste', 'mata_mata')),

    qtd_confrontos INTEGER NOT NULL,
    rodada_resolucao INTEGER NOT NULL,

    ativa BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE premios (
    id SERIAL PRIMARY KEY,
    competicao VARCHAR(30) NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    ano INT NOT NULL,
    referencia INT NOT NULL,
    time_id INT NOT NULL,
    valor NUMERIC(10,2) NOT NULL,
    observacao TEXT,
    data_registro TIMESTAMP DEFAULT NOW()
);

UPDATE nome_da_tabela
SET coluna = 'novo_valor'
WHERE condicao;


insert into premios (competicao, tipo, ano, referencia, time_id,valor)
values
('Simples','Rodada',2026,'4º Rodada',72,100),
('Simples','Mensal(Janeiro\Fevereiro)',2026,'Mes 1 e 2',51,100),
('Simples','Mensal(Janeiro\Fevereiro)',2026,'Vice-Mes 1 e 2',15,50);
;

select * from premios;

update premios
set valor = 0
where id = 9;

insert into premios (competicao, tipo, ano, referencia, time_id,valor)
values
('Duplas','Rodada',2026,'4º Rodada',20,0),
('Duplas','Mensal(Janeiro\Fevereiro) ',2026,'Mes 1 e 2',3,70),
('Simples','Mensal',2026,'Mes 2',51,0),
('Duplas','Mensal',2026,'Mes 2',20,0)
;


acessar postgreSQL via terminal:

PS C:\> cd "C:\Program Files\PostgreSQL\18\bin"
PS C:\Program Files\PostgreSQL\18\bin> ./psql -U postgres
Senha para o usuário postgres:

psql (18.1)
ADVERTÊNCIA: A página de código da console (850) difere da página de código do Windows (1252)
             os caracteres de 8 bits podem não funcionar corretamente. Veja a página de
             referência do psql "Notes for Windows users" para obter detalhes.
Digite "help" para obter ajuda.

postgres=#

CREATE DATABASE postgres_teste;


isso dentro do PS C:\> cd "C:\Program Files\PostgreSQL\18\bin" 
.\pg_restore -h localhost -U postgres -d postgres_teste -v "C:\backups_postgres\cartola_fc\teste_1.backup"


select * from premios order by 1;

insert into premios (competicao, tipo, ano, referencia, time_id, valor)
values
('Simples','Rodada',2026,'5ºRodada',66,0);

update premios
set tipo = 'Rodada'
where id = 15;

select * from rodadas duplas