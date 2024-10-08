from src.database.common import DatabaseInterface, User
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError


class Interface(DatabaseInterface):
    def add_user(self, user: User | None) -> User | dict[str, str]:
        user.last_updated_username = datetime.utcnow()

        session = self.Session()
        session.add(user)

        

        try:
            session.commit()
            user = self.get_user_by_username(user.username)
        except IntegrityError as e:
            session.rollback()
            session.close()
            if "UNIQUE constraint failed" in e.args[0]:
                return {"message": f"username {user.username} already exists!"}
        
        
        session.close()
        
        return user

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_by_id(self, user_id: int) -> User | None:
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user

    def get_user_by_username(self, username: str) -> User | None:
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

    def set_user_for_deletion(self, user_id: int) -> User:
        session = self.Session()
        session.query(User).filter(User.id == user_id).update(
            {"deletion_date": datetime.utcnow() + timedelta(days=45)}
        )
        session.commit()
        session.close()
        return self.get_user_by_id(user_id)

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
