from sqlalchemy import create_engine, text
import config
import os
import pathlib

class DBManager:
    def __init__(
        self,
        conn_string: str = config.config.get("DATABASE", "CONN_STRING"),
        script_name: str = "init.sql",
    ):
        self.script_name = script_name
        self.conn_string = conn_string
        self.engine = create_engine(conn_string)

    def init_db(self):

        script_path = pathlib.Path(__file__).resolve().parent / self.script_name

        with self.engine.connect() as con:
            with open(script_path) as file:
                query = text(file.read())
                con.execute(query)

        with open(script_path) as f:
            f = f.read()
        db_name = f.split('\n')[0].split(' ')[-1].replace(';','')

        self.engine = create_engine('/'.join([self.conn_string, db_name]))

    def delete_db(self, db_name: str = "syfit"):
        with self.engine.connect() as con:
            query = text(f"drop database if exists {db_name};")
            con.execute(query)
