--
-- PostgreSQL database dump
--

\restrict qH8scikluJzxlBIITF9pri9NQOz7J6hSBvjaknjvguPI1tBNDKy6MdD644vAy7J

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

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
-- Name: email_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token text NOT NULL,
    token_type text NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used_at timestamp with time zone
);


ALTER TABLE public.email_tokens OWNER TO postgres;

--
-- Name: email_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.email_tokens_id_seq OWNER TO postgres;

--
-- Name: email_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_tokens_id_seq OWNED BY public.email_tokens.id;


--
-- Name: notifications_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications_log (
    id integer NOT NULL,
    user_id integer NOT NULL,
    vehicle_id integer NOT NULL,
    schedule_item_id integer NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications_log OWNER TO postgres;

--
-- Name: notifications_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_log_id_seq OWNER TO postgres;

--
-- Name: notifications_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_log_id_seq OWNED BY public.notifications_log.id;


--
-- Name: schedule_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_items (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    service_name text NOT NULL,
    interval_miles integer,
    interval_months integer,
    severe_interval_miles integer,
    notes text
);


ALTER TABLE public.schedule_items OWNER TO postgres;

--
-- Name: schedule_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schedule_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_items_id_seq OWNER TO postgres;

--
-- Name: schedule_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedule_items_id_seq OWNED BY public.schedule_items.id;


--
-- Name: service_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_records (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    schedule_item_id integer,
    service_date date NOT NULL,
    mileage_at_service integer NOT NULL,
    cost numeric(8,2),
    performed_by text,
    notes text,
    receipt_key text
);


ALTER TABLE public.service_records OWNER TO postgres;

--
-- Name: service_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_records_id_seq OWNER TO postgres;

--
-- Name: service_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_records_id_seq OWNED BY public.service_records.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email text NOT NULL,
    hashed_password text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    email_verified boolean DEFAULT false NOT NULL
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
-- Name: vehicles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicles (
    id integer NOT NULL,
    make text NOT NULL,
    model text NOT NULL,
    year integer NOT NULL,
    vin text,
    current_mileage integer NOT NULL,
    mileage_updated_at timestamp with time zone DEFAULT now() NOT NULL,
    avg_miles_per_day numeric(6,2) DEFAULT 30.0,
    user_id integer NOT NULL
);


ALTER TABLE public.vehicles OWNER TO postgres;

--
-- Name: vehicles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicles_id_seq OWNER TO postgres;

--
-- Name: vehicles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicles_id_seq OWNED BY public.vehicles.id;


--
-- Name: email_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_tokens ALTER COLUMN id SET DEFAULT nextval('public.email_tokens_id_seq'::regclass);


--
-- Name: notifications_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_log ALTER COLUMN id SET DEFAULT nextval('public.notifications_log_id_seq'::regclass);


--
-- Name: schedule_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items ALTER COLUMN id SET DEFAULT nextval('public.schedule_items_id_seq'::regclass);


--
-- Name: service_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_records ALTER COLUMN id SET DEFAULT nextval('public.service_records_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vehicles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicles ALTER COLUMN id SET DEFAULT nextval('public.vehicles_id_seq'::regclass);


--
-- Data for Name: email_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.email_tokens VALUES (1, 2, 'oIl8MV-YIDOAaVRbKnJ7yhtS-DY31IDzW08uJBK2w_M', 'verify_email', '2026-08-04 04:36:27.228896+00', NULL);
INSERT INTO public.email_tokens VALUES (2, 2, 'm4teoNrxTnajuzmWs8wEOmVlUDEFATFuX3yK3eyBjAM', 'verify_email', '2026-08-04 05:01:52.400677+00', '2026-08-03 05:02:05.870531+00');
INSERT INTO public.email_tokens VALUES (3, 2, 'im2r8jBKVr8KF9fKL8KzQmmJmJRJJIQqoNK9LWAQcu4', 'reset_password', '2026-08-03 06:02:33.386618+00', NULL);
INSERT INTO public.email_tokens VALUES (4, 2, 'lBsgTFiPsf2SAt4Xkc5BWh5bNlOtQzwLc6etZOOIWP4', 'reset_password', '2026-08-03 06:03:24.085959+00', NULL);
INSERT INTO public.email_tokens VALUES (5, 2, 'XbtU-GDl-WAO9jj4PfKywyssrLUXMhe9b-o-w6l-hGA', 'reset_password', '2026-08-03 06:04:31.985992+00', NULL);


--
-- Data for Name: notifications_log; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: schedule_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.schedule_items VALUES (8, 2, 'Replace engine oil and oil filter', 7500, 6, NULL, 'Paired with tire rotation and road-test at same interval');
INSERT INTO public.schedule_items VALUES (9, 2, 'Rotate tires', 7500, 6, NULL, 'Paired with oil change');
INSERT INTO public.schedule_items VALUES (10, 2, 'Replace engine air filter', 30000, 24, NULL, 'Part of the larger 30,000-mile service');
INSERT INTO public.schedule_items VALUES (11, 2, 'Replace brake fluid', 30000, 24, NULL, 'Part of the larger 30,000-mile service');
INSERT INTO public.schedule_items VALUES (12, 2, 'Replace engine coolant', 30000, 24, NULL, 'Part of the larger 30,000-mile service');
INSERT INTO public.schedule_items VALUES (13, 2, 'Inspect transmission fluid', 30000, 24, NULL, 'Manual lists this as an inspection item at 30k, not a fixed replacement interval');
INSERT INTO public.schedule_items VALUES (14, 2, 'Replace brake pads', 50000, NULL, NULL, 'Estimated — wear-based, not in manual fixed schedule');
INSERT INTO public.schedule_items VALUES (15, 2, 'Replace battery', NULL, 48, NULL, 'Estimated — typical battery lifespan, not in manual fixed schedule');
INSERT INTO public.schedule_items VALUES (16, 2, 'Replace tires (set of 4)', 55000, NULL, NULL, 'Estimated — wear-based, not in manual fixed schedule');


--
-- Data for Name: service_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.service_records VALUES (1, 2, 8, '2023-04-15', 18420, 34.50, 'Valvoline Instant Oil Change', 'Full synthetic oil', NULL);
INSERT INTO public.service_records VALUES (2, 2, 9, '2023-04-15', 18420, 34.49, 'Valvoline Instant Oil Change', 'Full synthetic oil', NULL);
INSERT INTO public.service_records VALUES (3, 2, NULL, '2023-09-23', 24105, 24.99, 'DIY', 'Cabin air filter replacement', NULL);
INSERT INTO public.service_records VALUES (4, 2, 8, '2023-11-18', 26410, 72.99, 'Valvoline Instant Oil Change', 'Routine maintenance', NULL);
INSERT INTO public.service_records VALUES (5, 2, 15, '2024-02-10', 28980, 184.99, 'AutoZone', 'Battery replacement — old battery failed cold-start test', NULL);
INSERT INTO public.service_records VALUES (6, 2, 8, '2024-05-11', 31865, 37.50, 'Firestone Complete Auto Care', 'Multi-point inspection', NULL);
INSERT INTO public.service_records VALUES (7, 2, 9, '2024-05-11', 31865, 37.49, 'Firestone Complete Auto Care', 'Multi-point inspection', NULL);
INSERT INTO public.service_records VALUES (8, 2, 10, '2024-08-24', 35420, 32.50, 'DIY', 'OEM replacement filter', NULL);
INSERT INTO public.service_records VALUES (9, 2, 14, '2024-11-16', 39180, 312.45, 'Local Auto Repair', 'Front brake pads replaced — worn to 3mm', NULL);
INSERT INTO public.service_records VALUES (10, 2, 8, '2025-01-25', 41060, 76.99, 'Toyota Dealer', 'Synthetic oil and filter', NULL);
INSERT INTO public.service_records VALUES (11, 2, 11, '2025-06-14', 46215, 139.99, 'Toyota Dealer', 'Brake fluid flush — recommended at inspection', NULL);
INSERT INTO public.service_records VALUES (12, 2, 8, '2025-09-20', 49870, 40.00, 'Toyota Dealer', 'Routine service', NULL);
INSERT INTO public.service_records VALUES (13, 2, 9, '2025-09-20', 49870, 39.99, 'Toyota Dealer', 'Routine service', NULL);
INSERT INTO public.service_records VALUES (14, 2, 16, '2026-02-21', 54930, 768.40, 'Discount Tire', 'New tires (set of 4) — replaced original tires', NULL);
INSERT INTO public.service_records VALUES (15, 2, NULL, '2026-02-21', 54930, 119.99, 'Discount Tire', 'Wheel alignment — performed with new tires', NULL);
INSERT INTO public.service_records VALUES (16, 2, 8, '2026-06-06', 58410, 82.99, 'Toyota Dealer', 'Routine maintenance', NULL);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users VALUES (2, 'muneera0615@gmail.com', '$2b$12$F4Iwh0ddsJPriIuvsLjN7.oYqRnFwi59qO1HVrjA1UwSG/umn2yYi', '2026-08-03 03:06:20.72564+00', true);


--
-- Data for Name: vehicles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.vehicles VALUES (2, 'Lexus', 'ES300', 2002, NULL, 164784, '2026-07-24 00:36:22.405339+00', 30.00, 2);


--
-- Name: email_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_tokens_id_seq', 10, true);


--
-- Name: notifications_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_log_id_seq', 1, true);


--
-- Name: schedule_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedule_items_id_seq', 16, true);


--
-- Name: service_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_records_id_seq', 18, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 9, true);


--
-- Name: vehicles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehicles_id_seq', 6, true);


--
-- Name: email_tokens email_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_tokens
    ADD CONSTRAINT email_tokens_pkey PRIMARY KEY (id);


--
-- Name: email_tokens email_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_tokens
    ADD CONSTRAINT email_tokens_token_key UNIQUE (token);


--
-- Name: notifications_log notifications_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_log
    ADD CONSTRAINT notifications_log_pkey PRIMARY KEY (id);


--
-- Name: schedule_items schedule_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items
    ADD CONSTRAINT schedule_items_pkey PRIMARY KEY (id);


--
-- Name: service_records service_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_records
    ADD CONSTRAINT service_records_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (id);


--
-- Name: email_tokens email_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_tokens
    ADD CONSTRAINT email_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications_log notifications_log_schedule_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_log
    ADD CONSTRAINT notifications_log_schedule_item_id_fkey FOREIGN KEY (schedule_item_id) REFERENCES public.schedule_items(id);


--
-- Name: notifications_log notifications_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_log
    ADD CONSTRAINT notifications_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications_log notifications_log_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_log
    ADD CONSTRAINT notifications_log_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: schedule_items schedule_items_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items
    ADD CONSTRAINT schedule_items_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: service_records service_records_schedule_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_records
    ADD CONSTRAINT service_records_schedule_item_id_fkey FOREIGN KEY (schedule_item_id) REFERENCES public.schedule_items(id);


--
-- Name: service_records service_records_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_records
    ADD CONSTRAINT service_records_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicles vehicles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict qH8scikluJzxlBIITF9pri9NQOz7J6hSBvjaknjvguPI1tBNDKy6MdD644vAy7J

