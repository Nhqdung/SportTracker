"""Model Workout: một buổi tập cụ thể của người dùng."""


class Workout:
    def __init__(
        self,
        workout_id,
        user_id,
        sport_id,
        date,
        duration_minutes,
        calories_burned=0.0,
        note="",
    ):
        self._id = workout_id
        self.user_id = user_id
        self.sport_id = sport_id
        self.date = date
        self.duration_minutes = duration_minutes  # qua property để validate
        self.calories_burned = calories_burned
        self.note = note

    @property
    def id(self):
        return self._id

    @property
    def duration_minutes(self):
        return self._duration_minutes

    @duration_minutes.setter
    def duration_minutes(self, value):
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Thời lượng tập phải là số.") from error

        if number <= 0:
            raise ValueError("Thời lượng tập phải lớn hơn 0.")

        self._duration_minutes = number

    def to_dict(self):
        return {
            "id": self._id,
            "user_id": self.user_id,
            "sport_id": self.sport_id,
            "date": self.date,
            "duration_minutes": self._duration_minutes,
            "calories_burned": self.calories_burned,
            "note": self.note,
        }

    @staticmethod
    def from_dict(data):
        return Workout(
            workout_id=data.get("id"),
            user_id=data.get("user_id"),
            sport_id=data.get("sport_id"),
            date=data.get("date"),
            duration_minutes=data.get("duration_minutes", 0),
            calories_burned=data.get("calories_burned", 0.0),
            note=data.get("note", ""),
        )

    def __repr__(self):
        return f"<Workout {self._id} - {self.date} - {self._duration_minutes}p>"
