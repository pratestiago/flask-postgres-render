--
-- PostgreSQL database dump
--

\restrict 2cPM2Zg66ZnbK1aPx2xZrSNf801bQ9v5yxMSPhCouX2gHfpv8WihlDvXmpKiF5W

-- Dumped from database version 17.7 (bdc8956)
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cartoleiros; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.cartoleiros (
    id integer NOT NULL,
    nome character varying(100) NOT NULL
);


ALTER TABLE public.cartoleiros OWNER TO neondb_owner;

--
-- Name: cartoleiros_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.cartoleiros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cartoleiros_id_seq OWNER TO neondb_owner;

--
-- Name: cartoleiros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.cartoleiros_id_seq OWNED BY public.cartoleiros.id;


--
-- Name: placar; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.placar (
    id integer NOT NULL,
    jogador character varying(100),
    "time" character varying(100),
    pontos integer
);


ALTER TABLE public.placar OWNER TO neondb_owner;

--
-- Name: placar_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.placar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.placar_id_seq OWNER TO neondb_owner;

--
-- Name: placar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.placar_id_seq OWNED BY public.placar.id;


--
-- Name: resultado_rodada; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.resultado_rodada (
    id integer NOT NULL,
    rodada_id integer NOT NULL,
    time_id integer NOT NULL,
    pontos numeric(6,2) NOT NULL,
    patrimonio numeric(10,2)
);


ALTER TABLE public.resultado_rodada OWNER TO neondb_owner;

--
-- Name: resultado_rodada_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.resultado_rodada_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resultado_rodada_id_seq OWNER TO neondb_owner;

--
-- Name: resultado_rodada_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.resultado_rodada_id_seq OWNED BY public.resultado_rodada.id;


--
-- Name: rodadas; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.rodadas (
    id integer NOT NULL,
    liga_id integer NOT NULL,
    temporada integer NOT NULL,
    numero integer NOT NULL
);


ALTER TABLE public.rodadas OWNER TO neondb_owner;

--
-- Name: rodadas_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.rodadas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rodadas_id_seq OWNER TO neondb_owner;

--
-- Name: rodadas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.rodadas_id_seq OWNED BY public.rodadas.id;


--
-- Name: times; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.times (
    id integer NOT NULL,
    cartoleiro_id integer NOT NULL,
    nome_time character varying(150) NOT NULL,
    temporada integer NOT NULL,
    cartola_time_id bigint,
    cartola_slug character varying(100),
    ativo boolean DEFAULT true
);


ALTER TABLE public.times OWNER TO neondb_owner;

--
-- Name: times_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.times_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.times_id_seq OWNER TO neondb_owner;

--
-- Name: times_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.times_id_seq OWNED BY public.times.id;


--
-- Name: cartoleiros id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.cartoleiros ALTER COLUMN id SET DEFAULT nextval('public.cartoleiros_id_seq'::regclass);


--
-- Name: placar id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.placar ALTER COLUMN id SET DEFAULT nextval('public.placar_id_seq'::regclass);


--
-- Name: resultado_rodada id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.resultado_rodada ALTER COLUMN id SET DEFAULT nextval('public.resultado_rodada_id_seq'::regclass);


--
-- Name: rodadas id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.rodadas ALTER COLUMN id SET DEFAULT nextval('public.rodadas_id_seq'::regclass);


--
-- Name: times id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.times ALTER COLUMN id SET DEFAULT nextval('public.times_id_seq'::regclass);


--
-- Data for Name: cartoleiros; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.cartoleiros (id, nome) FROM stdin;
1	ADRIANO CUNHA EL LOUCO
2	ADRIANO ZIZU
3	ADSON MENDES
4	ALEX TENIS MOURA
5	ALEXANDRE IPANEMA
6	ALLAN JAMES
7	ALLAN SANTOS
8	ALLEN
9	ALMI JUNIOR
10	ALMIR RIMLAFC
11	ALYSON CALAZANS
12	ANDERSON PORKO
13	ANDRE FONTANA
14	ANDRE ORELHA
15	ANDRE PRATS
16	ANDRÉ TREVIZANI
17	AURO JR
18	CAIO BENJA
19	CARLOS ANDRÉ
20	CARLOS BARBOSA NENEN
21	CARLOS CAJURU
22	CHELIDE
23	CLAUDIO PELUSO
24	DANIEL QUIRINO
25	DIEGO PALMEIRESEN
26	DINIZ SANTASTICO
27	DIOGO CALVIN
28	DOUGLAS FERREIRA
29	DUCATI MALA
30	EDIPO MACEDO
31	EDUARDO BRABO
32	EDUARDO DORNEL RIBAS
33	EDUARDO ORNAGHI
34	EDUARDO TUROLLA
35	EMERSON PORCOLINO
36	EVANIL
37	FELIPE HENRIQUE
38	FELIPE MOSBY
39	GABRIEL LAGOS
40	GABRIEL RATTO
41	GABRIEL VUDU
42	GREG QUIRINI
43	GUSTAVO NERY
44	HENRIQUE VUDU
45	JEFFERSON FINHANI TI
46	JEFFERSON LALOR
47	JONATHAN BATATA
48	LEANDRO CANHISARES PARDAL
49	LEANDRO SCHULAI
50	LISSAO
51	LUCAS MASSIMINI
52	LUCAT
53	LUTTY
54	MARCÃO LUCAT
55	MARCEL CANTALEGO
56	MARCIO GAI
57	MARCOS COLLADO
58	MAURÍCIO VÉIO DA LARANJA
59	MICHAEL REIS
60	OTAVIO DAMASCENO
61	PAULO OTO
62	RICARDO FILGUEIRAS
63	RICARDO MALETA
64	RICARDO SHOJI
65	RICARDO TRIPAO
66	RICHARD MENEGUETI
67	ROBSON CUNHA
68	ROGÉRIO LAGOS
69	SERGIO GARCIA
70	SILINHAS
71	THIAGO RIBAS
72	VERON
73	VUDU
74	WEDSON
75	WELLIGTON ABOBORA
76	WESLEY YORKS
77	YURI ALLEJO
\.


--
-- Data for Name: placar; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.placar (id, jogador, "time", pontos) FROM stdin;
1	João	Azul	10
2	Maria	Verde	15
3	Carlos	Vermelho	8
4	Ana	Azul	20
5	Pedro	Verde	12
6	Schulai	Rosa	24
7	Pratis	Verde	15
8	Camila	Branco	50
\.


--
-- Data for Name: resultado_rodada; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.resultado_rodada (id, rodada_id, time_id, pontos, patrimonio) FROM stdin;
\.


--
-- Data for Name: rodadas; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.rodadas (id, liga_id, temporada, numero) FROM stdin;
1	1	2025	1
2	1	2025	2
3	1	2025	3
4	1	2025	4
5	1	2025	5
6	1	2025	6
7	1	2025	7
8	1	2025	8
9	1	2025	9
10	1	2025	10
11	1	2025	11
12	1	2025	12
13	1	2025	13
14	1	2025	14
15	1	2025	15
16	1	2025	16
17	1	2025	17
18	1	2025	18
19	1	2025	19
20	1	2025	20
21	1	2025	21
22	1	2025	22
23	1	2025	23
24	1	2025	24
25	1	2025	25
26	1	2025	26
27	1	2025	27
28	1	2025	28
29	1	2025	29
30	1	2025	30
31	1	2025	31
32	1	2025	32
33	1	2025	33
34	1	2025	34
35	1	2025	35
36	1	2025	36
37	1	2025	37
38	1	2025	38
\.


--
-- Data for Name: times; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.times (id, cartoleiro_id, nome_time, temporada, cartola_time_id, cartola_slug, ativo) FROM stdin;
1	1	Caixão do Papaco	2025	\N	\N	t
2	2	Adriano ZIZU	2025	\N	\N	t
3	3	Adshow17 F.C	2025	\N	\N	t
4	4	SOROCITYSOCCER	2025	\N	\N	t
5	5	Ipanema13	2025	\N	\N	t
6	6	Centenario Alviverde	2025	\N	\N	t
7	7	#Santos.Z/O	2025	\N	\N	t
8	8	Zona Leste Paulista	2025	\N	\N	t
9	9	Almi Jr. FC	2025	\N	\N	t
10	10	RIMLAFC	2025	\N	\N	t
11	11	CalazansTeam	2025	\N	\N	t
12	12	Os Porko é Loko - Z/O	2025	\N	\N	t
13	13	A.C. Fontana	2025	\N	\N	t
14	14	Joga Tranquilo F.S.	2025	\N	\N	t
15	15	REAL SARANDI CLUBE	2025	\N	\N	t
16	16	Andrétero FC	2025	\N	\N	t
17	17	SFC Diamond Dogs	2025	\N	\N	t
18	18	Xungas FC	2025	\N	\N	t
19	19	Gabirobense	2025	\N	\N	t
20	20	Nenenzico FC	2025	\N	\N	t
21	21	A D Peaky Blinders	2025	\N	\N	t
22	22	Xuchélides	2025	\N	\N	t
23	23	CRPELUSO	2025	\N	\N	t
24	24	Olimpingas Sport Club	2025	\N	\N	t
25	25	Paleztras Club	2025	\N	\N	t
26	26	Diniz Santastico1	2025	\N	\N	t
27	27	Diogo Alviverde Imponente	2025	\N	\N	t
28	27	Diogo Palestrudo	2025	\N	\N	t
29	28	Grajaux City F.C.	2025	\N	\N	t
30	29	Mala03Fc	2025	\N	\N	t
31	30	FOI O QUE SOBROU	2025	\N	\N	t
32	31	Brabo Globetrotters	2025	\N	\N	t
33	32	Dornel Cruel	2025	\N	\N	t
34	33	SC Ornaghi Paulista	2025	\N	\N	t
35	34	DuTurolla	2025	\N	\N	t
36	35	EmesuShow Porcolino	2025	\N	\N	t
37	36	Evans Jr FC	2025	\N	\N	t
38	37	FC Felipe Henrique	2025	\N	\N	t
39	38	Mosby	2025	\N	\N	t
40	39	Bilao Sport Club	2025	\N	\N	t
41	39	Bilao Sport FC	2025	\N	\N	t
42	40	08 Ratto FC	2025	\N	\N	t
43	40	Real Rattaria FC	2025	\N	\N	t
44	41	Botafogo Hell	2025	\N	\N	t
45	42	APELÕES FUTEBOL CLUB	2025	\N	\N	t
46	43	Sobottka FC 633	2025	\N	\N	t
47	44	HPano FC	2025	\N	\N	t
48	45	J.V.Finhani	2025	\N	\N	t
49	46	CR Pelég	2025	\N	\N	t
50	47	Sempre ForteF.C.	2025	\N	\N	t
51	48	P@rdall FC	2025	\N	\N	t
52	49	Schuletroll	2025	\N	\N	t
53	49	Pelicano Papada F.C	2025	\N	\N	t
54	50	LissaoCruzmaltino FC	2025	\N	\N	t
55	51	Massiminismo FC	2025	\N	\N	t
56	52	Luket Wanderes fc	2025	\N	\N	t
57	53	Sanlutty FC	2025	\N	\N	t
58	54	E.C. Ocram 5.5	2025	\N	\N	t
59	55	Mitinga`s F.C	2025	\N	\N	t
60	56	Metamoney F.C	2025	\N	\N	t
61	57	Collados FC	2025	\N	\N	t
62	58	Bike Cristo	2025	\N	\N	t
63	59	Kings Futebol Club	2025	\N	\N	t
64	60	Timao do Otao	2025	\N	\N	t
65	61	OtoPat@ma	2025	\N	\N	t
66	62	Amigos do Loco Abreu	2025	\N	\N	t
67	63	Maletinhas F.C.	2025	\N	\N	t
68	64	Na Midola FC	2025	\N	\N	t
69	65	ZEKABOLEIRO	2025	\N	\N	t
70	66	RMENEGHETTI	2025	\N	\N	t
71	67	RCUNHA S.C.C.P	2025	\N	\N	t
72	68	Borussia da Pompeia	2025	\N	\N	t
73	69	GIGANTES MORUMBI F.C	2025	\N	\N	t
74	70	Silasbrs FC	2025	\N	\N	t
75	71	Ferrugem Ultimate	2025	\N	\N	t
76	72	FUCKER AND SUCKER FC	2025	\N	\N	t
77	73	Vuduzera	2025	\N	\N	t
78	74	GEJA	2025	\N	\N	t
79	75	Abóbora Futebol C	2025	\N	\N	t
80	76	Yorks Gamora & Goku FC	2025	\N	\N	t
81	77	Allejo Team F.C	2025	\N	\N	t
\.


--
-- Name: cartoleiros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.cartoleiros_id_seq', 77, true);


--
-- Name: placar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.placar_id_seq', 8, true);


--
-- Name: resultado_rodada_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.resultado_rodada_id_seq', 81, true);


--
-- Name: rodadas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.rodadas_id_seq', 38, true);


--
-- Name: times_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.times_id_seq', 81, true);


--
-- Name: cartoleiros cartoleiros_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.cartoleiros
    ADD CONSTRAINT cartoleiros_pkey PRIMARY KEY (id);


--
-- Name: placar placar_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.placar
    ADD CONSTRAINT placar_pkey PRIMARY KEY (id);


--
-- Name: resultado_rodada resultado_rodada_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.resultado_rodada
    ADD CONSTRAINT resultado_rodada_pkey PRIMARY KEY (id);


--
-- Name: rodadas rodadas_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.rodadas
    ADD CONSTRAINT rodadas_pkey PRIMARY KEY (id);


--
-- Name: times times_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.times
    ADD CONSTRAINT times_pkey PRIMARY KEY (id);


--
-- Name: times fk_cartoleiro; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.times
    ADD CONSTRAINT fk_cartoleiro FOREIGN KEY (cartoleiro_id) REFERENCES public.cartoleiros(id);


--
-- Name: resultado_rodada fk_resultado_rodada_rodada; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.resultado_rodada
    ADD CONSTRAINT fk_resultado_rodada_rodada FOREIGN KEY (rodada_id) REFERENCES public.rodadas(id);


--
-- Name: resultado_rodada fk_resultado_rodada_time; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.resultado_rodada
    ADD CONSTRAINT fk_resultado_rodada_time FOREIGN KEY (time_id) REFERENCES public.times(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

\unrestrict 2cPM2Zg66ZnbK1aPx2xZrSNf801bQ9v5yxMSPhCouX2gHfpv8WihlDvXmpKiF5W

