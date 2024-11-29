# rh_db_controller.py
import json
import os
import psycopg

from psycopg import sql
from psycopg_pool import pool, ConnectionPool
# from psycopg_pool import pool_async

class RHDatabaseController:
    """
    Handles transactions with the PostgreSQL database.
    """

    def __init__(self, conn_params=None, db_name=None):
        if db_name is None:
            raise ValueError("Please give a db_name value.")

        if conn_params is None:
            conn_params = {
                'dbname': db_name,
                'user': os.getenv('pg_link_usr'),
                'password': os.getenv('pg_link_pwd'),
                'host': 'localhost',
                'port': '2000'
            }
        self.__conn_params = conn_params
        self.conn_pool = None
        self.conn = None
        self.db_name = db_name
        self.create_pool()
        self.get_connection()

    def create_pool(self):
        print("Creating connection pool...")
        try:
            self.conn_pool = ConnectionPool(self.__conn_params)
            print("Connection pool created successfully.")
        except psycopg.Error as e:
            print("Error creating connection pool.")
            raise e

    def get_connection(self):
        try:
            if self.conn_pool:
                self.conn = self.conn_pool.connection()
                print("Connection acquired from pool.")
            else:
                raise Exception("Connection pool is not initialized.")
        except psycopg.Error as e:
            print("Error getting connection from pool.")
            raise e

    def close_connection(self):
        if self.conn:
            if self.conn_pool:
                self.conn_pool.putconn(self.conn)
            else:
                self.conn.close()
        print("Database connection closed.")

    def insert_rows(self, table: str, columns: list[str] = None, conditions: dict[str, str] = None, rows: list[tuple] = None):
        if not rows:
            raise ValueError("There are no rows to insert.")

        # intial values
        sql_template = f'INSERT INTO "{self.db_name}"."public"."{table}" columns VALUES values conditions'

        # construct columns and conditions strings plus collect values
        columns_string = "" if columns is None else '(' + ', '.join(
            [f'"{column}"' for column in columns]) + ')'
        conditions_string = "" if conditions is None else (
            "WHERE " + ' '.join([f'"{key}" = ''$1''' for key in conditions.keys()]))
        values_string = '(' + \
            ', '.join(f'''${i+1}''' for i in range(len(columns))) + ')'

        # replace columns and values placeholder
        sql_template = sql_template.replace("columns", columns_string)
        sql_template = sql_template.replace("conditions", conditions_string)
        sql_template = sql_template.replace("values", values_string)
        sql_template = sql_template.strip()

        # format into sql string
        sql_string = sql.SQL(sql_template)

        print(f"Inserting {len(rows)} rows into {table}.")
        with self.conn.cursor() as cursor:
            try:
                cursor.executemany(sql_string, rows)
                self.conn.commit()
            except psycopg.Error as e:
                self.conn.rollback()  # Rollback in case of error
                print("Error inserting rows.")
                raise e

    def query_row(self, table: str = None, columns: list[str] = None, conditions: dict[str, str] = None):
        if table is None:
            raise ValueError("No table was entered.")
        if columns is None:
            columns = ['*']  # default is *
            print(f"Using * for select query to {table}.")

        # inital value
        sql_template = f'SELECT columns FROM "{self.db_name}"."public"."{table}" conditions'

        # construct columns and conditions plus extract parameters
        column_string = ' '.join([f'"{column}"' for column in columns]).strip(
        ) if columns[0] != '*' else f'{columns[0]}'
        conditions_string = "" if conditions is None else (
            "WHERE " + ' '.join([f'"{key}" = %s' for key in conditions.keys()]))
        parameters = tuple(value for value in conditions.values())

        # replace columns and conditions placeholder
        sql_template = sql_template.replace("columns", column_string)
        sql_template = sql_template.replace("conditions", conditions_string)
        sql_template = sql_template.strip()

        # format into sql string
        sql_string = sql.SQL(sql_template)

        # execute query
        print(f'Executing sql:\n{sql_string}')
        with self.conn.cursor() as cursor:
            try:
                # add collected parameters
                cursor.execute(sql_string, parameters)
            except psycopg.errors.Error as db_err:
                raise db_err
            except Exception as e:
                raise e

            results = cursor.fetchall()
            print(f'Retrieved {len(results)} rows.')

            return results

    def update_rows(self, table: str, columns: list[str] = None, conditions: dict[str, str] = None, rows: list[tuple] = None):
        if not rows:
            raise ValueError("There are no rows to insert.")

        # intial values
        sql_template = f'UPDATE "{self.db_name}"."public"."{table}" SET columns conditions'

        # construct columns and conditions strings plus collect values
        columns_string = "" if columns is None else ', '.join(
            [f'"{column}" = %s' for column in columns])
        conditions_string = "" if conditions is None else (
            "WHERE " + ' '.join([f'"{key}" = %s' for key in conditions.keys()]))
        values_string = ', '.join(f'%s' for i in range(len(columns)))

        # replace columns and values placeholder
        sql_template = sql_template.replace("columns", columns_string)
        sql_template = sql_template.replace("conditions", conditions_string)
        sql_template = sql_template.replace("values", values_string)
        sql_template = sql_template.strip()

        # format into sql string
        sql_string = sql.SQL(sql_template)

        print(f"Updating {len(rows)} rows into {table}.")
        with self.conn.cursor() as cursor:
            try:
                cursor.executemany(sql_string, rows)
                self.conn.commit()
            except psycopg.Error as e:
                self.conn.rollback()  # Rollback in case of error
                print("Error inserting rows.")
                raise e
