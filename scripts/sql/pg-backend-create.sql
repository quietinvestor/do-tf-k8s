CREATE SCHEMA IF NOT EXISTS :schema_name;
CREATE SEQUENCE IF NOT EXISTS :schema_name.:sequence_name AS bigint;
CREATE TABLE IF NOT EXISTS :schema_name.states (
    id bigint NOT NULL DEFAULT nextval(:'full_sequence_name') PRIMARY KEY,
    name text UNIQUE,
    data text
);
CREATE UNIQUE INDEX IF NOT EXISTS states_by_name ON :schema_name.states (name);
CREATE role :group_name;
GRANT USAGE ON SCHEMA :schema_name TO :group_name;
GRANT ALL ON SEQUENCE :schema_name.:sequence_name TO :group_name;
GRANT ALL
ON :schema_name.states
TO :group_name;
CREATE role :user_name
LOGIN
PASSWORD :'user_password';
GRANT :group_name TO :user_name;
