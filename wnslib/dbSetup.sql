--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.9
-- Dumped by pg_dump version 9.3.9
-- Started on 2015-09-07 17:03:38 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 8 (class 2615 OID 124543)
-- Name: wns; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA wns;


ALTER SCHEMA wns OWNER TO postgres;

SET search_path = wns, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 219 (class 1259 OID 124639)
-- Name: notification; Type: TABLE; Schema: wns; Owner: postgres; Tablespace: 
--

CREATE TABLE notification (
    id integer NOT NULL,
    name text,
    description text,
    "interval" integer
);


ALTER TABLE wns.notification OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 124637)
-- Name: notification_id_seq; Type: SEQUENCE; Schema: wns; Owner: postgres
--

CREATE SEQUENCE notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE wns.notification_id_seq OWNER TO postgres;

--
-- TOC entry 3485 (class 0 OID 0)
-- Dependencies: 218
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: wns; Owner: postgres
--

ALTER SEQUENCE notification_id_seq OWNED BY notification.id;


--
-- TOC entry 220 (class 1259 OID 124667)
-- Name: registration; Type: TABLE; Schema: wns; Owner: postgres; Tablespace: 
--

CREATE TABLE registration (
    user_id_fk integer NOT NULL,
    not_id_fk integer NOT NULL,
    not_list text[]
);


ALTER TABLE wns.registration OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 150882)
-- Name: responses; Type: TABLE; Schema: wns; Owner: postgres; Tablespace: 
--

CREATE TABLE responses (
    id integer NOT NULL,
    not_id integer NOT NULL,
    notification text,
    date timestamp with time zone,
    response text
);


ALTER TABLE wns.responses OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 150880)
-- Name: responses_id_seq; Type: SEQUENCE; Schema: wns; Owner: postgres
--

CREATE SEQUENCE responses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE wns.responses_id_seq OWNER TO postgres;

--
-- TOC entry 3486 (class 0 OID 0)
-- Dependencies: 250
-- Name: responses_id_seq; Type: SEQUENCE OWNED BY; Schema: wns; Owner: postgres
--

ALTER SEQUENCE responses_id_seq OWNED BY responses.id;


--
-- TOC entry 217 (class 1259 OID 124624)
-- Name: user; Type: TABLE; Schema: wns; Owner: postgres; Tablespace: 
--

CREATE TABLE "user" (
    id integer NOT NULL,
    username text,
    email text,
    twitter text,
    tel text,
    fax text,
    address text,
    zip integer,
    city text,
    state text,
    country text,
    name text,
    surname text
);


ALTER TABLE wns."user" OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 124622)
-- Name: user_id_seq; Type: SEQUENCE; Schema: wns; Owner: postgres
--

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE wns.user_id_seq OWNER TO postgres;

--
-- TOC entry 3487 (class 0 OID 0)
-- Dependencies: 216
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: wns; Owner: postgres
--

ALTER SEQUENCE user_id_seq OWNED BY "user".id;


--
-- TOC entry 3350 (class 2604 OID 124642)
-- Name: id; Type: DEFAULT; Schema: wns; Owner: postgres
--

ALTER TABLE ONLY notification ALTER COLUMN id SET DEFAULT nextval('notification_id_seq'::regclass);


--
-- TOC entry 3351 (class 2604 OID 150885)
-- Name: id; Type: DEFAULT; Schema: wns; Owner: postgres
--

ALTER TABLE ONLY responses ALTER COLUMN id SET DEFAULT nextval('responses_id_seq'::regclass);


--
-- TOC entry 3349 (class 2604 OID 124627)
-- Name: id; Type: DEFAULT; Schema: wns; Owner: postgres
--

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);


--
-- TOC entry 3359 (class 2606 OID 124649)
-- Name: notification_name_key; Type: CONSTRAINT; Schema: wns; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY notification
    ADD CONSTRAINT notification_name_key UNIQUE (name);


--
-- TOC entry 3361 (class 2606 OID 124647)
-- Name: notification_pkey; Type: CONSTRAINT; Schema: wns; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- TOC entry 3363 (class 2606 OID 124674)
-- Name: registration_pkey; Type: CONSTRAINT; Schema: wns; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY registration
    ADD CONSTRAINT registration_pkey PRIMARY KEY (user_id_fk, not_id_fk);


--
-- TOC entry 3353 (class 2606 OID 124636)
-- Name: user_email_key; Type: CONSTRAINT; Schema: wns; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- TOC entry 3355 (class 2606 OID 124632)
-- Name: user_pkey; Type: CONSTRAINT; Schema: wns; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3357 (class 2606 OID 124634)
-- Name: user_username_key; Type: CONSTRAINT; Schema: wns; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- TOC entry 3365 (class 2606 OID 124675)
-- Name: not_id_fkey; Type: FK CONSTRAINT; Schema: wns; Owner: postgres
--

ALTER TABLE ONLY registration
    ADD CONSTRAINT not_id_fkey FOREIGN KEY (not_id_fk) REFERENCES notification(id);


--
-- TOC entry 3366 (class 2606 OID 150894)
-- Name: not_id_fkey; Type: FK CONSTRAINT; Schema: wns; Owner: postgres
--

ALTER TABLE ONLY responses
    ADD CONSTRAINT not_id_fkey FOREIGN KEY (not_id) REFERENCES notification(id);


--
-- TOC entry 3364 (class 2606 OID 127102)
-- Name: user_id_fkey; Type: FK CONSTRAINT; Schema: wns; Owner: postgres
--

ALTER TABLE ONLY registration
    ADD CONSTRAINT user_id_fkey FOREIGN KEY (user_id_fk) REFERENCES "user"(id) ON DELETE CASCADE;


-- Completed on 2015-09-07 17:03:39 CEST

--
-- PostgreSQL database dump complete
--

