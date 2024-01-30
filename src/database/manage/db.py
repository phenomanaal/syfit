from sqlalchemy import create_engine, text
import src.config as config


class DBManager:
    def __init__(
        self,
        conn_string: str = config.config.get("DATABASE", "CONN_STRING"),
        db_name: str = config.config.get("DATABASE", "TEST_DB"),
    ):
        self.db_name = db_name
        self.engine = create_engine(conn_string)

    def create_db(self):
        init_script = config.config.get("DATABASE", "INIT_SCRIPT")

        with open(init_script, "r", newline="") as script_file:
            sql_script = script_file.read()

        sql_script = sql_script.format(self.db_name, self.db_name).replace("\n", "")
        statements = sql_script.split(";")
        statements = [";".join([s, ""]) for s in statements if len(s) > 1]

        with self.engine.connect() as connection:
            for s in statements:
                connection.execute(text(s))

    def delete_db(self):
        with self.engine.connect() as con:
            query = text(f"drop database if exists {self.db_name};")
            con.execute(query)
