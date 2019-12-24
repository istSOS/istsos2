/*
    Replace SCHEMA_NAME with the schema names present in your
    istSOS database.
*/
SET search_path = SCHEMA_NAME, pg_catalog;

CREATE TABLE specimens
(
    id_spec bigint NOT NULL,
    identifier VARCHAR(36),
    id_qi_fk integer NOT NULL,
    id_eti_fk bigint NOT NULL,
    specimen json
);

CREATE SEQUENCE specimens_id_spec_seq
    INCREMENT 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE specimens_id_spec_seq
    OWNED BY specimens.id_spec;

ALTER TABLE ONLY specimens
    ADD CONSTRAINT specimens_pkey
    PRIMARY KEY (id_spec);

ALTER TABLE ONLY specimens
    ADD CONSTRAINT specimens_id_eti_fk_fkey
    FOREIGN KEY (id_eti_fk)
    REFERENCES event_time(id_eti)
    ON DELETE CASCADE;

ALTER TABLE ONLY specimens    
	ADD CONSTRAINT specimens_id_qi_fk_fkey
    FOREIGN KEY (id_qi_fk)
    REFERENCES quality_index(id_qi);

CREATE UNIQUE INDEX idx_spec_identifier
    ON specimens(identifier);

INSERT INTO obs_type (id_oty, name_oty, desc_oty)
VALUES (
    4,
    'insitu-fixed-specimen',
    'fixed, in-situ, pointwise observation from specimen'
);

INSERT INTO observed_properties VALUES (
    'water-ph',
    'urn:ogc:def:parameter:x-istsos:1.0:water:ph',
    'water pH',
    '{"interval": ["0", "14"], "role": "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0"}'
);

INSERT INTO observed_properties VALUES (
    'water-dox',
    'urn:ogc:def:parameter:x-istsos:1.0:water:dox',
    'water dissolved oxygen', 
    '{"interval": ["0", "1000"], "role": "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0"}'
);
