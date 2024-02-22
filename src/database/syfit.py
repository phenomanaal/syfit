from src.database import (
    common,
    user,
    measurement,
    routine,
    routine_day,
    routine_exercise,
    exercise_log,
    exercise,
)
from src import config


class Syfit(common.DatabaseInterface):
    def __init__(self, conn_string: str, reset_db: bool = False):
        super().__init__(conn_string, reset_db)
        self.user = user.Interface(conn_string)
        self.measurement = measurement.Interface(conn_string)
        self.routine = routine.Interface(conn_string)
        self.routine_day = routine_day.Interface(conn_string)
        self.routine_exercise = routine_exercise.Interface(conn_string)
        self.exercise_log = exercise_log.Interface(conn_string)
        self.exercise = exercise.Interface(conn_string)


def get_db():
    db = Syfit(config.config["DATABASE"]["CONN_STRING"])
    try:
        yield db
    finally:
        db.Session().close()
