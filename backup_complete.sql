--
-- PostgreSQL database dump
--

\restrict KPU0PgJurQadzen6jVKFcUC1iWXX47t6yc3sXoRoZd35cRLSoTxbd7FdldEYsAs

-- Dumped from database version 15.16 (Debian 15.16-1.pgdg13+1)
-- Dumped by pg_dump version 15.16 (Debian 15.16-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: Categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Categories" (
    id uuid NOT NULL,
    restaurante_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion text,
    posicion integer NOT NULL,
    activa boolean NOT NULL,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now()
);


ALTER TABLE public."Categories" OWNER TO postgres;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id uuid NOT NULL,
    restaurante_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion text,
    posicion integer NOT NULL,
    activa boolean NOT NULL,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now()
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: dishes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dishes (
    id uuid NOT NULL,
    categoria_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    precio numeric(10,2) NOT NULL,
    precio_oferta numeric(10,2),
    imagen_url character varying,
    disponible boolean NOT NULL,
    destacado boolean NOT NULL,
    etiquetas character varying[],
    posicion integer,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now(),
    eliminado_en timestamp with time zone
);


ALTER TABLE public.dishes OWNER TO postgres;

--
-- Name: restaurants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.restaurants (
    id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    slug character varying(120) NOT NULL,
    descripcion text,
    logo character varying,
    telefono character varying,
    direccion character varying,
    horarios json,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now(),
    admin_id integer,
    qr_color_fg character varying(7) DEFAULT '#000000'::character varying NOT NULL,
    qr_color_bg character varying(7) DEFAULT '#FFFFFF'::character varying NOT NULL
);


ALTER TABLE public.restaurants OWNER TO postgres;

--
-- Name: menu_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_views (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    restaurant_id uuid NOT NULL,
    slug character varying(120) NOT NULL,
    source character varying(20) DEFAULT 'menu'::character varying NOT NULL,
    user_agent character varying(512),
    ip_address character varying(45),
    viewed_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.menu_views OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    nombre_completo character varying NOT NULL,
    usuario character varying NOT NULL,
    password character varying NOT NULL,
    rol character varying NOT NULL,
    activo boolean,
    email character varying(100)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: Categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Categories" (id, restaurante_id, nombre, descripcion, posicion, activa, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, restaurante_id, nombre, descripcion, posicion, activa, creado_en, actualizado_en) FROM stdin;
5a0ba68c-de3e-479c-807e-ea8bee8582a7	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	sopas	Sopas de la casa	1	t	2026-02-13 12:00:55.854715+00	2026-02-13 20:58:10.170501+00
f0369b3a-209e-4b59-81cf-d497b9921d35	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	categoira 1	otra preuba	33	t	2026-02-13 11:57:39.367014+00	2026-02-17 00:42:49.613792+00
f4e424f8-e3a6-4046-9f0e-dda94fb64380	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	preuba 12345	otra preuba	2	t	2026-02-13 00:38:25.864594+00	2026-02-17 00:44:11.501741+00
\.


--
-- Data for Name: dishes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dishes (id, categoria_id, nombre, descripcion, precio, precio_oferta, imagen_url, disponible, destacado, etiquetas, posicion, creado_en, actualizado_en, eliminado_en) FROM stdin;
0b41fc03-3689-49aa-ba8b-63d5b0497774	f4e424f8-e3a6-4046-9f0e-dda94fb64380	fsdf	3	3.00	3.00	\N	t	f	{no}	3	2026-02-13 19:23:46.473362+00	2026-02-13 19:23:46.473362+00	\N
9eeed5f5-aac0-4f90-ab6a-604537f2c9ef	f4e424f8-e3a6-4046-9f0e-dda94fb64380	fsdf	d	3.00	\N	\N	t	f	{no}	5	2026-02-13 20:08:57.146766+00	2026-02-13 20:53:54.632267+00	\N
87cb8c8f-32bf-4012-a5de-fefdf0848d1e	f4e424f8-e3a6-4046-9f0e-dda94fb64380	fsdf	3	3.00	3.00	\N	t	f	{no}	4	2026-02-13 19:49:19.118656+00	2026-02-13 20:54:07.707323+00	\N
48b05fc0-faf4-49a4-be31-6a8f42c8cf50	f4e424f8-e3a6-4046-9f0e-dda94fb64380	lentejas	plato fuerte	2.00	2.00	\N	t	f	{no}	2	2026-02-13 19:22:41.754277+00	2026-02-13 20:54:56.06418+00	\N
0dfbc9ba-95bc-40b9-8bbb-8766a64a84c6	5a0ba68c-de3e-479c-807e-ea8bee8582a7	ajiaco	sopa bogotana	12500.00	12500.00	\N	t	f	{"Ajiaco santafereño"}	1	2026-02-13 19:22:40.322016+00	2026-02-13 20:55:38.756714+00	\N
\.


--
-- Data for Name: menu_views; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_views (id, restaurant_id, slug, source, user_agent, ip_address, viewed_at) FROM stdin;
a0000001-0001-4000-8000-000000000001	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.10	2026-01-30 10:23:15+00
a0000001-0001-4000-8000-000000000002	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.55	2026-01-30 14:45:30+00
a0000001-0001-4000-8000-000000000003	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.22	2026-01-31 09:12:00+00
a0000001-0001-4000-8000-000000000004	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.101	2026-02-01 11:05:22+00
a0000001-0001-4000-8000-000000000005	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.44	2026-02-01 12:30:10+00
a0000001-0001-4000-8000-000000000006	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.78	2026-02-01 19:15:45+00
a0000001-0001-4000-8000-000000000007	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.33	2026-02-02 08:22:33+00
a0000001-0001-4000-8000-000000000008	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.55	2026-02-02 13:10:20+00
a0000001-0001-4000-8000-000000000009	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.200	2026-02-03 10:45:12+00
a0000001-0001-4000-8000-000000000010	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.11	2026-02-04 09:33:00+00
a0000001-0001-4000-8000-000000000011	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.42	2026-02-04 15:20:45+00
a0000001-0001-4000-8000-000000000012	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.88	2026-02-05 11:50:30+00
a0000001-0001-4000-8000-000000000013	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.44	2026-02-06 08:15:00+00
a0000001-0001-4000-8000-000000000014	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.130	2026-02-06 12:40:22+00
a0000001-0001-4000-8000-000000000015	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.77	2026-02-06 18:05:10+00
a0000001-0001-4000-8000-000000000016	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.15	2026-02-07 09:30:00+00
a0000001-0001-4000-8000-000000000017	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.55	2026-02-07 14:22:33+00
a0000001-0001-4000-8000-000000000018	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.23	2026-02-08 10:10:15+00
a0000001-0001-4000-8000-000000000019	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.99	2026-02-08 13:55:40+00
a0000001-0001-4000-8000-000000000020	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.33	2026-02-08 17:30:00+00
a0000001-0001-4000-8000-000000000021	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.66	2026-02-08 20:45:10+00
a0000001-0001-4000-8000-000000000022	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.91	2026-02-09 09:00:00+00
a0000001-0001-4000-8000-000000000023	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.177	2026-02-09 12:15:30+00
a0000001-0001-4000-8000-000000000024	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.61	2026-02-09 16:40:22+00
a0000001-0001-4000-8000-000000000025	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.77	2026-02-10 08:05:00+00
a0000001-0001-4000-8000-000000000026	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.12	2026-02-10 11:30:15+00
a0000001-0001-4000-8000-000000000027	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.88	2026-02-11 09:45:00+00
a0000001-0001-4000-8000-000000000028	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.144	2026-02-12 10:20:33+00
a0000001-0001-4000-8000-000000000029	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.88	2026-02-12 14:55:10+00
a0000001-0001-4000-8000-000000000030	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.33	2026-02-13 09:10:00+00
a0000001-0001-4000-8000-000000000031	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.55	2026-02-13 12:30:45+00
a0000001-0001-4000-8000-000000000032	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.22	2026-02-14 08:45:00+00
a0000001-0001-4000-8000-000000000033	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.99	2026-02-14 13:20:15+00
a0000001-0001-4000-8000-000000000034	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.66	2026-02-14 17:55:30+00
a0000001-0001-4000-8000-000000000035	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.170	2026-02-15 09:30:00+00
a0000001-0001-4000-8000-000000000036	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.91	2026-02-15 12:10:22+00
a0000001-0001-4000-8000-000000000037	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.11	2026-02-15 16:45:10+00
a0000001-0001-4000-8000-000000000038	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.42	2026-02-15 19:20:00+00
a0000001-0001-4000-8000-000000000039	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.66	2026-02-16 08:00:00+00
a0000001-0001-4000-8000-000000000040	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.180	2026-02-16 11:35:45+00
a0000001-0001-4000-8000-000000000041	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.22	2026-02-16 15:10:30+00
a0000001-0001-4000-8000-000000000042	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.99	2026-02-16 18:55:00+00
a0000001-0001-4000-8000-000000000043	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.33	2026-02-17 09:15:00+00
a0000001-0001-4000-8000-000000000044	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.77	2026-02-17 13:40:22+00
a0000001-0001-4000-8000-000000000045	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.33	2026-02-18 08:30:00+00
a0000001-0001-4000-8000-000000000046	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.15	2026-02-18 12:05:10+00
a0000001-0001-4000-8000-000000000047	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.122	2026-02-19 10:50:30+00
a0000001-0001-4000-8000-000000000048	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.200	2026-02-19 15:25:00+00
a0000001-0001-4000-8000-000000000049	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.44	2026-02-20 09:00:00+00
a0000001-0001-4000-8000-000000000050	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.55	2026-02-20 11:45:15+00
a0000001-0001-4000-8000-000000000051	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.44	2026-02-20 16:30:22+00
a0000001-0001-4000-8000-000000000052	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.155	2026-02-21 08:20:00+00
a0000001-0001-4000-8000-000000000053	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.55	2026-02-21 12:55:30+00
a0000001-0001-4000-8000-000000000054	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.77	2026-02-21 17:10:45+00
a0000001-0001-4000-8000-000000000055	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.88	2026-02-22 09:30:00+00
a0000001-0001-4000-8000-000000000056	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.33	2026-02-22 13:15:10+00
a0000001-0001-4000-8000-000000000057	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.66	2026-02-22 17:40:00+00
a0000001-0001-4000-8000-000000000058	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.22	2026-02-22 20:05:30+00
a0000001-0001-4000-8000-000000000059	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.177	2026-02-23 08:10:00+00
a0000001-0001-4000-8000-000000000060	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.66	2026-02-23 12:35:15+00
a0000001-0001-4000-8000-000000000061	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.77	2026-02-23 16:50:22+00
a0000001-0001-4000-8000-000000000062	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.44	2026-02-23 19:25:00+00
a0000001-0001-4000-8000-000000000063	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.111	2026-02-24 09:00:00+00
a0000001-0001-4000-8000-000000000064	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.44	2026-02-24 11:40:30+00
a0000001-0001-4000-8000-000000000065	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.88	2026-02-24 15:15:45+00
a0000001-0001-4000-8000-000000000066	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.88	2026-02-24 18:30:00+00
a0000001-0001-4000-8000-000000000067	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.155	2026-02-25 08:45:00+00
a0000001-0001-4000-8000-000000000068	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.88	2026-02-25 12:20:15+00
a0000001-0001-4000-8000-000000000069	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.99	2026-02-25 16:55:30+00
a0000001-0001-4000-8000-000000000070	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.33	2026-02-25 20:10:00+00
a0000001-0001-4000-8000-000000000071	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.200	2026-02-26 08:30:00+00
a0000001-0001-4000-8000-000000000072	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.122	2026-02-26 11:05:22+00
a0000001-0001-4000-8000-000000000073	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.11	2026-02-26 14:40:10+00
a0000001-0001-4000-8000-000000000074	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.66	2026-02-26 18:15:45+00
a0000001-0001-4000-8000-000000000075	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.77	2026-02-26 21:30:00+00
a0000001-0001-4000-8000-000000000076	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.166	2026-02-27 08:00:00+00
a0000001-0001-4000-8000-000000000077	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.33	2026-02-27 11:35:15+00
a0000001-0001-4000-8000-000000000078	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.11	2026-02-27 15:10:30+00
a0000001-0001-4000-8000-000000000079	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.144	2026-02-27 18:45:00+00
a0000001-0001-4000-8000-000000000080	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.55	2026-02-27 21:20:22+00
a0000001-0001-4000-8000-000000000081	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.44	2026-02-28 08:15:00+00
a0000001-0001-4000-8000-000000000082	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.55	2026-02-28 11:50:10+00
a0000001-0001-4000-8000-000000000083	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.33	2026-02-28 15:25:30+00
a0000001-0001-4000-8000-000000000084	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.99	2026-02-28 18:00:00+00
a0000001-0001-4000-8000-000000000085	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.55	2026-02-28 20:35:45+00
a0000001-0001-4000-8000-000000000086	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.77	2026-03-01 08:00:00+00
a0000001-0001-4000-8000-000000000087	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.166	2026-03-01 09:30:15+00
a0000001-0001-4000-8000-000000000088	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.111	2026-03-01 11:15:30+00
a0000001-0001-4000-8000-000000000089	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	172.16.0.66	2026-03-01 13:40:00+00
a0000001-0001-4000-8000-000000000090	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	192.168.1.99	2026-03-01 15:05:22+00
a0000001-0001-4000-8000-000000000091	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	10.0.0.22	2026-03-01 16:30:00+00
a0000001-0001-4000-8000-000000000092	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	10.0.0.188	2026-03-01 17:45:10+00
\.


--
-- Data for Name: restaurants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.restaurants (id, nombre, slug, descripcion, logo, telefono, direccion, horarios, creado_en, actualizado_en, admin_id, qr_color_fg, qr_color_bg) FROM stdin;
9dc24e18-08f9-42d4-83fc-bb4e40c4c968	Proyecto materia	proyecto-materia	Trabajo de materia	https://images.pexels.com/photos/2619967/pexels-photo-2619967.jpeg	3125698574	cra 1 en el centro	{"raw": "{\\n\\"lunes\\":  \\"9 a.m. a 8 p.m.\\"\\n\\"martes\\": \\"10 a.m. a 10 p.m.\\"\\n\\"domingo\\": \\"11 a.m a 10 p.m.\\"\\n}"}	2026-02-12 21:57:51.920692+00	2026-02-17 00:34:51.892407+00	1	#000000	#FFFFFF
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, nombre_completo, usuario, password, rol, activo, email) FROM stdin;
1	Juan Pérez	admin	$2b$12$1RSsFoppH0X4L3HL8iS4tOSXEM78C5PQ/6677yaJDnnMVyZlgrdD6	admin	t	f.ramirez@uniandes.edu.co
2	María García	maria.garcia	$2b$12$SzKzalNx0gHsS.r77EOgv.LVGE78Qr2qUsvDRzMCS4FDtX7MGcgre	cliente	t	maria.garcia@mail.com
3	Carlos López	carlos.lopez	$2b$12$SzKzalNx0gHsS.r77EOgv.LVGE78Qr2qUsvDRzMCS4FDtX7MGcgre	cliente	t	carlos.lopez@mail.com
4	Ana Rodríguez	ana.rodriguez	$2b$12$SzKzalNx0gHsS.r77EOgv.LVGE78Qr2qUsvDRzMCS4FDtX7MGcgre	cliente	t	ana.rodriguez@mail.com
5	Pedro Martínez	pedro.martinez	$2b$12$SzKzalNx0gHsS.r77EOgv.LVGE78Qr2qUsvDRzMCS4FDtX7MGcgre	cliente	t	pedro.martinez@mail.com
6	Laura Sánchez	laura.sanchez	$2b$12$SzKzalNx0gHsS.r77EOgv.LVGE78Qr2qUsvDRzMCS4FDtX7MGcgre	cliente	t	laura.sanchez@mail.com
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: Categories Categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Categories"
    ADD CONSTRAINT "Categories_pkey" PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: dishes dishes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT dishes_pkey PRIMARY KEY (id);


--
-- Name: restaurants restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (id);


--
-- Name: restaurants restaurants_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_slug_key UNIQUE (slug);


--
-- Name: menu_views menu_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_views
    ADD CONSTRAINT menu_views_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_usuario ON public.users USING btree (usuario);


--
-- Name: ix_menu_views_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_views_slug ON public.menu_views USING btree (slug);


--
-- Name: ix_menu_views_viewed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_views_viewed_at ON public.menu_views USING btree (viewed_at);


--
-- Name: dishes dishes_categoria_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT dishes_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES public.categories(id);


--
-- Name: restaurants restaurants_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id);


--
-- Name: menu_views menu_views_restaurant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_views
    ADD CONSTRAINT menu_views_restaurant_id_fkey FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict KPU0PgJurQadzen6jVKFcUC1iWXX47t6yc3sXoRoZd35cRLSoTxbd7FdldEYsAs

