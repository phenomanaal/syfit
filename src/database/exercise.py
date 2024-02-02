from src.database.syfit import DatabaseInterface, Exercise
from sqlalchemy.exc import IntegrityError


class Interface(DatabaseInterface):

    def add_exercise(
        self,
        exercise_name: str,
        reference_link: str,
        body_part: str,
        secondary_body_part: str,
        rep_type: str,
    ):
        exercise = Exercise(
            exercise_name=exercise_name,
            reference_link=reference_link,
            body_part=body_part,
            secondary_body_part=secondary_body_part,
            rep_type=rep_type,
        )

        session = self.Session()
        session.add(exercise)

        try:
            session.commit()
        except IntegrityError as e:
            session.close()
            if 'UNIQUE constraint failed' in e.args[0]:
                return "exercise name already in the database"

        session.close()

    def get_exercise_by_id(self, exercise_id: str):
        session = self.Session()
        exercise = session.query(Exercise).filter(Exercise.id == exercise_id).first()
        session.close()
        return exercise

    def get_exercise_by_name(self, exercise_name: str):
        session = self.Session()
        exercise = (
            session.query(Exercise)
            .filter(Exercise.exercise_name == exercise_name)
            .first()
        )
        session.close()
        return exercise

    def get_exercises_by_body_part(self, body_part: str):
        session = self.Session()
        exercises = (
            session.query(Exercise)
            .filter(Exercise.body_part == body_part)
            .filter(Exercise.secondary_body_part == body_part)
            .all()
        )
        session.close()
        return exercises
    
    def get_exercises_match_string(self, search_string: str):
        session = self.Session()
        exercise = session.query(Exercise).filter(Exercise.exercise_name.contains(search_string)).all()
        session.close()
        return exercise
