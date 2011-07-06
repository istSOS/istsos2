--
-- PostgreSQL database dump
--

-- Started on 2010-10-07 16:53:48 CEST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- TOC entry 7 (class 2615 OID 40380)
-- Name: istsos; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA istsos;


SET search_path = istsos, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 2323 (class 1259 OID 40838)
-- Dependencies: 7
-- Name: event_time; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE event_time (
    id_eti bigint NOT NULL,
    id_prc_fk integer NOT NULL,
    time_eti timestamp with time zone NOT NULL
);


--
-- TOC entry 2322 (class 1259 OID 40836)
-- Dependencies: 7 2323
-- Name: event_time_id_eti_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE event_time_id_eti_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2685 (class 0 OID 0)
-- Dependencies: 2322
-- Name: event_time_id_eti_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE event_time_id_eti_seq OWNED BY event_time.id_eti;


--
-- TOC entry 2298 (class 1259 OID 40387)
-- Dependencies: 7
-- Name: feature_type; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE feature_type (
    name_fty character varying(25) NOT NULL,
    id_fty integer NOT NULL
);


--
-- TOC entry 2306 (class 1259 OID 40472)
-- Dependencies: 7 2298
-- Name: feature_type_id_fty_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE feature_type_id_fty_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2687 (class 0 OID 0)
-- Dependencies: 2306
-- Name: feature_type_id_fty_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE feature_type_id_fty_seq OWNED BY feature_type.id_fty;


--
-- TOC entry 2299 (class 1259 OID 40390)
-- Dependencies: 2607 1016 7
-- Name: foi; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE foi (
    desc_foi text,
    geom_foi public.geometry,
    id_fty_fk integer NOT NULL,
    id_foi integer NOT NULL,
    name_foi character varying(25),
    CONSTRAINT enforce_srid_geom_foi CHECK ((public.srid(geom_foi) = 21781))
);


--
-- TOC entry 2307 (class 1259 OID 40474)
-- Dependencies: 7 2299
-- Name: foi_id_foi_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE foi_id_foi_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2690 (class 0 OID 0)
-- Dependencies: 2307
-- Name: foi_id_foi_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE foi_id_foi_seq OWNED BY foi.id_foi;


--
-- TOC entry 2321 (class 1259 OID 40825)
-- Dependencies: 7
-- Name: measures; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE measures (
    id_msr bigint NOT NULL,
    id_eti_fk bigint NOT NULL,
    id_qi_fk integer NOT NULL,
    id_opr_fk integer NOT NULL,
    val_msr numeric(10,6) NOT NULL
);


--
-- TOC entry 2320 (class 1259 OID 40823)
-- Dependencies: 7 2321
-- Name: measures_id_msr_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE measures_id_msr_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2692 (class 0 OID 0)
-- Dependencies: 2320
-- Name: measures_id_msr_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE measures_id_msr_seq OWNED BY measures.id_msr;


--
-- TOC entry 2317 (class 1259 OID 40735)
-- Dependencies: 2617 2618 2619 1016 7
-- Name: positions; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE positions (
    id_pos bigint NOT NULL,
    id_qi_fk integer NOT NULL,
    geom_pos public.geometry NOT NULL,
    id_eti_fk bigint NOT NULL,
    CONSTRAINT enforce_dims_geom_mmo CHECK ((public.ndims(geom_pos) = 3)),
    CONSTRAINT enforce_geotype_geom_mmo CHECK (((public.geometrytype(geom_pos) = 'POINT'::text) OR (geom_pos IS NULL))),
    CONSTRAINT enforce_srid_geom_mmo CHECK ((public.srid(geom_pos) = 21781))
);


--
-- TOC entry 2316 (class 1259 OID 40733)
-- Dependencies: 2317 7
-- Name: measures_mobile_id_mmo_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE measures_mobile_id_mmo_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2693 (class 0 OID 0)
-- Dependencies: 2316
-- Name: measures_mobile_id_mmo_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE measures_mobile_id_mmo_seq OWNED BY positions.id_pos;


--
-- TOC entry 2300 (class 1259 OID 40405)
-- Dependencies: 7
-- Name: observed_properties; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE observed_properties (
    name_opr character varying(60) NOT NULL,
    desc_opr text,
    id_opr integer NOT NULL
);


--
-- TOC entry 2308 (class 1259 OID 40480)
-- Dependencies: 7 2300
-- Name: obs_pr_id_opr_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE obs_pr_id_opr_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2695 (class 0 OID 0)
-- Dependencies: 2308
-- Name: obs_pr_id_opr_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE obs_pr_id_opr_seq OWNED BY observed_properties.id_opr;


--
-- TOC entry 2315 (class 1259 OID 40682)
-- Dependencies: 7
-- Name: obs_type; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE obs_type (
    id_oty integer NOT NULL,
    name_oty character varying(60) NOT NULL,
    desc_oty character varying(120)
);


--
-- TOC entry 2314 (class 1259 OID 40680)
-- Dependencies: 2315 7
-- Name: obs_type_id_oty_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE obs_type_id_oty_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2697 (class 0 OID 0)
-- Dependencies: 2314
-- Name: obs_type_id_oty_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE obs_type_id_oty_seq OWNED BY obs_type.id_oty;


--
-- TOC entry 2319 (class 1259 OID 40799)
-- Dependencies: 7
-- Name: off_proc; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE off_proc (
    id_off_prc integer NOT NULL,
    id_off_fk integer NOT NULL,
    id_prc_fk integer NOT NULL
);


--
-- TOC entry 2318 (class 1259 OID 40797)
-- Dependencies: 2319 7
-- Name: off_proc_id_opr_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE off_proc_id_opr_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2699 (class 0 OID 0)
-- Dependencies: 2318
-- Name: off_proc_id_opr_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE off_proc_id_opr_seq OWNED BY off_proc.id_off_prc;


--
-- TOC entry 2301 (class 1259 OID 40414)
-- Dependencies: 2609 7
-- Name: offerings; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE offerings (
    name_off character varying(10) NOT NULL,
    desc_off text,
    expiration_off timestamp with time zone,
    active_off boolean DEFAULT true NOT NULL,
    id_off integer NOT NULL
);


--
-- TOC entry 2309 (class 1259 OID 40484)
-- Dependencies: 7 2301
-- Name: offerings_id_off_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE offerings_id_off_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2701 (class 0 OID 0)
-- Dependencies: 2309
-- Name: offerings_id_off_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE offerings_id_off_seq OWNED BY offerings.id_off;


--
-- TOC entry 2325 (class 1259 OID 40865)
-- Dependencies: 7
-- Name: proc_obs; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE proc_obs (
    id_pro integer NOT NULL,
    id_prc_fk integer NOT NULL,
    id_uom_fk integer NOT NULL,
    id_opr_fk integer NOT NULL
);


--
-- TOC entry 2324 (class 1259 OID 40863)
-- Dependencies: 7 2325
-- Name: prc_obs_id_pro_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE prc_obs_id_pro_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2703 (class 0 OID 0)
-- Dependencies: 2324
-- Name: prc_obs_id_pro_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE prc_obs_id_pro_seq OWNED BY proc_obs.id_pro;


--
-- TOC entry 2302 (class 1259 OID 40433)
-- Dependencies: 7
-- Name: procedures; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE procedures (
    name_prc character varying(30) NOT NULL,
    desc_prc text,
    stime_prc timestamp with time zone,
    etime_prc timestamp with time zone,
    id_prc integer NOT NULL,
    id_tru_fk integer NOT NULL,
    time_res_prc integer,
    id_oty_fk integer,
    id_foi_fk integer,
    assignedid_prc character varying(32)
);


--
-- TOC entry 2310 (class 1259 OID 40494)
-- Dependencies: 2302 7
-- Name: procedures_id_prc_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE procedures_id_prc_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2705 (class 0 OID 0)
-- Dependencies: 2310
-- Name: procedures_id_prc_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE procedures_id_prc_seq OWNED BY procedures.id_prc;


--
-- TOC entry 2303 (class 1259 OID 40442)
-- Dependencies: 7
-- Name: quality_index; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE quality_index (
    name_qi character varying(25) NOT NULL,
    desc_qi text,
    id_qi integer NOT NULL
);


--
-- TOC entry 2311 (class 1259 OID 40496)
-- Dependencies: 7 2303
-- Name: quality_index_id_qi_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE quality_index_id_qi_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2708 (class 0 OID 0)
-- Dependencies: 2311
-- Name: quality_index_id_qi_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE quality_index_id_qi_seq OWNED BY quality_index.id_qi;


--
-- TOC entry 2304 (class 1259 OID 40457)
-- Dependencies: 7
-- Name: time_res_unit; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE time_res_unit (
    id_tru integer NOT NULL,
    name_tru character varying(15)
);


--
-- TOC entry 2312 (class 1259 OID 40504)
-- Dependencies: 7 2304
-- Name: time_res_unit_id_tru_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE time_res_unit_id_tru_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2711 (class 0 OID 0)
-- Dependencies: 2312
-- Name: time_res_unit_id_tru_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE time_res_unit_id_tru_seq OWNED BY time_res_unit.id_tru;


--
-- TOC entry 2305 (class 1259 OID 40460)
-- Dependencies: 7
-- Name: uoms; Type: TABLE; Schema: istsos; Owner: -; Tablespace: 
--

CREATE TABLE uoms (
    name_uom character varying(20) NOT NULL,
    desc_uom text,
    id_uom integer NOT NULL
);


--
-- TOC entry 2313 (class 1259 OID 40506)
-- Dependencies: 7 2305
-- Name: uoms_id_uom_seq; Type: SEQUENCE; Schema: istsos; Owner: -
--

CREATE SEQUENCE uoms_id_uom_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2714 (class 0 OID 0)
-- Dependencies: 2313
-- Name: uoms_id_uom_seq; Type: SEQUENCE OWNED BY; Schema: istsos; Owner: -
--

ALTER SEQUENCE uoms_id_uom_seq OWNED BY uoms.id_uom;


--
-- TOC entry 2622 (class 2604 OID 40841)
-- Dependencies: 2322 2323 2323
-- Name: id_eti; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE event_time ALTER COLUMN id_eti SET DEFAULT nextval('event_time_id_eti_seq'::regclass);


--
-- TOC entry 2605 (class 2604 OID 40510)
-- Dependencies: 2306 2298
-- Name: id_fty; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE feature_type ALTER COLUMN id_fty SET DEFAULT nextval('feature_type_id_fty_seq'::regclass);


--
-- TOC entry 2606 (class 2604 OID 40511)
-- Dependencies: 2307 2299
-- Name: id_foi; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE foi ALTER COLUMN id_foi SET DEFAULT nextval('foi_id_foi_seq'::regclass);


--
-- TOC entry 2621 (class 2604 OID 40828)
-- Dependencies: 2320 2321 2321
-- Name: id_msr; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE measures ALTER COLUMN id_msr SET DEFAULT nextval('measures_id_msr_seq'::regclass);


--
-- TOC entry 2615 (class 2604 OID 40685)
-- Dependencies: 2314 2315 2315
-- Name: id_oty; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE obs_type ALTER COLUMN id_oty SET DEFAULT nextval('obs_type_id_oty_seq'::regclass);


--
-- TOC entry 2608 (class 2604 OID 40514)
-- Dependencies: 2308 2300
-- Name: id_opr; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE observed_properties ALTER COLUMN id_opr SET DEFAULT nextval('obs_pr_id_opr_seq'::regclass);


--
-- TOC entry 2620 (class 2604 OID 40802)
-- Dependencies: 2319 2318 2319
-- Name: id_off_prc; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE off_proc ALTER COLUMN id_off_prc SET DEFAULT nextval('off_proc_id_opr_seq'::regclass);


--
-- TOC entry 2610 (class 2604 OID 40516)
-- Dependencies: 2309 2301
-- Name: id_off; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE offerings ALTER COLUMN id_off SET DEFAULT nextval('offerings_id_off_seq'::regclass);


--
-- TOC entry 2616 (class 2604 OID 40738)
-- Dependencies: 2316 2317 2317
-- Name: id_pos; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE positions ALTER COLUMN id_pos SET DEFAULT nextval('measures_mobile_id_mmo_seq'::regclass);


--
-- TOC entry 2623 (class 2604 OID 40868)
-- Dependencies: 2325 2324 2325
-- Name: id_pro; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE proc_obs ALTER COLUMN id_pro SET DEFAULT nextval('prc_obs_id_pro_seq'::regclass);


--
-- TOC entry 2611 (class 2604 OID 40521)
-- Dependencies: 2310 2302
-- Name: id_prc; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE procedures ALTER COLUMN id_prc SET DEFAULT nextval('procedures_id_prc_seq'::regclass);


--
-- TOC entry 2612 (class 2604 OID 40522)
-- Dependencies: 2311 2303
-- Name: id_qi; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE quality_index ALTER COLUMN id_qi SET DEFAULT nextval('quality_index_id_qi_seq'::regclass);


--
-- TOC entry 2613 (class 2604 OID 40525)
-- Dependencies: 2312 2304
-- Name: id_tru; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE time_res_unit ALTER COLUMN id_tru SET DEFAULT nextval('time_res_unit_id_tru_seq'::regclass);


--
-- TOC entry 2614 (class 2604 OID 40526)
-- Dependencies: 2313 2305
-- Name: id_uom; Type: DEFAULT; Schema: istsos; Owner: -
--

ALTER TABLE uoms ALTER COLUMN id_uom SET DEFAULT nextval('uoms_id_uom_seq'::regclass);


--
-- TOC entry 2662 (class 2606 OID 40845)
-- Dependencies: 2323 2323 2323
-- Name: event_time_id_prc_fk_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY event_time
    ADD CONSTRAINT event_time_id_prc_fk_key UNIQUE (id_prc_fk, time_eti);


--
-- TOC entry 2664 (class 2606 OID 40843)
-- Dependencies: 2323 2323
-- Name: event_time_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY event_time
    ADD CONSTRAINT event_time_pkey PRIMARY KEY (id_eti);


--
-- TOC entry 2625 (class 2606 OID 40530)
-- Dependencies: 2298 2298
-- Name: feature_type_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY feature_type
    ADD CONSTRAINT feature_type_pkey PRIMARY KEY (id_fty);


--
-- TOC entry 2627 (class 2606 OID 40532)
-- Dependencies: 2299 2299
-- Name: foi_name_foi_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY foi
    ADD CONSTRAINT foi_name_foi_key UNIQUE (name_foi);


--
-- TOC entry 2629 (class 2606 OID 40534)
-- Dependencies: 2299 2299
-- Name: foi_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY foi
    ADD CONSTRAINT foi_pkey PRIMARY KEY (id_foi);


--
-- TOC entry 2657 (class 2606 OID 40830)
-- Dependencies: 2321 2321
-- Name: measures_fix_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY measures
    ADD CONSTRAINT measures_fix_pkey PRIMARY KEY (id_msr);


--
-- TOC entry 2659 (class 2606 OID 40936)
-- Dependencies: 2321 2321 2321
-- Name: measures_id_eti_fk_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY measures
    ADD CONSTRAINT measures_id_eti_fk_key UNIQUE (id_eti_fk, id_opr_fk);


--
-- TOC entry 2651 (class 2606 OID 40740)
-- Dependencies: 2317 2317
-- Name: measures_mobile_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY positions
    ADD CONSTRAINT measures_mobile_pkey PRIMARY KEY (id_pos);


--
-- TOC entry 2631 (class 2606 OID 40940)
-- Dependencies: 2300 2300
-- Name: obs_pr_name_opr_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY observed_properties
    ADD CONSTRAINT obs_pr_name_opr_key UNIQUE (name_opr);


--
-- TOC entry 2633 (class 2606 OID 40540)
-- Dependencies: 2300 2300
-- Name: obs_pr_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY observed_properties
    ADD CONSTRAINT obs_pr_pkey PRIMARY KEY (id_opr);


--
-- TOC entry 2649 (class 2606 OID 40687)
-- Dependencies: 2315 2315
-- Name: obs_type_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY obs_type
    ADD CONSTRAINT obs_type_pkey PRIMARY KEY (id_oty);


--
-- TOC entry 2653 (class 2606 OID 40862)
-- Dependencies: 2319 2319 2319
-- Name: off_proc_id_off_fk_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY off_proc
    ADD CONSTRAINT off_proc_id_off_fk_key UNIQUE (id_off_fk, id_prc_fk);


--
-- TOC entry 2655 (class 2606 OID 40804)
-- Dependencies: 2319 2319
-- Name: off_proc_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY off_proc
    ADD CONSTRAINT off_proc_pkey PRIMARY KEY (id_off_prc);


--
-- TOC entry 2635 (class 2606 OID 40922)
-- Dependencies: 2301 2301
-- Name: offerings_name_off_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY offerings
    ADD CONSTRAINT offerings_name_off_key UNIQUE (name_off);


--
-- TOC entry 2637 (class 2606 OID 40546)
-- Dependencies: 2301 2301
-- Name: offerings_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY offerings
    ADD CONSTRAINT offerings_pkey PRIMARY KEY (id_off);


--
-- TOC entry 2666 (class 2606 OID 40870)
-- Dependencies: 2325 2325
-- Name: prc_obs_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY proc_obs
    ADD CONSTRAINT prc_obs_pkey PRIMARY KEY (id_pro);


--
-- TOC entry 2668 (class 2606 OID 40938)
-- Dependencies: 2325 2325 2325 2325
-- Name: proc_obs_id_uom_fk_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY proc_obs
    ADD CONSTRAINT proc_obs_id_uom_fk_key UNIQUE (id_uom_fk, id_opr_fk, id_prc_fk);


--
-- TOC entry 2639 (class 2606 OID 40924)
-- Dependencies: 2302 2302
-- Name: procedures_assignedid_prc_key; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY procedures
    ADD CONSTRAINT procedures_assignedid_prc_key UNIQUE (assignedid_prc);


--
-- TOC entry 2641 (class 2606 OID 40556)
-- Dependencies: 2302 2302
-- Name: procedures_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY procedures
    ADD CONSTRAINT procedures_pkey PRIMARY KEY (id_prc);


--
-- TOC entry 2643 (class 2606 OID 40558)
-- Dependencies: 2303 2303
-- Name: quality_index_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY quality_index
    ADD CONSTRAINT quality_index_pkey PRIMARY KEY (id_qi);


--
-- TOC entry 2645 (class 2606 OID 40566)
-- Dependencies: 2304 2304
-- Name: time_res_unit_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY time_res_unit
    ADD CONSTRAINT time_res_unit_pkey PRIMARY KEY (id_tru);


--
-- TOC entry 2647 (class 2606 OID 40568)
-- Dependencies: 2305 2305
-- Name: uoms_pkey; Type: CONSTRAINT; Schema: istsos; Owner: -; Tablespace: 
--

ALTER TABLE ONLY uoms
    ADD CONSTRAINT uoms_pkey PRIMARY KEY (id_uom);


--
-- TOC entry 2660 (class 1259 OID 47251)
-- Dependencies: 2323 2323
-- Name: ety_prc_date; Type: INDEX; Schema: istsos; Owner: -; Tablespace: 
--

CREATE INDEX ety_prc_date ON event_time USING btree (id_eti, time_eti);


--
-- TOC entry 2679 (class 2606 OID 40901)
-- Dependencies: 2640 2323 2302
-- Name: event_time_id_prc_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY event_time
    ADD CONSTRAINT event_time_id_prc_fk_fkey FOREIGN KEY (id_prc_fk) REFERENCES procedures(id_prc) ON DELETE CASCADE;


--
-- TOC entry 2669 (class 2606 OID 40590)
-- Dependencies: 2624 2298 2299
-- Name: foi_id_fty_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY foi
    ADD CONSTRAINT foi_id_fty_fk_fkey FOREIGN KEY (id_fty_fk) REFERENCES feature_type(id_fty);


--
-- TOC entry 2678 (class 2606 OID 40831)
-- Dependencies: 2642 2303 2321
-- Name: measures_fix_id_qi_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY measures
    ADD CONSTRAINT measures_fix_id_qi_fk_fkey FOREIGN KEY (id_qi_fk) REFERENCES quality_index(id_qi);


--
-- TOC entry 2677 (class 2606 OID 40896)
-- Dependencies: 2321 2663 2323
-- Name: measures_id_eti_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY measures
    ADD CONSTRAINT measures_id_eti_fk_fkey FOREIGN KEY (id_eti_fk) REFERENCES event_time(id_eti) ON DELETE CASCADE;


--
-- TOC entry 2673 (class 2606 OID 40741)
-- Dependencies: 2317 2642 2303
-- Name: measures_mobile_id_qi_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY positions
    ADD CONSTRAINT measures_mobile_id_qi_fk_fkey FOREIGN KEY (id_qi_fk) REFERENCES quality_index(id_qi);


--
-- TOC entry 2675 (class 2606 OID 40886)
-- Dependencies: 2301 2319 2636
-- Name: off_proc_id_off_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY off_proc
    ADD CONSTRAINT off_proc_id_off_fk_fkey FOREIGN KEY (id_off_fk) REFERENCES offerings(id_off);


--
-- TOC entry 2676 (class 2606 OID 40891)
-- Dependencies: 2319 2640 2302
-- Name: off_proc_id_prc_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY off_proc
    ADD CONSTRAINT off_proc_id_prc_fk_fkey FOREIGN KEY (id_prc_fk) REFERENCES procedures(id_prc) ON DELETE CASCADE;


--
-- TOC entry 2674 (class 2606 OID 40916)
-- Dependencies: 2663 2317 2323
-- Name: positions_id_eti_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY positions
    ADD CONSTRAINT positions_id_eti_fk_fkey FOREIGN KEY (id_eti_fk) REFERENCES event_time(id_eti) ON DELETE CASCADE;


--
-- TOC entry 2681 (class 2606 OID 40881)
-- Dependencies: 2325 2300 2632
-- Name: prc_obs_id_opr_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY proc_obs
    ADD CONSTRAINT prc_obs_id_opr_fk_fkey FOREIGN KEY (id_opr_fk) REFERENCES observed_properties(id_opr);


--
-- TOC entry 2680 (class 2606 OID 40876)
-- Dependencies: 2646 2305 2325
-- Name: prc_obs_id_uom_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY proc_obs
    ADD CONSTRAINT prc_obs_id_uom_fk_fkey FOREIGN KEY (id_uom_fk) REFERENCES uoms(id_uom);


--
-- TOC entry 2682 (class 2606 OID 40911)
-- Dependencies: 2640 2302 2325
-- Name: proc_obs_id_prc_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY proc_obs
    ADD CONSTRAINT proc_obs_id_prc_fk_fkey FOREIGN KEY (id_prc_fk) REFERENCES procedures(id_prc) ON DELETE CASCADE;


--
-- TOC entry 2671 (class 2606 OID 40760)
-- Dependencies: 2628 2299 2302
-- Name: procedures_id_foi_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY procedures
    ADD CONSTRAINT procedures_id_foi_fk_fkey FOREIGN KEY (id_foi_fk) REFERENCES foi(id_foi);


--
-- TOC entry 2670 (class 2606 OID 40688)
-- Dependencies: 2648 2315 2302
-- Name: procedures_id_oty_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY procedures
    ADD CONSTRAINT procedures_id_oty_fk_fkey FOREIGN KEY (id_oty_fk) REFERENCES obs_type(id_oty);


--
-- TOC entry 2672 (class 2606 OID 40650)
-- Dependencies: 2302 2304 2644
-- Name: procedures_id_tru_fk_fkey; Type: FK CONSTRAINT; Schema: istsos; Owner: -
--

ALTER TABLE ONLY procedures
    ADD CONSTRAINT procedures_id_tru_fk_fkey FOREIGN KEY (id_tru_fk) REFERENCES time_res_unit(id_tru);

--
-- INSERT CONSTANT VALUES
--

INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('outboud', 'gross error', 0);
INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('raw', 'the format is correct', 100);
INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('reasonable', 'the value is in a resonable range', 200);
INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('timely coherent', 'the value is coherent with time-series', 300);
INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('spatilly coherent', 'the value is coherent with close by observations', 400);
INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('manually adjusted', 'the value has been manually corrected', 500);
INSERT INTO quality_index (name_qi, desc_qi, id_qi) VALUES ('correct', 'the value has not been modified and is correct', 600);

INSERT INTO obs_type (id_oty, name_oty, desc_oty) VALUES (1, 'fixpoint', 'fixed, in-situ, pointwise observation');
INSERT INTO obs_type (id_oty, name_oty, desc_oty) VALUES (2, 'mobilepoint', 'mobile, in-situ, pointwise observation');
INSERT INTO obs_type (id_oty, name_oty, desc_oty) VALUES (3, 'virtual', 'virtual procedure');




-- Completed on 2010-10-07 16:53:49 CEST

--
-- PostgreSQL database dump complete
--

