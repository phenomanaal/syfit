from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import config
import subprocess
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

    def delete_db(self, db_name: str = "syfit"):
        with self.engine.connect() as con:
            query = text(f"drop database if exists {db_name};")
            con.execute(query)
