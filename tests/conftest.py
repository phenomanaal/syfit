import pytest
from fastapi.testclient import TestClient
from src.database.syfit import Syfit
from src import config
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    yield TestClient(app)

@pytest.fixture(scope="module")
def db():
    """Fixture that resets the database before each test module."""
    # Initialize the Syfit database instance with reset_db=True to reset the database
    conn_string = config.config.get("DATABASE", "CONN_STRING")
    db = Syfit(conn_string, reset_db=True)

    # Return the db instance to be used in the tests
    yield db