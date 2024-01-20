from typing import List
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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import config

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    username = Column(String(25), nullable=False)
    DOB = Column(DATE, nullable=False)
    last_updated_username = Column(TIMESTAMP)


class Measurement(Base):
    __tablename__ = "measurement"

    id = Column(Integer, Sequence("measurement_id_seq"), primary_key=True)
    measurement_time = Column(TIMESTAMP, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    height = Column(Float)
    height_units = Column(String(3))
    body_weight = Column(Float)
    weight_units = Column(String(3))


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


class DatabaseInterface:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    ## User Methods

    def add_user(
        self, first_name: str, last_name: str, username: str, DOB: datetime
    ) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            DOB=DOB,
            last_updated_username=datetime.utcnow(),
        )
        session = self.Session()
        session.add(user)

        try:
            session.commit()
        except IntegrityError as e:
            if "duplicate" in e.args[0].lower():
                print(f"username '{e.params.get('username')}' already exists.")

        user = self.get_user_by_username(username)
        session.close()

        return user

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_by_id(self, user_id: int) -> User:
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user

    def get_user_by_username(self, username: str) -> User:
        session = self.Session()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        return user

    def delete_user(self, user_id: int) -> None:
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
        session.close()

    def change_username_by_id(self, user_id: int, new_username: str) -> User:
        session = self.Session()

        user = self.get_user_by_id(user_id)
        hours_since_username_change = (
            datetime.utcnow() - user.last_updated_username
        ).total_seconds() / (60**2)

        if hours_since_username_change > 24:
            user = (
                session.query(User)
                .filter(User.id == user_id)
                .update(
                    {
                        "username": new_username,
                        "last_updated_username": datetime.utcnow(),
                    }
                )
            )
            session.commit()

            user = self.get_user_by_id(user_id)
        else:
            user = {
                "message": "username was updated less than 24 hours ago. Please wait to update username again."
            }

        session.close()

        return user

    def change_username_by_username(self, username: str, new_username: str) -> User:
        session = self.Session()

        user = self.get_user_by_username(username)
        hours_since_username_change = (
            datetime.utcnow() - user.last_updated_username
        ).total_seconds() / (60**2)

        if hours_since_username_change > 24:
            user = (
                session.query(User)
                .filter(User.username == username)
                .update(
                    {
                        "username": new_username,
                        "last_updated_username": datetime.utcnow(),
                    }
                )
            )
            session.commit()

            user = self.get_user_by_username(username)

        else:
            user = {
                "message": "username was updated less than 24 hours ago. Please wait to update username again."
            }

        session.close()

        return user

    ## Measurement Methods

    def add_measurement(
        self, user_id: int, measurement_time: datetime = None, **kwargs
    ) -> Measurement:
        """
        TODO: insert functionality that determines
        if the same EXACT measurements were inputted
        within 24 hours, throw duplicate error
        TODO: create function that goes back and reads
        the latest valid units and updates all null values with it
        """

        if measurement_time is None or measurement_time > datetime.utcnow():
            measurement_time = datetime.utcnow()

        measurement = Measurement(
            measurement_time=measurement_time, user_id=user_id, **kwargs
        )

        session = self.Session()
        session.add(measurement)
        session.commit()
        id = measurement.id
        session.close()

        measurement = self.get_measurement_by_id(id)

        return measurement

    def get_measurement_by_id(self, measurement_id: int) -> Measurement:
        session = self.Session()
        measurement = (
            session.query(Measurement).filter(Measurement.id == measurement_id).first()
        )
        session.close()
        return measurement

    def get_all_measurement_by_user(self, user_id: int) -> List[Measurement]:
        """
        ## TODO: allow filtering by date
        """
        session = self.Session()
        measurements = (
            session.query(Measurement).filter(Measurement.user_id == user_id).all()
        )
        session.close()
        return measurements

    def edit_measurement(self, measurement_id: int, **kwargs) -> Measurement:
        session = self.Session()
        measurement_update = {
            k: v
            for k, v in kwargs.items()
            if k in Measurement.__table__.columns and "id" not in k
        }
        session.query(Measurement).filter(Measurement.id == measurement_id).update(
            measurement_update
        )
        session.commit()

        measurement = self.get_measurement_by_id(measurement_id)

        session.close()

        return measurement

    def delete_measurement(self, measurement_id: int) -> None:
        session = self.Session()
        measurement = self.get_measurement_by_id(measurement_id)

        if measurement:
            session.delete(measurement)
            session.commit()

        session.close()

    ## Routine Methods

    def add_routine(
        self, user_id: int, routine_name: str, num_days: int, is_current: bool = None
    ) -> Routine:
        any_routines = len(self.get_all_user_routines(user_id)) > 0

        if is_current is None:
            if not any_routines:
                is_current = True
            else:
                is_current = False

        routine = Routine(
            user_id=user_id,
            routine_name=routine_name,
            num_days=num_days,
            is_current=is_current,
        )

        session = self.Session()
        session.add(routine)
        session.commit()
        id = routine.id
        session.close()

        routine = self.get_routine_by_id(id)

        return routine

    def get_all_user_routines(self, user_id: int) -> List[Routine]:
        session = self.Session()
        routines = session.query(Routine).filter(Routine.user_id == user_id).all()
        session.close()

        return routines

    def get_routine_by_id(self, routine_id: int) -> Routine:
        session = self.Session()
        routine = session.query(Routine).filter(Routine.id == routine_id).first()
        session.close()

        return routine

    def edit_routine(self, routine_id: int, **kwargs):
        session = self.Session()
        routine_update = {
            k: v for k, v in kwargs.items() if k in ["routine_name", "num_days"]
        }
        session.query(Routine).filter(Routine.id == routine_id).update(routine_update)
        session.commit()

        routine = self.get_routine_by_id(routine_id)

        session.close()

        return routine

    def make_routine_not_current(self, routine_id: int) -> None:
        session = self.Session()
        session.query(Routine).filter(Routine.id == routine_id).update(
            {"is_current": False}
        )
        session.commit()
        routine = self.get_routine_by_id(routine_id)
        session.close()
        return routine

    def make_routine_current(self, routine_id: int):
        session = self.Session()
        routine = self.get_routine_by_id(routine_id)
        user_id = routine.user_id
        routine_ids = [
            r.id for r in self.get_all_user_routines(user_id) if r != routine_id
        ]

        for i in routine_ids:
            self.make_routine_not_current(i)

        session.query(Routine).filter(Routine.id == routine_id).update(
            {"is_current": True}
        )

        session.commit()
        session.close()

        routine = self.get_routine_by_id(routine_id)

        return routine

    def delete_routine(self, routine_id: int) -> None:
        """
        ## TODO: once routine_days are created go through and delete days
        """
        session = self.Session()
        routine = self.get_routine_by_id(routine_id)

        if routine:
            session.delete(routine)
            session.commit()

        session.close()

    ## Routine Days Methods

    def add_routine_day(
        self, routine_id: int, routine_day_name: str, day_of_week: str
    ):
        
        routine_days = self.get_days_by_routine_id(routine_id)
        day_idx = max([ d.day_idx for d in routine_days ]) + 1
        day = RoutineDay(
            routine_id=routine_id,
            day_idx=day_idx,
            routine_day_name=routine_day_name,
            day_of_week=day_of_week,
        )

        session = self.Session()
        session.add(day)
        session.commit()
        session.close()
        return day

    def get_days_by_routine_id(self, routine_id: int):
        session = self.Session()
        routine_days = (
            session.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).all()
        )
        session.close()

        return routine_days
    
    def reset_day_idxs(self, routine_id: int):
        routine_days = self.get_days_by_routine_id(routine_id)

        session = self.Session()

        for n, d in enumerate(routine_days):
            if d.day_idx != n:
                session.query(RoutineDay).filter(RoutineDay.id == d.id).update( { "day_idx": n } )
        session.commit()
        session.close()                
    
    def delete_day_by_id(self, day_id: int) -> None:

        session = self.Session()
        day = session.query(RoutineDay).filter(RoutineDay.id == day_id).first()
        if day:
            routine_id = day.routine_id
            session.delete(day)
            self.reset_day_idxs(routine_id)
            session.commit()
        session.close()

    def delete_days_by_routine_id(self, routine_id: int) -> None:

        session = self.Session()
        session.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).delete()
        session.commit()
        session.close()


# Example usage:
if __name__ == "__main__":
    print(3)
