from typing import List
import enum
import os
from sqlalchemy import (
    create_engine,
    text,
    Column,
    Integer,
    Float,
    String,
    Sequence,
    ForeignKey,
    Boolean,
    TIMESTAMP,
    DATE,
    Enum,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import src.config as config
from operator import itemgetter

Base = declarative_base()


class MeasurementSystemCheck(enum.Enum):
    imperial = "imperial"
    metric = "metric"


class DayOfWeekCheck(enum.Enum):
    mon = "mon"
    tue = "tue"
    wed = "wed"
    thu = "thu"
    fri = "fri"
    sat = "sat"
    sun = "sun"


class BodyPartCheck(enum.Enum):
    triceps = "triceps"
    chest = "chest"
    shoulders = "shoulders"
    biceps = "biceps"
    core = "core"
    back = "back"
    forearms = "forearms"
    upper_legs = "upper_legs"
    glutes = "glutes"
    cardio = "cardio"
    lower_legs = "lower_legs"
    other = "other"


class RepTypeCheck(enum.Enum):
    reps = "reps"
    time = "time"


class User(Base):
    __tablename__ = "app_user"

    id = Column(Integer, Sequence("app_user_id_seq"), primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    username = Column(String(25), nullable=False, unique=True)
    DOB = Column(DATE, nullable=False)
    last_updated_username = Column(TIMESTAMP)
    measurement_system = Column(
        String(10), Enum(MeasurementSystemCheck, create_constraint=True)
    )


class Measurement(Base):
    __tablename__ = "measurement"

    id = Column(Integer, Sequence("measurement_id_seq"), primary_key=True)
    measurement_time = Column(TIMESTAMP, nullable=False)
    user_id = Column(Integer, ForeignKey("app_user.id"), nullable=False)
    height = Column(Float)
    body_weight = Column(Float)


class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer, Sequence("routine_id_seq"), primary_key=True)
    routine_name = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("app_user.id"))
    num_days = Column(Integer)
    is_current = Column(Boolean)


class RoutineDay(Base):
    __tablename__ = "routine_day"

    id = Column(Integer, Sequence("routine_day_id_seq"), primary_key=True)
    routine_id = Column(Integer, ForeignKey("routine.id"), nullable=False)
    day_idx = Column(Integer)
    routine_day_name = Column(String(10))
    day_of_week = Column(String(3), Enum(DayOfWeekCheck, create_constraint=True))


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, Sequence("exercise_id_seq"), primary_key=True)
    exercise_name = Column(String(100), nullable=False, unique=True)
    reference_link = Column(String(255))
    body_part = Column(String(50), Enum(BodyPartCheck, create_constraint=True))
    secondary_body_part = Column(
        String(50), Enum(BodyPartCheck, create_constraint=True)
    )
    rep_type = Column(String(4), Enum(RepTypeCheck, create_constraint=True))


class RoutineExercise(Base):
    __tablename__ = "routine_exercise"

    id = Column(Integer, Sequence("routine_exercise_id_seq"), primary_key=True)
    day_id = Column(Integer, ForeignKey("routine_day.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    exercise_idx = Column(Integer, nullable=False)
    num_sets = Column(Integer)
    default_reps = Column(Integer)
    default_time = Column(Float)


class ExerciseLog(Base):
    __tablename__ = "exercise_log"

    id = Column(Integer, Sequence("exercise_log_id_seq"), primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    routine_exercise_id = Column(
        Integer, ForeignKey("routine_exercise.id"), nullable=False
    )
    time_stamp = Column(TIMESTAMP, nullable=False)
    set_num = Column(Integer)
    num_reps = Column(Integer)
    time_duration = Column(Float)


class DatabaseInterface:
    def __init__(self, connection_string: str, restart_db: bool = False):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        if restart_db:
            self.restart_db()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def delete_db(self):
        os.remove(self.engine.url.database)

    def restart_db(self):
        self.delete_db()
        self.create_tables()


# Example usage:
if __name__ == "__main__":
    """make sure database is empty, but initialized with init.sql when running test script"""
