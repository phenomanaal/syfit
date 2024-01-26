from typing import List
import enum
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
import config
from operator import itemgetter

Base = declarative_base()


class MeasurementSystemCheck(enum.Enum):
    imperial = "imperial"
    metric = "metric"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    username = Column(String(25), nullable=False)
    DOB = Column(DATE, nullable=False)
    last_updated_username = Column(TIMESTAMP)
    measurement_system = Column(
        String(10), Enum(MeasurementSystemCheck, create_constraint=True)
    )


class Measurement(Base):
    __tablename__ = "measurement"

    id = Column(Integer, Sequence("measurement_id_seq"), primary_key=True)
    measurement_time = Column(TIMESTAMP, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    height = Column(Float)
    body_weight = Column(Float)


class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer, Sequence("routine_id_seq"), primary_key=True)
    routine_name = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    num_days = Column(Integer)
    is_current = Column(Boolean)


class RoutineDay(Base):
    __tablename__ = "routine_day"

    id = Column(Integer, Sequence("routine_day_id_seq"), primary_key=True)
    routine_id = Column(Integer, ForeignKey("routine.id"), nullable=False)
    day_idx = Column(Integer)
    routine_day_name = Column(String(10))
    day_of_week = Column(String(3))


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, Sequence("exercise_id_seq"), primary_key=True)
    exercise_name = Column(String(100), nullable=False)
    reference_link = Column(String(255))
    body_part = Column(String(50))
    secondary_body_part = Column(String(50))
    rep_type = Column(String(4))


class RoutineExercise(Base):
    __tablename__ = "routine_exerise"

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
    routine_exercise_id = Column(
        Integer, ForeignKey("routine_exericse.id"), nullable=False
    )
    time_stamp = Column(TIMESTAMP, nullable=False)
    set_num = Column(Integer)
    num_reps = Column(Integer)
    time_duration = Column(Float)

db_url = ''.join([config.config.get('DATABASE', 'CONN_STRING'), config.config.get('DATABASE', 'DB_NAME')])

class DatabaseInterface:
    def __init__(self, connection_string: str = db_url):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)



    ## Measurement Methods



    ## Routine Methods



    ## Routine Days Methods




# Example usage:
if __name__ == "__main__":
    """ make sure database is empty, but initialized with init.sql when running test script """
