## reset test database
import requests
from src.database.syfit import Syfit
from src.database import common
import src.config as config

conn_string = config.config.get("DATABASE", "CONN_STRING")
db = Syfit(conn_string, reset_db=True)


class TestUser:
    def test_signup_admin(self):
        data = {
            "first_name": "Admin",
            "last_name": "User",
            "username": "admin",
            "email": "admin@syfit.com",
            "password": "adminadminadmin",
            "DOB": "1/1/2001",
            "measurement_system": "imperial",
        }
        post_admin = requests.post(
            "http://127.0.0.1:8000/users/signup",
            json=data,
            headers={"Content-Type": "application/json"},
        )

        session = db.Session()
        admin = (
            session.query(common.User)
            .filter(common.User.username == data["username"])
            .first()
        )
        session.close()

        assert admin is not None
        assert int(post_admin.content.decode()) == admin.id

    def test_signup_user(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser2023",
            "email": "test@test.com",
            "password": "test20242024",
            "DOB": "1/1/2001",
            "measurement_system": "imperial",
        }
        post_user = requests.post(
            "http://127.0.0.1:8000/users/signup",
            json=data,
            headers={"Content-Type": "application/json"},
        )

        session = db.Session()
        user = (
            session.query(common.User)
            .filter(common.User.username == data["username"])
            .first()
        )
        session.close()

        assert user is not None
        assert int(post_user.content.decode()) == user.id
