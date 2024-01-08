from sqlalchemy import create_engine, Column, Integer, Float, String, Sequence, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    username = Column(String(25), nullable=False)
    DOB = Column(String(10), nullable=False)


class Measurement(Base):
    __tablename__ = 'measurement'

    id = Column(Integer, Sequence('measurement_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    height = Column(Float)
    height_units = Column(String(3))
    weight = Column(Float)
    weight_units = Column(String(3))


class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer, Sequence('routine_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    num_days = Column(Integer)
    is_current = Column(Boolean)


class RoutineDay(Base):
    __tablename__ = "routine_day"

    id = Column(Integer, Sequence('routine_day_id_seq'), primary_key=True)
    routine_id = Column(Integer, ForeignKey("routine.id"), nullable=False)
    day_idx = Column(Integer)
    routine_day_name = Column(String(10))
    day_of_week = Column(String(3))


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, Sequence('exercise_id_seq'), primary_key=True)
    exercise_name = Column(String(100), nullable=False)
    reference_link = Column(String(255))
    body_part = Column(String(50))
    secondary_body_part = Column(String(50))
    rep_type = Column(String(4))


class RoutineExercise(Base):
    __tablename__ = "routine_exerise"

    id = Column(Integer, Sequence('routine_exercise_id_seq'), primary_key=True)
    day_id = Column(Integer, ForeignKey("routine_day.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    exercise_idx = Column(Integer, nullable=False)
    num_sets = Column(Integer)
    default_reps = Column(Integer)
    default_time = Column(Float)


class ExerciseLog(Base):
    __tablename__ = "exercise_log"

    id = Column(Integer, Sequence('exercise_log_id_seq'), primary_key=True)
    routine_exercise_id = Column(
        Integer, ForeignKey("routine_exericse.id"), nullable=False)
    time_stamp = Column(TIMESTAMP, nullable=False)
    set_num = Column(Integer)
    num_reps = Column(Integer)
    time_duration = Column(Float)


class DatabaseInterface:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_user(self, first_name, last_name, username, DOB):
        user = User(first_name=first_name,
                    last_name=last_name, username=username, DOB=DOB)
        session = self.Session()
        session.add(user)

        try:
            session.commit()
        except IntegrityError as e:
            if 'duplicate' in e.args[0].lower():
                print(f"username '{e.params.get('username')}' already exists.")

        session.close()

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_by_id(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user

    def get_user_by_username(self, username):
        session = self.Session()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        return user

    def delete_user(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
        session.close()


# Example usage:
if __name__ == "__main__":
    # Update this with your MySQL connection details
    connection_string = config.config.get('DATABASE', 'CONN_STRING')

    db_interface = DatabaseInterface(connection_string)

    # Create tables (run this only once)
    db_interface.create_tables()

    # Add a user
    db_interface.add_user("John Doe", 25)

    # Get all users
    all_users = db_interface.get_all_users()
    print("All Users:", all_users)

    # Get user by ID
    user_by_id = db_interface.get_user_by_id(1)
    print("User by ID:", user_by_id)

    # Update user age
    db_interface.update_user_age(1, 30)

    # Delete user
    db_interface.delete_user(1)

    # Get all users after deletion
    all_users_after_deletion = db_interface.get_all_users()
    print("All Users After Deletion:", all_users_after_deletion)

if __name__ == "__main__":
    print(3)
