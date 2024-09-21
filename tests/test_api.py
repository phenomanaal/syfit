## reset test database
import json
from src.database import common
from src.config import config
from src.api.auth import get_token_data

class TestUser:
    def test_signup_admin(self, db, client):
        data = {
            "first_name": "Admin",
            "last_name": "User",
            "username": "admin",
            "email": "admin@syfit.com",
            "password": "adminadminadmin",
            "DOB": "1/1/2001",
            "measurement_system": "imperial",
        }

        headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "api_key": config["API"]["API_KEY"],
            }
        post_admin = client.post(
            "/users/signup",
            data=data,
            headers=headers,
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

    def test_signup_user(self, db, client):
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
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "api_key": config["API"]["API_KEY"],
            },
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

        assert post_user.status_code == 200
        assert user is not None
        assert token.id == user.id

    def test_signup_duplicate_user(self, db, client):
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
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "api_key": config["API"]["API_KEY"],
            },
        )
        assert post_user.status_code == 409
        error_msg = json.loads(post_user.text)
        assert (
            error_msg.get("detail")
            == f"username {data.get('username')} already exists!"
        )
