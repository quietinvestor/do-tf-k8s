import argparse
import json
import psycopg2
from psycopg2 import extensions
from psycopg2 import sql
import requests
import sys

def do_api_request_get(do_api_token, do_api_endpoint):
    api_token = do_api_token
    api_url_base = "https://api.digitalocean.com/v2/"

    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {api_token}"
    }
  
    api_url = f"{api_url_base}{do_api_endpoint}"

    try:
        response = requests.get(api_url, headers = headers, timeout = 5)
        response.raise_for_status() 
    except requests.exceptions.HTTPError as errhttp: 
        print("HTTP Error") 
        raise SystemExit(errhttp)
    except requests.exceptions.ReadTimeout as errrt: 
        print("Time out") 
        raise SystemExit(errrt)
    except requests.exceptions.ConnectionError as errconn: 
        print("Connection error") 
        raise SystemExit(errconn)
    except requests.exceptions.RequestException as errex: 
        print("Exception request")
        raise SystemExit(errex)
    else:
        if response.status_code == 200:
            response_json = response.json()
        else:
            response_json = None
    finally:
        return response_json

def do_db_cluster_get_conn_dict(do_db_cluster_name, do_db_name, do_db_list):
    if do_db_list is not None:
        for cluster in do_db_list["databases"]:
            if cluster["name"] == do_db_cluster_name:
                if do_db_name in cluster["db_names"]:
                    cluster["connection"]["database"] = do_db_name
                    return cluster["connection"]
                else:
                    print(f"No database exists with name: {do_db_name}")
            else:
                print(f"No cluster exists with name: {do_db_cluster_name}")
    else:
        print(f"DigitalOcean database cluster connection details request failed for {do_db_cluster_name}")

    return None

def sql_script(db_schema_name, db_sequence_name, db_group_name, db_user_name, db_user_password):
    schema_name = sql.Identifier(db_schema_name)
    seq_name = sql.Identifier(db_sequence_name)
    group_name = sql.Identifier(db_group_name)
    user_name = sql.Identifier(db_user_name)
    user_password = sql.Literal(db_user_password)

    cmd_list = [
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema};").format(
                    schema = schema_name),
                sql.SQL("CREATE SEQUENCE IF NOT EXISTS {schema}.{seq} AS bigint;").format(
                    schema = schema_name,
                    seq = seq_name),
                sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {schema}.states (
                        id bigint NOT NULL DEFAULT nextval(\'{schema}.{seq}\') PRIMARY KEY,
                        name text UNIQUE,
                        data text
                    );
                    """).format(
                    schema = schema_name,
                    seq = seq_name),
                sql.SQL("CREATE UNIQUE INDEX IF NOT EXISTS states_by_name ON {schema}.states (name);").format(
                    schema = schema_name),
                sql.SQL("CREATE role {group};").format(
                    group = group_name),
                sql.SQL("GRANT USAGE ON SCHEMA {schema} TO {group};").format(
                    schema = schema_name,
                    group = group_name),
                sql.SQL("GRANT ALL ON SEQUENCE {schema}.{seq} TO {group};").format(
                    schema = schema_name,
                    seq = seq_name,
                    group = group_name),
                sql.SQL("""
                    GRANT ALL
                    ON {schema}.states
                    TO {group};
                    """).format(
                    schema = schema_name,
                    group = group_name),
                sql.SQL("""
                    CREATE role {user}
                    LOGIN
                    PASSWORD {password};
                    """).format(
                    user = user_name,
                    password = user_password),
                sql.SQL("GRANT {group} TO {user};").format(
                    group = group_name,
                    user = user_name)
    ]

    return cmd_list

def do_db_cluster_connect(do_db_cluster_conn_dict, sql_cmds):
    db_cluster_connection = None

    try:
        db_cluster_connection = psycopg2.connect(
            dbname = do_db_cluster_conn_dict["database"],
            user = do_db_cluster_conn_dict["user"],
            password = do_db_cluster_conn_dict["password"],
            host = do_db_cluster_conn_dict["host"],
            port = do_db_cluster_conn_dict["port"],
            connect_timeout = 5)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    else:
        print("Database connection open.", file=sys.stderr)

        with db_cluster_connection:
            with db_cluster_connection.cursor() as curs:
                for cmd in sql_cmds:
                    curs.execute(cmd)

        print("Successfully executed SQL script.", file=sys.stderr)
    finally:
        if db_cluster_connection is not None:
            db_cluster_connection.close()
            print('Database connection closed.', file=sys.stderr)

def do_db_cluster_conn_str_custom(do_db_cluster_conn_dict, do_db_name, db_user_name, db_user_password):
    if do_db_cluster_conn_dict is not None:
        conn_str_custom = f"postgresql://{db_user_name}:{db_user_password}@{do_db_cluster_conn_dict['host']}:{do_db_cluster_conn_dict['port']}/{do_db_name}?sslmode=require&connect_timeout=5"

        return conn_str_custom
    else:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    arg_opt_list = [
        [ ["-c", "--cluster-name"], { 'help': "DigitalOcean PostgreSQL database cluster name", 'required': True } ],
        [ ["-d", "--database-name"], { 'help': "PostgreSQL database name", 'required': True } ],
        [ ["-g", "--group-name"], { 'help': "PostgreSQL database schema group name", 'required': True } ],
        [ ["-p", "--user-password"], { 'help': "PostgreSQL database schema user password", 'required': True } ],
        [ ["-q", "--sequence-name"], { 'help': "PostgreSQL database schema sequence name", 'required': True } ],
        [ ["-s", "--schema-name"], { 'help': "PostgreSQL database schema name", 'required': True } ],
        [ ["-t", "--token"], { 'help': "DigitalOcean API token", 'required': True } ],
        [ ["-u", "--user-name"], { 'help': "PostgreSQL database schema user name", 'required': True } ]
    ]

    for arg_opt in arg_opt_list:
        optional_arg_list = arg_opt[0]
        positional_arg_dict = arg_opt[1]

        parser.add_argument(*optional_arg_list, **positional_arg_dict)

    args = parser.parse_args()

    db_list = do_api_request_get(args.token, "databases")
    db_cluster_conn_dict = do_db_cluster_get_conn_dict(args.cluster_name, args.database_name, db_list)
    sql_cmd_list = sql_script(args.schema_name, args.sequence_name, args.group_name, args.user_name, args.user_password)
    do_db_cluster_connect(db_cluster_conn_dict, sql_cmd_list)
    db_conn_str_custom = do_db_cluster_conn_str_custom(db_cluster_conn_dict, args.database_name, args.user_name, args.user_password)

    if db_conn_str_custom is not None:
        print(db_conn_str_custom)
    else:
        print(f"Connection string for PostgresSQL DB cannot be {db_conn_str_custom}")
