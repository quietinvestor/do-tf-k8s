CREATE SCHEMA IF NOT EXISTS :schema_name;
CREATE SEQUENCE IF NOT EXISTS :schema_name.:sequence_name AS bigint;
CREATE TABLE IF NOT EXISTS :schema_name.:table_name (
    id bigint NOT NULL DEFAULT nextval(:'full_sequence_name') PRIMARY KEY,
    name text UNIQUE,
    data text
);
CREATE role :group_name;
GRANT ALL
ON :schema_name.:table_name
TO :group_name;
CREATE role :user_name
LOGIN
PASSWORD :'user_password';
GRANT :group_name TO :user_name;
