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
            return user, {
                "message": "username was updated less than 24 hours ago. Please wait to update username again."
            }
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
            return user, {
                "message": "username was updated less than 24 hours ago. Please wait to update username again."
            }
        return user

    def add_measurement(
        self,
        user_id: int,
        height: float,
        height_units: str,
        body_weight: float,
        weight_units: str,
        measurement_time: datetime=None
    ) -> Measurement:
        '''
        TODO: insert functionality that determines
        if the same EXACT measurements were inputted
        within 24 hours, throw duplicate error
        '''

        if measurement_time is None or measurement_time > datetime.utcnow():
            measurement_time = datetime.utcnow()

        measurement = Measurement(
            measurement_time=measurement_time,
            user_id=user_id,
            height=height,
            height_units=height_units,
            body_weight=body_weight,
            weight_units=weight_units,
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
        measurement = session.query(Measurement).filter(Measurement.id == measurement_id).first()
        session.close()
        return measurement

# Example usage:
if __name__ == "__main__":
    print(3)
