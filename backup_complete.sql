--
-- PostgreSQL database dump
--

\restrict YFmA6gnhSUXv8JGu7Qt8OroAeqP5lobJ6uKsmICYdAI87W9gM4ELimPvt7m8elL

-- Dumped from database version 18.1
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
    admin_id integer
);


ALTER TABLE public.restaurants OWNER TO postgres;

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


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

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
5a0ba68c-de3e-479c-807e-ea8bee8582a7	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	sopas	Sopas de la casa	1	t	2026-02-13 07:00:55.854715-05	2026-02-13 15:58:10.170501-05
f0369b3a-209e-4b59-81cf-d497b9921d35	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	categoira 1	otra preuba	33	t	2026-02-13 06:57:39.367014-05	2026-02-16 19:42:49.613792-05
f4e424f8-e3a6-4046-9f0e-dda94fb64380	9dc24e18-08f9-42d4-83fc-bb4e40c4c968	preuba 12345	otra preuba	2	t	2026-02-12 19:38:25.864594-05	2026-02-16 19:44:11.501741-05
\.


--
-- Data for Name: dishes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dishes (id, categoria_id, nombre, descripcion, precio, precio_oferta, imagen_url, disponible, destacado, etiquetas, posicion, creado_en, actualizado_en, eliminado_en) FROM stdin;
0b41fc03-3689-49aa-ba8b-63d5b0497774	f4e424f8-e3a6-4046-9f0e-dda94fb64380	fsdf	3	3.00	3.00	\N	t	f	{no}	3	2026-02-13 14:23:46.473362-05	2026-02-13 14:23:46.473362-05	\N
9eeed5f5-aac0-4f90-ab6a-604537f2c9ef	f4e424f8-e3a6-4046-9f0e-dda94fb64380	fsdf	d	3.00	\N	\N	t	f	{no}	5	2026-02-13 15:08:57.146766-05	2026-02-13 15:53:54.632267-05	\N
87cb8c8f-32bf-4012-a5de-fefdf0848d1e	f4e424f8-e3a6-4046-9f0e-dda94fb64380	fsdf	3	3.00	3.00	\N	t	f	{no}	4	2026-02-13 14:49:19.118656-05	2026-02-13 15:54:07.707323-05	\N
48b05fc0-faf4-49a4-be31-6a8f42c8cf50	f4e424f8-e3a6-4046-9f0e-dda94fb64380	lentejas	plato fuerte	2.00	2.00	\N	t	f	{no}	2	2026-02-13 14:22:41.754277-05	2026-02-13 15:54:56.06418-05	\N
0dfbc9ba-95bc-40b9-8bbb-8766a64a84c6	5a0ba68c-de3e-479c-807e-ea8bee8582a7	ajiaco	sopa bogotana	12500.00	12500.00	\N	t	f	{"Ajiaco santafereño"}	1	2026-02-13 14:22:40.322016-05	2026-02-13 15:55:38.756714-05	\N
\.


--
-- Data for Name: restaurants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.restaurants (id, nombre, slug, descripcion, logo, telefono, direccion, horarios, creado_en, actualizado_en, admin_id) FROM stdin;
9dc24e18-08f9-42d4-83fc-bb4e40c4c968	Proyecto materia	proyecto-materia	Trabajo de materia	https://images.pexels.com/photos/2619967/pexels-photo-2619967.jpeg	3125698574	cra 1 en el centro	{"raw": "{\\n\\"lunes\\":  \\"9 a.m. a 8 p.m.\\"\\n\\"martes\\": \\"10 a.m. a 10 p.m.\\"\\n\\"domingo\\": \\"11 a.m a 10 p.m.\\"\\n}"}	2026-02-12 16:57:51.920692-05	2026-02-16 19:34:51.892407-05	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, nombre_completo, usuario, password, rol, activo, email) FROM stdin;
1	Juan Pérez	admin	$2b$12$AmVlWQ1O2TeQvps8nJ8mRO83uag0s2o9jujH6802rQWvDxftRJQBK	admin	t	f.ramirez@uniandes.edu.co
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


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
-- PostgreSQL database dump complete
--

\unrestrict YFmA6gnhSUXv8JGu7Qt8OroAeqP5lobJ6uKsmICYdAI87W9gM4ELimPvt7m8elL

