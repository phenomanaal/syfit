## reset test database
import requests
import json
from fastapi.testclient import TestClient
from src.database.syfit import Syfit
from src.database import common
import src.config as config
from src.api.auth import get_token_data
from src.api.main import app

client = TestClient(app)

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
        post_admin = client.post(
            "/users/signup",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = get_token_data(
            json.loads(post_admin.content.decode()).get("access_token")
        )

        session = db.Session()
        admin = (
            session.query(common.User)
            .filter(common.User.username == data["username"])
            .first()
        )
        session.close()

        assert post_admin.status_code == 200
        assert admin is not None
        assert token.id == admin.id

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
        post_user = client.post(
            "/users/signup",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = get_token_data(
            json.loads(post_user.content.decode()).get("access_token")
        )

        session = db.Session()
        user = (
            session.query(common.User)
            .filter(common.User.username == data["username"])
            .first()
        )
        session.close()

        assert user is not None
        assert token.id == user.id

    def test_signup_duplicate_user(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser2023",
            "email": "test@test.com",
            "password": "test20242024",
            "DOB": "1/1/2001",
            "measurement_system": "imperial",
        }
        post_user = client.post(
            "/users/signup",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        post_user = json.loads(post_user.content.decode())
        assert (
            post_user.get("message")
            == f"username {data.get('username')} already exists!"
        )
