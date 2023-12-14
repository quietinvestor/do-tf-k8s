import argparse
import json
import psycopg2
from psycopg2 import sql
import requests

def do_db_cluster_get_conn_dict(do_api_token, do_db_cluster_name, do_db_name):
    api_token = do_api_token
    api_url_base = "https://api.digitalocean.com/v2/"

    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {api_token}"
    }
  
    api_url = f"{api_url_base}databases"

    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        database_list = json.loads(response.content.decode('utf-8'))
    else:
        database_list = None

    if database_list is not None:
        for cluster in database_list["databases"]:
            if cluster["name"] == do_db_cluster_name:
                if do_db_name in cluster["db_names"]:
                    cluster["connection"]["database"] = do_db_name
                    return cluster["connection"]
                else:
                    print(f"No database exists with name: {do_db_name}")
            else:
                print(f"No cluster exists with name: {do_db_cluster_name}")
                return None
    else:
        print(f"DigitalOcean database cluster connection details request failed for {do_db_cluster_name}")

def sql_script(do_db_schema_name, do_db_sequence_name, do_db_group_name, do_db_user_name, do_db_user_password):
    cmd_list = [
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema};").format(
                    schema=sql.Identifier(do_db_schema_name)),
                sql.SQL("CREATE SEQUENCE IF NOT EXISTS {schema}.{seq} AS bigint;").format(
                    schema=sql.Identifier(do_db_schema_name),
                    seq=sql.Identifier(do_db_sequence_name)),
                sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {schema}.states (
                        id bigint NOT NULL DEFAULT nextval(\'{schema}.{seq}\') PRIMARY KEY,
                        name text UNIQUE,
                        data text
                    );
                    """).format(
                    schema=sql.Identifier(do_db_schema_name),
                    seq=sql.Identifier(do_db_sequence_name)),
                sql.SQL("CREATE UNIQUE INDEX IF NOT EXISTS states_by_name ON {schema}.states (name);").format(
                    schema=sql.Identifier(do_db_schema_name)),
                sql.SQL("CREATE role {group};").format(
                    group=sql.Identifier(do_db_group_name)),
                sql.SQL("GRANT USAGE ON SCHEMA {schema} TO {group};").format(
                    schema=sql.Identifier(do_db_schema_name),
                    group=sql.Identifier(do_db_group_name)),
                sql.SQL("GRANT ALL ON SEQUENCE {schema}.{seq} TO {group};").format(
                    schema=sql.Identifier(do_db_schema_name),
                    seq=sql.Identifier(do_db_sequence_name),
                    group=sql.Identifier(do_db_group_name)),
                sql.SQL("""
                    GRANT ALL
                    ON {schema}.states
                    TO {group};
                    """).format(
                    schema=sql.Identifier(do_db_schema_name),
                    group=sql.Identifier(do_db_group_name)),
                sql.SQL("""
                    CREATE role {user}
                    LOGIN
                    PASSWORD \'{password}\';
                    """).format(
                    user=sql.Identifier(do_db_user_name),
                    password=sql.Identifier(do_db_user_password)),
                sql.SQL("GRANT {group} TO {user};").format(
                    group=sql.Identifier(do_db_group_name),
                    user=sql.Identifier(do_db_user_name))
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
            port = do_db_cluster_conn_dict["port"])

        with db_cluster_connection:
            with db_cluster_connection.cursor() as curs:
                for cmd in sql_cmds:
                    curs.execute(cmd)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if db_cluster_connection is not None:
            db_cluster_connection.close()
            print('Database connection closed.')

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

    db_cluster_conn_dict = do_db_cluster_get_conn_dict(args.token, args.cluster_name, args.database_name)
    sql_cmd_list = sql_script(args.schema_name, args.sequence_name, args.group_name, args.user_name, args.user_password)
    do_db_cluster_connect(db_cluster_conn_dict, sql_cmd_list)
