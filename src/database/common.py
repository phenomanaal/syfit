import os
from sqlalchemy import (
    create_engine,
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
    CheckConstraint,
)
from sqlalchemy.orm import sessionmaker, declarative_base, validates
import src.database.constraints as constraints
from src.database.utils import CountryCode

Base = declarative_base()


class User(Base):
    __tablename__ = "app_user"

    id = Column(Integer, Sequence("app_user_id_seq"), primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    username = Column(String(25), nullable=False, unique=True)
    tel_country = Column(String(2))
    tel = Column(String(15), unique=True)
    email = Column(String(200), nullable=False, unique=True)
    password = Column(
        String(200),
        nullable=False,
    )
    DOB = Column(DATE, nullable=False)
    last_updated_username = Column(TIMESTAMP)
    deletion_date = Column(TIMESTAMP)
    measurement_system = Column(
        String(10), Enum(constraints.MeasurementSystemCheck, create_constraint=True)
    )

    __table_args__ = (CheckConstraint("LENGTH(password) > 8", name="pwd_gt_8"),)

    @validates("password")
    def validate_password(self, _, password) -> str:
        if len(password) <= 8:
            raise ValueError("password too short")
        return password

    @validates("tel")
    def validate_tel(self, _, tel) -> str:
        if not tel.isdigit():
            raise ValueError("phone number must be all numeric!")
        return tel

    def to_model_dict(self):
        model_dict = self.__dict__
        model_dict["DOB"] = model_dict["DOB"].strftime("%Y-%m-%d")
        model_dict["password"] = None
        return model_dict


class TelCountryCode(Base):
    __tablename__ = "tel_country_code"

    id = Column(Integer, Sequence("tel_country_code_id_seq"), primary_key=True)
    name = Column(String(CountryCode().get_max_country_name_length()))
    short_name = Column(String(2))
    tele_code = Column(String(CountryCode().get_max_country_code_length()))

    @validates("name")
    def validate_name(self, _, name: str) -> str:
        if name not in CountryCode().get_all_country_names():
            raise ValueError("invalid country name")
        return name

    @validates("tele_code")
    def validate_name(self, _, tele_code: str) -> str:
        if tele_code not in CountryCode().get_all_country_codes():
            raise ValueError("invalid country code")
        return tele_code

    @validates("short_name")
    def validate_name(self, _, short_name) -> str:
        if short_name not in CountryCode().get_all_country_short_names():
            raise ValueError("invalid country short name")
        return short_name


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
    is_public = Column(Boolean)


class RoutineDay(Base):
    __tablename__ = "routine_day"

    id = Column(Integer, Sequence("routine_day_id_seq"), primary_key=True)
    routine_id = Column(Integer, ForeignKey("routine.id"), nullable=False)
    day_idx = Column(Integer)
    routine_day_name = Column(String(10))
    day_of_week = Column(
        String(3), Enum(constraints.DayOfWeekCheck, create_constraint=True)
    )


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, Sequence("exercise_id_seq"), primary_key=True)
    exercise_name = Column(String(100), nullable=False, unique=True)
    reference_link = Column(String(255))
    body_part = Column(
        String(50), Enum(constraints.BodyPartCheck, create_constraint=True)
    )
    secondary_body_part = Column(
        String(50), Enum(constraints.BodyPartCheck, create_constraint=True)
    )
    rep_type = Column(String(4), Enum(constraints.RepTypeCheck, create_constraint=True))
    user_id = Column(Integer, ForeignKey("app_user.id"))


class WarmUp(Base):
    __tablename__ = "warmup"

    id = Column(Integer, Sequence("warmup_id_seq"), primary_key=True)
    num_sets = Column(Integer)
    default_reps = Column(Integer)
    default_time = Column(Float)


class WarmUpSet(Base):
    __tablename__ = "warmup_set"

    id = Column(Integer, Sequence("warmup_set_id_seq"), primary_key=True)
    warmup_id = Column(Integer, ForeignKey("warmup.id"), nullable=False)
    set_idx = Column(Integer, nullable=False)
    num_reps = Column(Integer)
    time_duration = Column(Float)
    working_percentage = Column(Float)


class RoutineExercise(Base):
    __tablename__ = "routine_exercise"

    id = Column(Integer, Sequence("routine_exercise_id_seq"), primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    day_id = Column(Integer, ForeignKey("routine_day.id"), nullable=False)
    exercise_idx = Column(Integer, nullable=False)
    num_sets = Column(Integer)
    default_reps = Column(Integer)
    default_time = Column(Float)
    warmup_schema = Column(Integer, ForeignKey("warmup.id"))


class ExerciseLog(Base):
    __tablename__ = "exercise_log"

    id = Column(Integer, Sequence("exercise_log_id_seq"), primary_key=True)
    routine_exercise_id = Column(
        Integer, ForeignKey("routine_exercise.id"), nullable=False
    )
    time_stamp = Column(TIMESTAMP, nullable=False)
    set_idx = Column(Integer)
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
        if os.path.isfile(self.engine.url.database):
            os.remove(self.engine.url.database)

    def restart_db(self):
        self.delete_db()
        self.create_tables()

    def initialize_country_code_table(self):
        pass


# Example usage:
if __name__ == "__main__":
    """make sure database is empty, but initialized with init.sql when running test script"""
