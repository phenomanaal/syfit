from datetime import datetime, timedelta
import math
from sqlalchemy import and_
from src.database import common
from src.database.common import User
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TestUser:
    def test_add_user(self, db):
        pwd = password_context.hash("testpassword")
        user = User(
            first_name="Test",
            last_name="User",
            username="testuser2023",
            email="test@test.com",
            password=pwd,
            DOB=datetime.strptime("1/25/2023", "%m/%d/%Y").date(),
            measurement_system="imperial",
        )

        add_user = db.user.add_user(user)

        session = db.Session()

        get_user = (
            session.query(User)
            .filter(User.username == add_user.username)
            .first()
        )

        assert add_user.id == get_user.id
        assert add_user.first_name == get_user.first_name
        assert add_user.last_name == get_user.last_name
        assert add_user.username == get_user.username
        assert add_user.DOB == get_user.DOB
        assert add_user.last_updated_username == get_user.last_updated_username
        assert add_user.measurement_system == get_user.measurement_system

        session.close()        

    def test_add_duplicate_username(self, db):
        duplicate_user = User(
            first_name="NewTest",
            last_name="User",
            username="testuser2023",
            email="test@test.com",
            password="asdfasdfasdf",
            DOB=datetime.utcnow().date(),
            measurement_system="metric",
        )
        duplicate_user = db.user.add_user(duplicate_user)

        session = db.Session()

        get_user = (
            session.query(User)
            .filter(User.username == "testuser2023")
            .all()
        )

        assert isinstance(duplicate_user, dict)
        assert isinstance(duplicate_user.get("message"), str)
        assert len(get_user) == 1
        assert get_user[0].username == "testuser2023"
        assert get_user[0].first_name != "NewTest"

        session.commit()
        session.close()

    def test_get_all_users(self, db):
        users = db.user.get_all_users()

        assert len(users) == 1

        test_user = users[0]
        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"

    def test_get_user_by_id(self, db):
        test_user = db.user.get_user_by_id(1)

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"
        assert db.user.get_user_by_id(23424234) is None

    def test_get_user_by_username(self, db):
        test_user = db.user.get_user_by_username("testuser2023")

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"
        assert db.user.get_user_by_username("asdf") is None

    def test_change_username_by_id(self, db):
        user_ = db.user.change_username_by_id(1, "newusername23")

        session = db.Session()

        test_user = (
            session.query(User)
            .filter(User.username == "newusername23")
            .first()
        )

        user_ = session.query(User).filter(User.id == 1).first()

        session.close()

        assert test_user is None
        assert user_ is not None
        assert user_.username == "testuser2023"

    def test_set_user_for_deletion(self, db):
        ## TODO: adjust methods so that all associated data is also deleted
        ## TODO: create test that adjust the date to 1 minute from now and then test to see if user and all user data is deleted
        user_id = 1
        db.user.set_user_for_deletion(user_id)

        session = db.Session()
        test_user = session.query(User).filter(User.id == user_id).first()
        session.close()

        assert test_user.deletion_date.date() == (
            datetime.utcnow().date() + timedelta(days=45)
        )


class TestMeasurement:
    def test_add_measurement(self, db):
        session = db.Session()

        db.measurement.add_measurement(1, None, height=60, body_weight=125)

        test_measurement = (
            session.query(common.Measurement).filter(common.Measurement.id == 1).first()
        )

        assert test_measurement is not None
        assert test_measurement.height == 60
        assert test_measurement.body_weight == 125
        assert test_measurement.user_id == 1

    def test_get_all_measurements_by_user(self, db):
        user_id = 1

        db.measurement.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-120), body_weight=150
        )
        db.measurement.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-100), body_weight=145
        )
        db.measurement.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-80), body_weight=140
        )
        db.measurement.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-60), body_weight=135
        )
        db.measurement.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-30), body_weight=130
        )

        measurements = db.measurement.get_all_measurement_by_user(user_id)
        body_weights = [m.body_weight for m in measurements]

        session = db.Session()

        query_measurements = (
            session.query(common.Measurement)
            .filter(common.Measurement.user_id == user_id)
            .all()
        )
        query_body_weights = [m.body_weight for m in query_measurements]

        assert len(measurements) == len(query_measurements)
        assert max(body_weights) == max(query_body_weights)
        assert min(body_weights) == min(query_body_weights)

    def test_get_all_measurements_by_user_by_date(self, db):
        start_time = (datetime.utcnow() + timedelta(days=-120)).date()
        end_time = (datetime.utcnow() + timedelta(days=-59)).date()

        session = db.Session()

        measurements = db.measurement.get_all_measurements_by_user_by_date(
            1, start_time, end_time
        )

        query_measurements = (
            session.query(common.Measurement)
            .filter(common.Measurement.measurement_time >= start_time)
            .filter(common.Measurement.measurement_time < end_time)
            .all()
        )

        assert len(measurements) == len(query_measurements)

    def test_get_latest_measurement_by_user(self, db):
        latest = db.measurement.get_latest_measurement_by_user(1)

        measurement_times = [
            m.measurement_time for m in db.measurement.get_all_measurement_by_user(1)
        ]
        latest_query = max(measurement_times)

        assert latest.measurement_time == latest_query

    def test_get_measurement_by_measurement(self, db):
        session = db.Session()

        measurements = db.measurement.get_measurement_by_measurements(
            user_id=1, body_weight=125
        )

        assert len(measurements) == 1

        measurement = measurements[0]

        query_measurement = (
            session.query(common.Measurement)
            .filter(
                common.Measurement.user_id == 1, common.Measurement.body_weight == 125
            )
            .first()
        )

        assert measurement.user_id == query_measurement.id
        assert measurement.body_weight == query_measurement.body_weight
        assert measurement.height == query_measurement.height

        db.measurement.add_measurement(
            1, datetime.utcnow() + timedelta(days=30), body_weight=130
        )

        measurements = db.measurement.get_measurement_by_measurements(
            user_id=1, body_weight=130
        )

        assert len(measurements) == 2

    def test_get_measurement_by_id(self, db):
        session = db.Session()
        measurement = db.measurement.get_measurement_by_id(1)

        query_measurement = (
            session.query(common.Measurement).filter(common.Measurement.id == 1).first()
        )

        assert measurement.id == query_measurement.id
        assert measurement.user_id == query_measurement.user_id
        assert measurement.height == query_measurement.height
        assert measurement.body_weight == query_measurement.body_weight

    def test_edit_measurement(self, db):
        db.measurement.edit_measurement(
            7, measurement_time=datetime.utcnow() + timedelta(days=-10), body_weight=127
        )

        session = db.Session()

        query_measurement = (
            session.query(common.Measurement).filter(common.Measurement.id == 7).first()
        )

        assert query_measurement.body_weight == 127
        assert (
            query_measurement.measurement_time.date()
            == (datetime.utcnow() + timedelta(days=-10)).date()
        )

    def test_change_measurement_system(self, db):
        measurements = db.measurement.get_all_measurement_by_user(1)

        db.measurement.change_measurement_system(1, 1)
        db.measurement.change_measurement_system(1, 1)

        new_measurements = db.measurement.get_all_measurement_by_user(1)

        for m in measurements:
            new_measurement = [n for n in new_measurements if n.id == m.id]

            assert len(new_measurement) == 1
            new_measurement = new_measurement[0]

            assert new_measurement.id == m.id
            assert new_measurement.user_id == m.user_id
            assert (
                new_measurement.height == m.height
                or math.ceil(new_measurement.height) == m.height
                or math.floor(new_measurement.height) == m.height
            )
            assert (
                new_measurement.body_weight == m.body_weight
                or math.ceil(new_measurement.body_weight) == m.body_weight
                or math.floor(new_measurement.body_weight) == m.body_weight
            )


class TestRoutine:
    def test_add_routine(self, db):
        user_id = 1
        routine_name = "TEST ROUTINE"
        num_days = 4
        db.routine.add_routine(user_id, routine_name, num_days)

        session = db.Session()
        routine = (
            session.query(common.Routine).filter(common.Routine.user_id == 1).all()
        )

        assert len(routine) == 1

        routine = routine[0]

        assert routine.user_id == user_id
        assert routine.routine_name == routine_name
        assert routine.num_days == num_days
        assert routine.is_current is True

    def test_get_all_user_routines(self, db):
        routine = db.routine.get_all_user_routines(1)

        assert len(routine) == 1
        routine = routine[0]

        assert isinstance(routine, common.Routine)
        assert routine.user_id == 1
        assert routine.routine_name == "TEST ROUTINE"
        assert routine.num_days == 4

    def test_get_routine_by_id(self, db):
        routine = db.routine.get_routine_by_id(1)

        assert isinstance(routine, common.Routine)
        assert routine.user_id == 1
        assert routine.routine_name == "TEST ROUTINE"
        assert routine.num_days == 4

    def test_edit_routine(self, db):
        db.routine.edit_routine(1, routine_name="CHANGED ROUTINE NAME", num_days=5)

        routine = db.routine.get_routine_by_id(1)

        assert routine.user_id == 1
        assert routine.routine_name == "CHANGED ROUTINE NAME"
        assert routine.num_days == 5

    def test_make_routine_not_current(self, db):
        assert db.routine.get_routine_by_id(1).is_current is True

        db.routine.make_routine_not_current(1)

        routine = db.routine.get_routine_by_id(1)

        assert routine.is_current is False

    def test_make_routine_current(self, db):
        db.routine.add_routine(1, "NEW ROUTINE", 3)

        db.routine.make_routine_current(1)

        routine = db.routine.get_routine_by_id(1)
        new_routine = db.routine.get_routine_by_id(2)

        assert routine.is_current is True
        assert new_routine.is_current is False


class TestRoutineDay:
    def test_add_routine_day(self, db):
        db.routine_day.add_routine_day(1, "LEGS & GLUTES", "mon")
        db.routine_day.add_routine_day(1, "CHEST & ABS", "tue")
        db.routine_day.add_routine_day(1, "BACK & ARMS", "wed")
        db.routine_day.add_routine_day(1, "CARDIO", "thu")
        db.routine_day.add_routine_day(1, "LEGS & GLUTES", "fri")

        session = db.Session()

        days = (
            session.query(common.RoutineDay)
            .filter(common.RoutineDay.routine_id == 1)
            .all()
        )

        assert len(days) == 5

        test_legs = [d for d in days if d.routine_day_name == "LEGS & GLUTES"]
        assert len(test_legs) == 2

        test_cardio = [d for d in days if d.routine_day_name == "CARDIO"]
        assert len(test_cardio) == 1

        test_chest = [d for d in days if d.routine_day_name == "CHEST & ABS"]
        assert len(test_chest) == 1

        test_back = [d for d in days if d.routine_day_name == "BACK & ARMS"]
        assert len(test_back) == 1

    def test_get_routine_day_by_id(self, db):
        day = db.routine_day.get_routine_day_by_id(1)

        assert day.id == 1
        assert day.routine_id == 1
        assert day.routine_day_name == "LEGS & GLUTES"
        assert day.day_of_week == "mon"
        assert day.day_idx == 0

    def test_get_all_days_by_routine_id(self, db):
        days = db.routine_day.get_days_by_routine_id(1)

        assert len(days) == 5

        test_legs = [d for d in days if d.routine_day_name == "LEGS & GLUTES"]
        assert len(test_legs) == 2

        test_cardio = [d for d in days if d.routine_day_name == "CARDIO"]
        assert len(test_cardio) == 1

        test_chest = [d for d in days if d.routine_day_name == "CHEST & ABS"]
        assert len(test_chest) == 1

        test_back = [d for d in days if d.routine_day_name == "BACK & ARMS"]
        assert len(test_back) == 1

    def test_get_routine_day_by_idx(self, db):
        day = db.routine_day.get_routine_day_by_idx(1, 0)

        assert day.id == 1
        assert day.routine_id == 1
        assert day.routine_day_name == "LEGS & GLUTES"
        assert day.day_of_week == "mon"
        assert day.day_idx == 0

    def test_edit_routine_day(self, db):
        db.routine_day.edit_routine_day(
            1, routine_day_name="LEGS & BUTT", day_of_week="sun"
        )

        day = db.routine_day.get_routine_day_by_id(1)

        assert day.id == 1
        assert day.routine_id == 1
        assert day.routine_day_name == "LEGS & BUTT"
        assert day.day_of_week == "sun"
        assert day.day_idx == 0


class TestExercise:
    def test_add_exercise(self, db):
        exercise_name = "bodyweight squat"
        reference_link = "www.test.com"
        body_part = "upper_legs"
        secondary_body_part = "lower_legs"
        rep_type = "reps"

        db.exercise.add_exercise(
            exercise_name, reference_link, body_part, secondary_body_part, rep_type
        )

        session = db.Session()
        exercises = session.query(common.Exercise).all()

        assert len(exercises) == 1
        query_exercise = exercises[0]

        assert exercise_name == query_exercise.exercise_name
        assert reference_link == query_exercise.reference_link
        assert body_part == query_exercise.body_part
        assert secondary_body_part == query_exercise.secondary_body_part
        assert rep_type == query_exercise.rep_type

    def test_add_duplicate_exercise(self, db):
        exercise_name = "bodyweight squat"
        reference_link = "www.test.com"
        body_part = "upper_legs"
        secondary_body_part = "lower_legs"
        rep_type = "reps"

        duplicate_exercise = db.exercise.add_exercise(
            exercise_name, reference_link, body_part, secondary_body_part, rep_type
        )

        session = db.Session()
        exercises = (
            session.query(common.Exercise)
            .filter(common.Exercise.exercise_name == exercise_name)
            .all()
        )

        assert len(exercises) == 1
        assert isinstance(duplicate_exercise, str)

    def test_get_exercise_by_id(self, db):
        exercise = db.exercise.get_exercise_by_id(1)
        session = db.Session()
        query_exercise = (
            session.query(common.Exercise).filter(common.Exercise.id == 1).first()
        )

        assert exercise.id == query_exercise.id
        assert exercise.exercise_name == query_exercise.exercise_name
        assert exercise.reference_link == query_exercise.reference_link
        assert exercise.body_part == query_exercise.body_part
        assert exercise.secondary_body_part == query_exercise.secondary_body_part
        assert exercise.rep_type == query_exercise.rep_type

    def test_get_exercise_by_name(self, db):
        exercise = db.exercise.get_exercise_by_name("bodyweight squat")
        session = db.Session()
        query_exercise = (
            session.query(common.Exercise)
            .filter(common.Exercise.exercise_name == "bodyweight squat")
            .first()
        )

        assert exercise.id == query_exercise.id
        assert exercise.exercise_name == query_exercise.exercise_name
        assert exercise.reference_link == query_exercise.reference_link
        assert exercise.body_part == query_exercise.body_part
        assert exercise.secondary_body_part == query_exercise.secondary_body_part
        assert exercise.rep_type == query_exercise.rep_type

    def test_get_exercises_by_body_part(self, db):
        body_part = "upper_legs"
        secondary_body_part = "lower_legs"
        ref_link = "test.com"
        db.exercise.add_exercise(
            "barbell squat", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "bulgarian split squat", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "box squat", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "bodyweight lunge", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "leg press", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "sumo squat", ref_link, body_part, secondary_body_part, "reps"
        )

        body_part = "chest"
        secondary_body_part = "shoulders"
        db.exercise.add_exercise(
            "barbell bench press", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "incline bench press", ref_link, body_part, secondary_body_part, "reps"
        )
        db.exercise.add_exercise(
            "dumbbell bench press", ref_link, body_part, secondary_body_part, "reps"
        )

        body_part = "shoulders"
        secondary_body_part = "biceps"
        db.exercise.add_exercise(
            "dumbbell arnold press", ref_link, body_part, secondary_body_part, "reps"
        )
        secondary_body_part = "forearms"
        db.exercise.add_exercise(
            "dumbbell lateral raise", ref_link, body_part, secondary_body_part, "reps"
        )

        leg_exercises = db.exercise.get_exercises_by_body_part("upper_legs")
        chest_exercises = db.exercise.get_exercises_by_body_part("chest")
        shoulder_exercises = db.exercise.get_exercises_by_body_part("shoulders")
        bicep_exercises = db.exercise.get_exercises_by_body_part("biceps")
        forearm_exercises = db.exercise.get_exercises_by_body_part("forearms")

        assert len(leg_exercises) == 7
        assert len(chest_exercises) == 3
        assert len(shoulder_exercises) == 5
        assert len(bicep_exercises) == 1
        assert len(forearm_exercises) == 1

    def test_get_exercises_match_string(self, db):
        squats = db.exercise.get_exercises_match_string("squat")
        press = db.exercise.get_exercises_match_string("press")
        dumbbell = db.exercise.get_exercises_match_string("dumbbell")

        assert len(squats) == 5
        assert len(press) == 5
        assert len(dumbbell) == 3

    def test_edit_exercise(self, db):
        name = "edit me"
        ref_link = "delete.com"
        body_part = "forearms"
        secondary_body_part = None
        rep_type = "reps"

        old_exercise = db.exercise.add_exercise(
            name, ref_link, body_part, secondary_body_part, rep_type
        )

        new_name = "delete me"
        db.exercise.edit_exercise(old_exercise.id, exercise_name=new_name)

        exercise = db.exercise.get_exercise_by_name(new_name)

        assert db.exercise.get_exercise_by_name(name) is None
        assert exercise is not None
        assert exercise.id == old_exercise.id
        assert exercise.reference_link == ref_link
        assert exercise.body_part == body_part
        assert exercise.secondary_body_part == secondary_body_part
        assert exercise.rep_type == rep_type

    def test_get_user_created_exercise(self, db):
        name = "user created exercise"
        ref_link = "used.com"
        body_part = "core"
        secondary_body_part = "back"
        db.exercise.add_exercise(
            name, ref_link, body_part, secondary_body_part, "reps", 1
        )

        exercises = db.exercise.get_user_created_exercises(1)

        assert len(exercises) == 1


class TestRoutineExercise:
    def test_add_routine_exercise(self, db):
        e = db.routine_exercise.add_routine_exercise(day_id=1, exercise_id=1)

        assert e.exercise_idx == 0

        e = db.routine_exercise.add_routine_exercise(day_id=1, exercise_id=2)

        assert e.exercise_idx == 1

        e = db.routine_exercise.add_routine_exercise(
            day_id=1, exercise_id=3, num_sets=4, default_reps=12
        )

        assert e.exercise_idx == 2

        e = db.routine_exercise.add_routine_exercise(
            day_id=1, exercise_id=4, default_time=60
        )

        assert e.exercise_idx == 3

        session = db.Session()
        routine_exercises = (
            session.query(common.RoutineExercise)
            .filter(common.RoutineExercise.day_id == 1)
            .all()
        )
        session.close()

        assert len(routine_exercises) == 4

    def test_get_exercises_by_routine_day(self, db):
        exercises = db.routine_exercise.get_exercises_by_routine_day_id(1)
        ex_idxs = [e.exercise_idx for e in exercises]

        assert len(exercises) == 4
        assert list(set(ex_idxs)) == ex_idxs

    def test_get_routine_exercise_by_id(self, db):
        exercise = db.routine_exercise.get_routine_exercise_by_id(3)

        assert exercise.id == 3
        assert exercise.day_id == 1
        assert exercise.exercise_id == 3
        assert exercise.exercise_idx == 2
        assert exercise.num_sets == 4
        assert exercise.default_reps == 12
        assert exercise.default_time is None
        assert exercise.warmup_schema is None

    def test_get_routine_exercise_by_idx(self, db):
        exercise = db.routine_exercise.get_routine_exercise_by_idx(1, 2)
        assert exercise.id == 3
        assert exercise.day_id == 1
        assert exercise.exercise_id == 3
        assert exercise.exercise_idx == 2
        assert exercise.num_sets == 4
        assert exercise.default_reps == 12
        assert exercise.default_time is None
        assert exercise.warmup_schema is None

    def test_edit_routine_exercise(self, db):
        db.routine_exercise.edit_routine_exercise(3, num_sets=5)

        exercise = db.routine_exercise.get_routine_exercise_by_id(3)
        assert exercise.id == 3
        assert exercise.day_id == 1
        assert exercise.exercise_id == 3
        assert exercise.exercise_idx == 2
        assert exercise.num_sets == 5
        assert exercise.default_reps == 12
        assert exercise.default_time is None
        assert exercise.warmup_schema is None


class TestExerciseLog:
    def test_add_exercise_log(self, db):
        db.exercise_log.add_log(1, datetime.utcnow(), 10)
        db.exercise_log.add_log(1, datetime.utcnow(), 10)
        db.exercise_log.add_log(1, datetime.utcnow(), 10)

        session = db.Session()
        logs = (
            session.query(common.ExerciseLog)
            .filter(common.ExerciseLog.routine_exercise_id == 1)
            .all()
        )

        assert len(logs) == 3

    def test_get_exercise_logs_by_routine_exercise_id(self, db):
        logs = db.exercise_log.get_exercise_logs_by_routine_exercise_id(1)

        session = db.Session()

        query_logs = (
            session.query(common.ExerciseLog)
            .filter(common.ExerciseLog.routine_exercise_id == 1)
            .all()
        )

        assert len(logs) == len(query_logs)

    def test_get_exercise_log_by_id(self, db):
        log = db.exercise_log.get_exercise_log_by_id(1)

        session = db.Session()

        query_log = (
            session.query(common.ExerciseLog).filter(common.ExerciseLog.id == 1).first()
        )

        assert log.id == query_log.id
        assert log.routine_exercise_id == query_log.routine_exercise_id
        assert log.time_stamp == query_log.time_stamp
        assert log.set_idx == query_log.set_idx
        assert log.num_reps == query_log.num_reps
        assert log.time_duration == query_log.time_duration

    def test_get_exercise_log_by_set(self, db):
        log = db.exercise_log.get_exercise_log_by_set(1, 1)

        session = db.Session()
        query_log = (
            session.query(common.ExerciseLog)
            .filter(
                and_(
                    common.ExerciseLog.routine_exercise_id == 1,
                    common.ExerciseLog.set_idx == 1,
                )
            )
            .first()
        )

        assert log.id == query_log.id
        assert log.routine_exercise_id == query_log.routine_exercise_id
        assert log.time_stamp == query_log.time_stamp
        assert log.set_idx == query_log.set_idx
        assert log.num_reps == query_log.num_reps
        assert log.time_duration == query_log.time_duration

    def test_edit_exercise_log(self, db):
        db.exercise_log.edit_exercise_log(1, num_reps=9)

        log = db.exercise_log.get_exercise_log_by_id(1)

        assert log.num_reps == 9

    def test_get_exercise_log_by_routine_exercise(self, db):
        logs = db.exercise_log.get_exercise_logs_by_routine_exercise(1)
        for log in logs:
            assert log.routine_exercise_id == 1


class TestDelete:
    __test__ = False

    def test_delete_user(self, db):
        delete_user = db.user.add_user(
            "delete", "me", "delete_me", datetime.today().date(), "metric"
        )

        assert db.user.get_user_by_username("delete_me") is not None

        db.user.delete_user(delete_user.id)

        assert db.user.get_user_by_username("delete_me") is None

    def test_delete_measurements(self, db):
        db.measurement.delete_measurement(7)

        session = db.Session()

        query_measurements = (
            session.query(common.Measurement).filter(common.Measurement.id == 7).all()
        )

        assert len(query_measurements) == 0

    def test_delete_all_measurements_by_user(self, db):
        user_id = 1
        db.measurement.delete_all_measurements_by_user(user_id)

        session = db.Session()
        measurements = (
            session.query(common.Measurement)
            .filter(common.Measurement.user_id == user_id)
            .all()
        )

        assert len(measurements) == 0

    def test_delete_routine(self, db):
        db.routine.delete_routine(2)

        session = db.Session()

        routine = session.query(common.Routine).filter(common.Routine.id == 2).all()

        assert len(routine) == 0

    def test_delete_day_by_id(self, db):
        db.routine_day.delete_day_by_id(4)

        days = db.routine_day.get_days_by_routine_id(1)

        assert len(days) == 4

        for n, d in enumerate(days):
            assert n == d.day_idx

    def test_delete_days_by_routine_id(self, db):
        db.routine_day.delete_days_by_routine_id(1)

        session = db.Session()

        days = (
            session.query(common.RoutineDay)
            .filter(common.RoutineDay.routine_id == 1)
            .all()
        )

        assert len(days) == 0

        routine = session.query(common.Routine).filter(common.Routine.id == 1).all()

        assert len(routine) == 0

    def test_delete_exercise(self, db):
        exercise_id = db.exercise.get_exercise_by_name("delete me").id

        db.exercise.delete_exercise(exercise_id)

        session = db.Session()
        exercise = (
            session.query(common.Exercise)
            .filter(common.Exercise.id == exercise_id)
            .first()
        )

        assert exercise is None

        exercise = (
            session.query(common.Exercise)
            .filter(common.Exercise.exercise_name == "delete me")
            .first()
        )

        assert exercise is None

    def test_delete_exercise_by_id(self, db):
        db.routine_exercise.delete_exercise_by_id(3)
        exercises = db.routine_exercise.get_exercises_by_routine_day_id(1)

        assert len(exercises) == 3
        for n, d in enumerate(exercises):
            assert n == d.exercise_idx

    def test_delete_exercises_by_day_id(self, db):
        db.routine_exercise.delete_exercises_by_day_id(1)

        session = db.Session()

        exercises = (
            session.query(common.RoutineExercise)
            .filter(common.RoutineExercise.day_id == 1)
            .all()
        )

        assert len(exercises) == 0

        routine_day = (
            session.query(common.RoutineDay).filter(common.RoutineDay.id == 1).all()
        )

        assert len(routine_day) == 0

    def test_delete_exercises_by_routine_exercise_id(self, db):
        db.exercise_log.delete_exercises_by_routine_exercise_id(1)

        session = db.Session()

        logs = (
            session.query(common.ExerciseLog)
            .filter(common.ExerciseLog.routine_exercise_id == 1)
            .all()
        )

        assert len(logs) == 0

    def test_delete_exercise_log_by_id(self, db):
        num_logs_before = len(
            db.exercise_log.get_exercise_logs_by_routine_exercise_id(1)
        )
        db.exercise_log.delete_exercise_log_by_id(2)
        logs = db.exercise_log.get_exercise_logs_by_routine_exercise_id(1)

        assert len(logs) == num_logs_before - 1

        for n, log in enumerate(logs):
            assert log.set_idx == n
