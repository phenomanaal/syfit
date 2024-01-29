from datetime import datetime, timedelta
from database.manage import db
from database.interface import user, syfit, measurement
import config

conn_string = config.config.get("DATABASE", "CONN_STRING")
db_name = config.config.get("DATABASE", "TEST_DB")

mng = db.DBManager(conn_string, db_name)
mng.delete_db()
mng.create_db()

test_url = "/".join([conn_string, db_name])
user_interface = user.Interface(test_url)
measurement_interface = measurement.Interface(test_url)


class TestUser:
    def test_add_user(self):
        add_user = user_interface.add_user(
            "Test",
            "User",
            "testuser2023",
            datetime.strptime("1/25/2023", "%m/%d/%Y").date(),
            "imperial",
        )

        session = user_interface.Session()
        get_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "testuser2023")
            .first()
        )

        assert add_user.id == get_user.id
        assert add_user.first_name == get_user.first_name
        assert add_user.last_name == get_user.last_name
        assert add_user.username == get_user.username
        assert add_user.DOB == get_user.DOB
        assert add_user.last_updated_username == get_user.last_updated_username
        assert add_user.measurement_system == get_user.measurement_system

    def test_add_duplicate_username(self):
        duplicate_user = user_interface.add_user(
            "NewTest", "User", "testuser2023", datetime.utcnow().date(), "metric"
        )

        session = user_interface.Session()

        get_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "testuser2023")
            .all()
        )

        assert isinstance(duplicate_user, str)
        assert len(get_user) == 1
        assert get_user[0].username == "testuser2023"
        assert get_user[0].first_name != "NewTest"

    def test_get_all_users(self):
        users = user_interface.get_all_users()

        assert len(users) == 1

        test_user = users[0]
        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"

    def test_get_user_by_id(self):
        test_user = user_interface.get_user_by_id(1)

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"
        assert user_interface.get_user_by_id(23424234) is None

    def test_get_user_by_username(self):
        test_user = user_interface.get_user_by_username("testuser2023")

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"
        assert user_interface.get_user_by_username("asdf") is None

    def test_delete_user(self):
        delete_user = user_interface.add_user(
            "delete", "me", "delete_me", datetime.today().date(), "metric"
        )

        assert user_interface.get_user_by_username("delete_me") is not None

        user_interface.delete_user(delete_user.id)

        assert user_interface.get_user_by_username("delete_me") is None

    def test_change_username_by_id(self):
        user_ = user_interface.change_username_by_id(1, "newusername23")

        session = user_interface.Session()

        test_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "newusername23")
            .first()
        )

        user_ = session.query(syfit.User).filter(syfit.User.id == 1).first()

        session.close()

        assert test_user is None
        assert user_ is not None
        assert user_.username == "testuser2023"

    def test_change_username_by_username(self):
        user_ = user_interface.change_username_by_username(
            "testuser2023", "newusername23"
        )

        session = user_interface.Session()

        test_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "newusername23")
            .first()
        )

        user_ = session.query(syfit.User).filter(syfit.User.id == 1).first()

        session.close()

        assert test_user is None
        assert user_ is not None
        assert user_.username == "testuser2023"

        # TODO: wait 24 hours from when testuser2023 was added and try again but this time assert that the username has changed


class TestMeasurement:
    def test_add_measurement(self):
        session = measurement_interface.Session()

        measurement_interface.add_measurement(1, None, height=60, body_weight=125)

        test_measurement = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 1).first()
        )

        assert test_measurement is not None
        assert test_measurement.height == 60
        assert test_measurement.body_weight == 125
        assert test_measurement.user_id == 1

    def test_get_all_measurements_by_user(self):
        user_id = 1

        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-120), body_weight=150
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-100), body_weight=145
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-80), body_weight=140
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-60), body_weight=135
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-30), body_weight=130
        )

        measurements = measurement_interface.get_all_measurement_by_user(user_id)
        body_weights = [m.body_weight for m in measurements]

        session = measurement_interface.Session()

        query_measurements = (
            session.query(syfit.Measurement)
            .filter(syfit.Measurement.user_id == user_id)
            .all()
        )
        query_body_weights = [m.body_weight for m in query_measurements]

        assert len(measurements) == len(query_measurements)
        assert max(body_weights) == max(query_body_weights)
        assert min(body_weights) == min(query_body_weights)

    def test_get_all_measurements_by_user_by_date(self):
        start_time = (datetime.utcnow() + timedelta(days=-120)).date()
        end_time = (datetime.utcnow() + timedelta(days=-59)).date()

        session = measurement_interface.Session()

        measurements = measurement_interface.get_all_measurements_by_user_by_date(
            1, start_time, end_time
        )

        query_measurements = (
            session.query(syfit.Measurement)
            .filter(syfit.Measurement.measurement_time >= start_time)
            .filter(syfit.Measurement.measurement_time < end_time)
            .all()
        )

        assert len(measurements) == len(query_measurements)

    def test_get_measurement_by_measurement(self):
        session = measurement_interface.Session()

        measurements = measurement_interface.get_measurement_by_measurements(
            user_id=1, body_weight=125
        )

        assert len(measurements) == 1

        measurement = measurements[0]

        query_measurement = (
            session.query(syfit.Measurement)
            .filter(
                syfit.Measurement.user_id == 1, syfit.Measurement.body_weight == 125
            )
            .first()
        )

        assert measurement.user_id == query_measurement.id
        assert measurement.body_weight == query_measurement.body_weight
        assert measurement.height == query_measurement.height

        measurement_interface.add_measurement(
            1, datetime.utcnow() + timedelta(days=30), body_weight=130
        )

        measurements = measurement_interface.get_measurement_by_measurements(
            user_id=1, body_weight=130
        )

        assert len(measurements) == 2

    def test_get_measurement_by_id(self):
        session = measurement_interface.Session()
        measurement = measurement_interface.get_measurement_by_id(1)

        query_measurement = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 1).first()
        )

        assert measurement.id == query_measurement.id
        assert measurement.user_id == query_measurement.user_id
        assert measurement.height == query_measurement.height
        assert measurement.body_weight == query_measurement.body_weight

    def test_edit_measurement(self):
        measurement_interface.edit_measurement(
            7, measurement_time=datetime.utcnow() + timedelta(days=-10), body_weight=127
        )

        session = measurement_interface.Session()

        query_measurement = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 7).first()
        )

        assert query_measurement.body_weight == 127
        assert (
            query_measurement.measurement_time.date()
            == (datetime.utcnow() + timedelta(days=-10)).date()
        )

    def test_change_measurement_system(self):
        measurements = measurement_interface.get_all_measurement_by_user(1)

        user_interface.change_measurement_system(1, 1)
        user_interface.change_measurement_system(1, 1)

        new_measurements = measurement_interface.get_all_measurement_by_user(1)

        for m in measurements:
            new_measurement = [n for n in new_measurements if n.id == m.id]

            assert len(new_measurement) == 1

            new_measurement = new_measurement[0]

            assert new_measurement.id == m.id
            assert new_measurement.user_id == m.user_id
            assert new_measurement.height == m.height
            assert new_measurement.body_weight == m.body_weight

    def test_delete_measurements(self):
        measurement_interface.delete_measurement(7)

        session = measurement_interface.Session()

        query_measurements = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 7).all()
        )

        assert len(query_measurements) == 0

    def test_delete_all_measurements_by_user(self):
        user_id = 1
        measurement_interface.delete_all_measurements_by_user(user_id)

        session = measurement_interface.Session()
        measurements = (
            session.query(syfit.Measurement)
            .filter(syfit.Measurement.user_id == user_id)
            .all()
        )

        assert len(measurements) == 0
