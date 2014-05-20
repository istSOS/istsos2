-- ===============================================
-- WORKING
-- ===============================================
SET search_path = SCHEMA_NAME, pg_catalog;

CREATE TYPE status AS ENUM ('verified','pending');

CREATE TABLE cron_log
(
   id_clo serial NOT NULL, 
   id_prc_fk integer NOT NULL,              -- "5"
   process_clo character varying NOT NULL, -- "acquisizione"
   element_clo character varying NOT NULL, -- "T_TREVANO"
   datetime_clo timestamp with time zone NOT NULL, -- "NOW"
   message_clo character varying NOT NULL, -- "TIPO DI ECCEZIONE"
   details_clo character varying, -- "MESSAGGIO LIBERO"
   status_clo status,            -- "error"
   PRIMARY KEY (id_clo)
);

ALTER TABLE procedures DROP CONSTRAINT procedures_id_tru_fk_fkey;
ALTER TABLE procedures ADD COLUMN time_acq_prc integer;
ALTER TABLE procedures DROP COLUMN id_tru_fk;

ALTER TABLE ONLY cron_log
    ADD CONSTRAINT cron_log_id_prc_fk_fkey FOREIGN KEY (id_prc_fk) REFERENCES procedures(id_prc) ON DELETE CASCADE;
DROP SEQUENCE time_res_unit_id_tru_seq CASCADE;
DROP TABLE time_res_unit;