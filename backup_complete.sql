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
    ip_hash character varying(64),
    referrer character varying(512),
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

COPY public.menu_views (id, restaurant_id, slug, source, user_agent, ip_hash, referrer, viewed_at) FROM stdin;
a0000001-0001-4000-8000-000000000001	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	805ebf201c523f69376591c6ce5ceb3f12ebcfedad297c5f175a380426cf0b42	https://www.google.com/	2026-01-30 10:23:15+00
a0000001-0001-4000-8000-000000000002	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	d876fc90398ef69c2562b942438010676b7c22a40f59445dcdbd96255b993885	https://www.google.com/	2026-01-30 14:45:30+00
a0000001-0001-4000-8000-000000000003	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	61318e741586720d2d69943ba84afa8efef9d7e883d01068006486ff2a9311d7	https://www.facebook.com/	2026-01-31 09:12:00+00
a0000001-0001-4000-8000-000000000004	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	8696ced5e64331fd8faafbdf5f79f6e2b8bd6cd59e4697e091934b961276d2ed	https://www.instagram.com/	2026-02-01 11:05:22+00
a0000001-0001-4000-8000-000000000005	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	629e1bbe393416d676e9c8a1cc823029e9f25a8b5452ddb4701ab388d18d375f	https://www.instagram.com/	2026-02-01 12:30:10+00
a0000001-0001-4000-8000-000000000006	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	47b9bc8ad2261927d952e357cbe61230b8ba750dfbf74d5a9addf5b8c126663c	https://www.instagram.com/	2026-02-01 19:15:45+00
a0000001-0001-4000-8000-000000000007	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	adf186c852b151bade7a4cb2864e62c6aa85e5d9a7ea7cdde77fd46004f1670e	https://www.google.com/	2026-02-02 08:22:33+00
a0000001-0001-4000-8000-000000000008	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	de8838000814009fc32142e4121a9599df8aa9d69ffbb72f7b9ecbb677904e82	\N	2026-02-02 13:10:20+00
a0000001-0001-4000-8000-000000000009	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	b55245c77bb54b0f3ae775eda11a53b12ff9a62a4fe40e4648594175f60ee8ce	https://www.google.com/	2026-02-03 10:45:12+00
a0000001-0001-4000-8000-000000000010	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	81800b1955c8a59bffcba571e8000831612a91e4f92711e9d7a304884cb2d937	\N	2026-02-04 09:33:00+00
a0000001-0001-4000-8000-000000000011	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	1305dd3154b9eb8dfdea27a901e8b79d579c4359ae265922d0d91af6e4e89074	https://maps.google.com/	2026-02-04 15:20:45+00
a0000001-0001-4000-8000-000000000012	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	4c77a37c18c62b0d6ad2118a6cfeb15170302053fc29efad5081191a3b2a949a	https://www.google.com/	2026-02-05 11:50:30+00
a0000001-0001-4000-8000-000000000013	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	0742d4a92f6e9c3b431ac762229adb94997a30a772081658027f606b5b7f852e	https://www.google.com/	2026-02-06 08:15:00+00
a0000001-0001-4000-8000-000000000014	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	f0c9e6fa4ac3933118578f14010c13150c16a031f2f45dee20d361620df31287	https://www.google.com/	2026-02-06 12:40:22+00
a0000001-0001-4000-8000-000000000015	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	0fa74370b819cc049283e5391faef7e2377d7f8669b2b846fa646682356974b3	https://www.instagram.com/	2026-02-06 18:05:10+00
a0000001-0001-4000-8000-000000000016	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	a01e58af54341c4c7b6d042de4c8c9fbfafb3ae9dd7955c4aeb26ca8c823b495	https://www.instagram.com/	2026-02-07 09:30:00+00
a0000001-0001-4000-8000-000000000017	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	a0ce6978086cff8aa90b1c7a3cd27c5d1e8976791f39e73e4ef845b09e3669e5	\N	2026-02-07 14:22:33+00
a0000001-0001-4000-8000-000000000018	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	cc6b08f9e38f604b3b318293a83ebb79d6cfa7bf184d46ff6ce45d627f2d73e2	\N	2026-02-08 10:10:15+00
a0000001-0001-4000-8000-000000000019	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	851b82ef28b8ee071273ccfdb2ad3927e9cec5b02ae201485e5ccd1ed169c663	https://www.google.com/	2026-02-08 13:55:40+00
a0000001-0001-4000-8000-000000000020	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	ea8a70783586ed0228cfdf8c4648875b5cc0297c6acb5f7aa4bc36e3a5acbeef	\N	2026-02-08 17:30:00+00
a0000001-0001-4000-8000-000000000021	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	d780fb50bdb39c67d3605ed545e14742ac75ffca2ab9ceea6f9276fa21f835b6	https://www.instagram.com/	2026-02-08 20:45:10+00
a0000001-0001-4000-8000-000000000022	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	6f1fe95f524020f8214a3db9411afd9c7912b98f65751aef05bbfb02e92cfb56	\N	2026-02-09 09:00:00+00
a0000001-0001-4000-8000-000000000023	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	4824937ff86230ac6ba6aff474be33af4317ef71444a5e5a6868c6b7eca4ba61	https://maps.google.com/	2026-02-09 12:15:30+00
a0000001-0001-4000-8000-000000000024	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	61661e39199c2e90a61bd3ca1ea0d9f02adc29b40618023a6b7cb442d7927d24	https://www.instagram.com/	2026-02-09 16:40:22+00
a0000001-0001-4000-8000-000000000025	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	73a9a302758764680d6172e631255a39096c634757256eec02286306741db299	https://maps.google.com/	2026-02-10 08:05:00+00
a0000001-0001-4000-8000-000000000026	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	734d6b3fb4778119bbf7010d94157466f40f860a003f057574e1d066d58b6c3d	\N	2026-02-10 11:30:15+00
a0000001-0001-4000-8000-000000000027	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	0a082eb464e6742009152e751fdb9436da2c6fa6c53112444db6f1717119893c	https://www.facebook.com/	2026-02-11 09:45:00+00
a0000001-0001-4000-8000-000000000028	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	e7e11206efb990b9614350cfadc95781c20b7c235bf41edc058a1545535483eb	https://www.google.com/	2026-02-12 10:20:33+00
a0000001-0001-4000-8000-000000000029	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	5fa2b4bf5fbb0fa0c6a6c3708573c9476ac98825b97b7dee4222255d418de536	https://www.instagram.com/	2026-02-12 14:55:10+00
a0000001-0001-4000-8000-000000000030	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	aa66341ec6fddde35c237b1bf5c0a2f007e5892b4a9dd11a3619f3da58bb27d7	https://maps.google.com/	2026-02-13 09:10:00+00
a0000001-0001-4000-8000-000000000031	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	d876fc90398ef69c2562b942438010676b7c22a40f59445dcdbd96255b993885	https://www.facebook.com/	2026-02-13 12:30:45+00
a0000001-0001-4000-8000-000000000032	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	063223c56986574dd274290a8eed5179aff82eef4c62ee989bdc95ebd5cdc5cf	https://www.facebook.com/	2026-02-14 08:45:00+00
a0000001-0001-4000-8000-000000000033	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	ede60db2cdb2f765f566e9790e6237d24479e2ea65c9fe6204312438a49e4507	https://www.instagram.com/	2026-02-14 13:20:15+00
a0000001-0001-4000-8000-000000000034	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	9b45101315171aeba9aee6186e015f23408d24851037e3f8c6fa8ede22bb3da7	https://www.instagram.com/	2026-02-14 17:55:30+00
a0000001-0001-4000-8000-000000000035	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	d4709c11e074e846b17a6110f84a19daaa6b22dacaab60f83457da50df4e6770	https://www.facebook.com/	2026-02-15 09:30:00+00
a0000001-0001-4000-8000-000000000036	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	78c76127428cb14b2153438b4733fbbf48eea2fbb8a8260e4a0b5b235db30553	https://www.google.com/	2026-02-15 12:10:22+00
a0000001-0001-4000-8000-000000000037	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	81800b1955c8a59bffcba571e8000831612a91e4f92711e9d7a304884cb2d937	https://www.google.com/	2026-02-15 16:45:10+00
a0000001-0001-4000-8000-000000000038	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	84b4812195edd00eade601ea1bcd88014093567b46b964d901a9ae31220ff9ca	https://maps.google.com/	2026-02-15 19:20:00+00
a0000001-0001-4000-8000-000000000039	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	f41081e1ce70dd2947712928109c741f2e07be5315c7140ccf3d9ed8ab3bf27d	https://www.google.com/	2026-02-16 08:00:00+00
a0000001-0001-4000-8000-000000000040	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	b08e30294c44fe6e25edcf5449320cbf16130c790af5b3027efa20c6cdb81c09	https://www.facebook.com/	2026-02-16 11:35:45+00
a0000001-0001-4000-8000-000000000041	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	61318e741586720d2d69943ba84afa8efef9d7e883d01068006486ff2a9311d7	https://www.facebook.com/	2026-02-16 15:10:30+00
a0000001-0001-4000-8000-000000000042	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	f2d05f872e42a2fbf9e84e3d616d258d4790660cd279511ec47deab5cce3d8c8	\N	2026-02-16 18:55:00+00
a0000001-0001-4000-8000-000000000043	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	ea8a70783586ed0228cfdf8c4648875b5cc0297c6acb5f7aa4bc36e3a5acbeef	https://www.facebook.com/	2026-02-17 09:15:00+00
a0000001-0001-4000-8000-000000000044	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	7600d018b75675318bf22e860bd8c7d4e9bc6588f7fa5ec2bc345eb5d746b302	https://www.google.com/	2026-02-17 13:40:22+00
a0000001-0001-4000-8000-000000000045	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	adf186c852b151bade7a4cb2864e62c6aa85e5d9a7ea7cdde77fd46004f1670e	https://maps.google.com/	2026-02-18 08:30:00+00
a0000001-0001-4000-8000-000000000046	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	c0096e7df394a6ba5e4d4dbae1ae1604b9ef342d7ac69e836e40c474a8ccd59e	\N	2026-02-18 12:05:10+00
a0000001-0001-4000-8000-000000000047	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	c946c59b4c132a61870581627542d062ab11cd3b7ad09ae4864870a4cec352a9	https://www.google.com/	2026-02-19 10:50:30+00
a0000001-0001-4000-8000-000000000048	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	b55245c77bb54b0f3ae775eda11a53b12ff9a62a4fe40e4648594175f60ee8ce	https://maps.google.com/	2026-02-19 15:25:00+00
a0000001-0001-4000-8000-000000000049	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	0742d4a92f6e9c3b431ac762229adb94997a30a772081658027f606b5b7f852e	https://www.google.com/	2026-02-20 09:00:00+00
a0000001-0001-4000-8000-000000000050	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	de8838000814009fc32142e4121a9599df8aa9d69ffbb72f7b9ecbb677904e82	\N	2026-02-20 11:45:15+00
a0000001-0001-4000-8000-000000000051	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	d5dd453c32cffb3d8237f44e92d5169183b6279a007fd98deb9073ff95709019	https://www.facebook.com/	2026-02-20 16:30:22+00
a0000001-0001-4000-8000-000000000052	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	266eb3321e6ed8ebca128ea560fa160f20e30a724a2b6d4a02799febae4345ea	\N	2026-02-21 08:20:00+00
a0000001-0001-4000-8000-000000000053	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	a0ce6978086cff8aa90b1c7a3cd27c5d1e8976791f39e73e4ef845b09e3669e5	https://www.facebook.com/	2026-02-21 12:55:30+00
a0000001-0001-4000-8000-000000000054	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	0fa74370b819cc049283e5391faef7e2377d7f8669b2b846fa646682356974b3	\N	2026-02-21 17:10:45+00
a0000001-0001-4000-8000-000000000055	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	0a082eb464e6742009152e751fdb9436da2c6fa6c53112444db6f1717119893c	https://www.instagram.com/	2026-02-22 09:30:00+00
a0000001-0001-4000-8000-000000000056	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	ea8a70783586ed0228cfdf8c4648875b5cc0297c6acb5f7aa4bc36e3a5acbeef	https://www.google.com/	2026-02-22 13:15:10+00
a0000001-0001-4000-8000-000000000057	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	d780fb50bdb39c67d3605ed545e14742ac75ffca2ab9ceea6f9276fa21f835b6	https://www.google.com/	2026-02-22 17:40:00+00
a0000001-0001-4000-8000-000000000058	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	3e96d8732051b54fef2ae0c914fb09658c3defa513f6bbd274e73ccd57f59fc4	https://www.instagram.com/	2026-02-22 20:05:30+00
a0000001-0001-4000-8000-000000000059	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	4824937ff86230ac6ba6aff474be33af4317ef71444a5e5a6868c6b7eca4ba61	https://www.facebook.com/	2026-02-23 08:10:00+00
a0000001-0001-4000-8000-000000000060	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	f41081e1ce70dd2947712928109c741f2e07be5315c7140ccf3d9ed8ab3bf27d	https://www.google.com/	2026-02-23 12:35:15+00
a0000001-0001-4000-8000-000000000061	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	73a9a302758764680d6172e631255a39096c634757256eec02286306741db299	https://www.instagram.com/	2026-02-23 16:50:22+00
a0000001-0001-4000-8000-000000000062	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	629e1bbe393416d676e9c8a1cc823029e9f25a8b5452ddb4701ab388d18d375f	https://www.google.com/	2026-02-23 19:25:00+00
a0000001-0001-4000-8000-000000000063	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	b1fd967aabbd678536671fdd90d20bbbf3e7044be7d15662e0e78814f072f0c3	https://maps.google.com/	2026-02-24 09:00:00+00
a0000001-0001-4000-8000-000000000064	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	d5dd453c32cffb3d8237f44e92d5169183b6279a007fd98deb9073ff95709019	https://www.facebook.com/	2026-02-24 11:40:30+00
a0000001-0001-4000-8000-000000000065	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	5fa2b4bf5fbb0fa0c6a6c3708573c9476ac98825b97b7dee4222255d418de536	https://maps.google.com/	2026-02-24 15:15:45+00
a0000001-0001-4000-8000-000000000066	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	4c77a37c18c62b0d6ad2118a6cfeb15170302053fc29efad5081191a3b2a949a	https://www.facebook.com/	2026-02-24 18:30:00+00
a0000001-0001-4000-8000-000000000067	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	266eb3321e6ed8ebca128ea560fa160f20e30a724a2b6d4a02799febae4345ea	https://www.instagram.com/	2026-02-25 08:45:00+00
a0000001-0001-4000-8000-000000000068	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	0a082eb464e6742009152e751fdb9436da2c6fa6c53112444db6f1717119893c	https://www.facebook.com/	2026-02-25 12:20:15+00
a0000001-0001-4000-8000-000000000069	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	ede60db2cdb2f765f566e9790e6237d24479e2ea65c9fe6204312438a49e4507	https://www.facebook.com/	2026-02-25 16:55:30+00
a0000001-0001-4000-8000-000000000070	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	aa66341ec6fddde35c237b1bf5c0a2f007e5892b4a9dd11a3619f3da58bb27d7	https://www.instagram.com/	2026-02-25 20:10:00+00
a0000001-0001-4000-8000-000000000071	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	b55245c77bb54b0f3ae775eda11a53b12ff9a62a4fe40e4648594175f60ee8ce	https://www.facebook.com/	2026-02-26 08:30:00+00
a0000001-0001-4000-8000-000000000072	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	c946c59b4c132a61870581627542d062ab11cd3b7ad09ae4864870a4cec352a9	https://www.google.com/	2026-02-26 11:05:22+00
a0000001-0001-4000-8000-000000000073	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	81800b1955c8a59bffcba571e8000831612a91e4f92711e9d7a304884cb2d937	\N	2026-02-26 14:40:10+00
a0000001-0001-4000-8000-000000000074	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	9b45101315171aeba9aee6186e015f23408d24851037e3f8c6fa8ede22bb3da7	https://www.instagram.com/	2026-02-26 18:15:45+00
a0000001-0001-4000-8000-000000000075	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	7600d018b75675318bf22e860bd8c7d4e9bc6588f7fa5ec2bc345eb5d746b302	\N	2026-02-26 21:30:00+00
a0000001-0001-4000-8000-000000000076	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	ef2dd60516e1c2a848cfb7348fdbfb604ec1a22cded9bf03587c3c78e784fa61	https://www.instagram.com/	2026-02-27 08:00:00+00
a0000001-0001-4000-8000-000000000077	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	adf186c852b151bade7a4cb2864e62c6aa85e5d9a7ea7cdde77fd46004f1670e	https://www.instagram.com/	2026-02-27 11:35:15+00
a0000001-0001-4000-8000-000000000078	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	ba753efa2015157bd094d405599223a50af144ea30c22ce5755f88d0aca95845	https://maps.google.com/	2026-02-27 15:10:30+00
a0000001-0001-4000-8000-000000000079	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	e7e11206efb990b9614350cfadc95781c20b7c235bf41edc058a1545535483eb	https://maps.google.com/	2026-02-27 18:45:00+00
a0000001-0001-4000-8000-000000000080	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	d876fc90398ef69c2562b942438010676b7c22a40f59445dcdbd96255b993885	https://www.facebook.com/	2026-02-27 21:20:22+00
a0000001-0001-4000-8000-000000000081	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	0742d4a92f6e9c3b431ac762229adb94997a30a772081658027f606b5b7f852e	\N	2026-02-28 08:15:00+00
a0000001-0001-4000-8000-000000000082	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	de8838000814009fc32142e4121a9599df8aa9d69ffbb72f7b9ecbb677904e82	https://www.instagram.com/	2026-02-28 11:50:10+00
a0000001-0001-4000-8000-000000000083	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	ea8a70783586ed0228cfdf8c4648875b5cc0297c6acb5f7aa4bc36e3a5acbeef	https://www.facebook.com/	2026-02-28 15:25:30+00
a0000001-0001-4000-8000-000000000084	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	851b82ef28b8ee071273ccfdb2ad3927e9cec5b02ae201485e5ccd1ed169c663	https://www.google.com/	2026-02-28 18:00:00+00
a0000001-0001-4000-8000-000000000085	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	a0ce6978086cff8aa90b1c7a3cd27c5d1e8976791f39e73e4ef845b09e3669e5	https://www.instagram.com/	2026-02-28 20:35:45+00
a0000001-0001-4000-8000-000000000086	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	0fa74370b819cc049283e5391faef7e2377d7f8669b2b846fa646682356974b3	https://www.google.com/	2026-03-01 08:00:00+00
a0000001-0001-4000-8000-000000000087	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	ef2dd60516e1c2a848cfb7348fdbfb604ec1a22cded9bf03587c3c78e784fa61	https://www.facebook.com/	2026-03-01 09:30:15+00
a0000001-0001-4000-8000-000000000088	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	b1fd967aabbd678536671fdd90d20bbbf3e7044be7d15662e0e78814f072f0c3	https://maps.google.com/	2026-03-01 11:15:30+00
a0000001-0001-4000-8000-000000000089	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	direct	Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0	d780fb50bdb39c67d3605ed545e14742ac75ffca2ab9ceea6f9276fa21f835b6	https://www.facebook.com/	2026-03-01 13:40:00+00
a0000001-0001-4000-8000-000000000090	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15	f2d05f872e42a2fbf9e84e3d616d258d4790660cd279511ec47deab5cce3d8c8	https://www.google.com/	2026-03-01 15:05:22+00
a0000001-0001-4000-8000-000000000091	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	menu	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/17.0	063223c56986574dd274290a8eed5179aff82eef4c62ee989bdc95ebd5cdc5cf	https://www.instagram.com/	2026-03-01 16:30:00+00
a0000001-0001-4000-8000-000000000092	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	proyecto-materia	qr	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0	2aecab8bd0bc7db809ee9f23700cdc5f4de05b2552a7515f536fde057562affe	\N	2026-03-01 17:45:10+00
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

