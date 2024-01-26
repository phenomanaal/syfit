from datetime import datetime, timedelta
from typing import List
from database.interface.syfit import DatabaseInterface, Measurement


class Interface(DatabaseInterface):
    def add_measurement(
        self, user_id: int, measurement_time: datetime = None, **kwargs
    ) -> Measurement:
        """
        TODO: verify kwargs (maybe do on front end?)
        """

        if measurement_time is None or measurement_time > datetime.utcnow():
            measurement_time = datetime.utcnow()

        query_dict = {k: v for k, v in kwargs.items()}
        measurement = self.get_measurement_by_fields(user_id, **query_dict)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

        if measurement is not None:
            if measurement.measurement_time > (twenty_four_hours_ago):
                print(
                    "These exact measurements have been entered less than 24 hours ago."
                )

        if measurement is None or measurement.measurement_time > (
            twenty_four_hours_ago
        ):
            measurement = Measurement(
                measurement_time=measurement_time, user_id=user_id, **kwargs
            )

            session = self.Session()
            session.add(measurement)
            session.commit()
            id = measurement.id
            session.close()

            measurement = self.get_measurement_by_id(id)

        return measurement

    def get_measurement_by_fields(self, user_id: int, **kwargs) -> Measurement:
        session = self.Session()
        measurement = (
            session.query(Measurement)
            .filter(Measurement.id == 1)
            .filter_by(**kwargs)
            .first()
        )
        session.close()

        return measurement

    def get_measurement_by_id(self, measurement_id: int) -> Measurement:
        session = self.Session()
        measurement = (
            session.query(Measurement).filter(Measurement.id == measurement_id).first()
        )
        session.close()
        return measurement

    def get_all_measurement_by_user(self, user_id: int) -> List[Measurement]:
        session = self.Session()
        measurements = (
            session.query(Measurement).filter(Measurement.user_id == user_id).all()
        )
        session.close()
        return measurements

    def get_all_measurements_by_user_by_date(
        self, user_id: int, start_time: datetime, end_time: datetime = datetime.utcnow()
    ):
        session = self.Session()
        measurements = (
            session.query(Measurement)
            .filter(Measurement.user_id == user_id)
            .filter(Measurement.measurement_time >= start_time)
            .filter(Measurement.measurement_time <= end_time)
            .all()
        )
        session.close()
        return measurements

    def edit_measurement(self, measurement_id: int, **kwargs) -> Measurement:
        session = self.Session()
        measurement_update = {
            k: v
            for k, v in kwargs.items()
            if k in Measurement.__table__.columns and "id" not in k
        }
        session.query(Measurement).filter(Measurement.id == measurement_id).update(
            measurement_update
        )
        session.commit()

        measurement = self.get_measurement_by_id(measurement_id)

        session.close()

        return measurement

    def change_measurement_units(
        self, user_id: int, change_to: str
    ) -> List[Measurement]:
        measurements = self.get_all_measurement_by_user(user_id)
        session = self.Session()
        for m in measurements:
            update_keys = [
                k
                for k, v in m.__dict__.items()
                if v is not None
                and k not in ["measurement_time", "_sa_instance_state", "id", "user_id"]
            ]
            update_values = {k: v for k, v in m.__dict__.items() if k in update_keys}

            if change_to == "imperial":
                weight_convert = 2.20462262185
                length_convert = 0.39370079
            elif change_to == "metric":
                weight_convert = 0.45359237
                length_convert = 2.54
            else:
                raise ValueError

            for k, v in update_values.items():
                if k == "body_weight":
                    update_values[k] = v * weight_convert
                else:
                    update_values[k] = v * length_convert

            session.query(Measurement).filter(Measurement.id == m.id).update(
                update_values
            )

            session.commit()

        return self.get_all_measurement_by_user(user_id)

    def delete_measurement(self, measurement_id: int) -> None:
        session = self.Session()
        measurement = self.get_measurement_by_id(measurement_id)

        if measurement:
            session.delete(measurement)
            session.commit()

        session.close()
