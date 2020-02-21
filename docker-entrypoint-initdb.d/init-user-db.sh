#!/bin/bash
set -e
# --dbname "$POSTGRES_DB"


    # SET TIME ZONE '${TZ}';
    # CREATE DATABASE istsos ENCODING 'UTF8';
    # CREATE EXTENSION postgis;
    # CREATE TABLE distributors;


psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SET TIME ZONE '${TZ}';
    CREATE DATABASE istsos ENCODING 'UTF8';
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    CREATE EXTENSION postgis;

EOSQL
