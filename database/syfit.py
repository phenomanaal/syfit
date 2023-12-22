from sqlalchemy import create_engine, Column, Integer, Float, String, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25))
    username = Column(String(25), nullable=False)
    DOB = Column(String(10), nullable=False)


class Measurement(Base):
    __tablename__ = 'measurement'

    id = Column(Integer, Sequence('measurement_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    height = Column(Float)
    height_units = Column(String(3))
    weight = Column(Float)
    weight_units = Column(String(3))


class DatabaseInterface:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_user(self, name, age):
        user = User(name=name, age=age)
        session = self.Session()
        session.add(user)
        session.commit()
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

    def update_user_age(self, user_id, new_age):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.age = new_age
            session.commit()
        session.close()

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
