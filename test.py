from datetime import datetime
from database.interface import user, syfit
class TestUser:
    def test_add_user(self):
        user_interface = user.Interface()
        add_user = user_interface.add_user('Test', 'User', 'testuser2023', datetime.strptime('1/25/2023', '%m/%d/%Y').date(), "imperial")

        session = user_interface.Session()
        get_user = session.query(syfit.User).filter(syfit.User.username == 'testuser2023').first()

        assert add_user.id == get_user.id
        assert add_user.first_name == get_user.first_name
        assert add_user.last_name == get_user.last_name
        assert add_user.username == get_user.username
        assert add_user.DOB == get_user.DOB
        assert add_user.last_updated_username == get_user.last_updated_username
        assert add_user.measurement_system == get_user.measurement_system

    def test_get_all_users(self):
        user_interface = user.Interface()
        users = user_interface.get_all_users()

        assert len(users) == 1

        test_user = users[0]
        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime('1/25/2023', '%m/%d/%Y').date()
        assert test_user.measurement_system == "imperial"

    def test_get_user_by_id(self):
        user_interface = user.Interface()
        test_user = user_interface.get_user_by_id(1)

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime('1/25/2023', '%m/%d/%Y').date()
        assert test_user.measurement_system == "imperial"
        assert user_interface.get_user_by_id(23424234) is None

    def test_get_user_by_username(self):
        user_interface = user.Interface()
        test_user = user_interface.get_user_by_username("testuser2023")

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime('1/25/2023', '%m/%d/%Y').date()
        assert test_user.measurement_system == "imperial"
        assert user_interface.get_user_by_username('asdf') is None

    def test_delete_user(self):
        user_interface = user.Interface()
        
        delete_user = user_interface.add_user('delete', 'me', 'delete_me', datetime.today().date(), "metric")

        assert user_interface.get_user_by_username("delete_me") is not None

        user_interface.delete_user(delete_user.id)

        assert user_interface.get_user_by_username("delete_me") is None

