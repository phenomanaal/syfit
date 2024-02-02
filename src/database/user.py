from src.database.syfit import DatabaseInterface, User
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class Interface(DatabaseInterface):
    def add_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        DOB: datetime,
        measurement_system: str,
    ) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            DOB=DOB,
            last_updated_username=datetime.utcnow(),
            measurement_system=measurement_system,
        )
        session = self.Session()
        session.add(user)

        try:
            session.commit()
        except IntegrityError as e:
            session.close()
            if 'UNIQUE constraint failed' in e.args[0]:
                return "duplicate username"

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
        user = self.get_user_by_id(user_id)
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
