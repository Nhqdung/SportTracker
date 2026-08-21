"""Model BodyMetric: chỉ số cơ thể (cân nặng, chiều cao, BMI)."""


class BodyMetric:
    def __init__(self, metric_id, user_id, date, weight_kg, height_cm):
        self._id = metric_id
        self.user_id = user_id
        self.date = date
        self.weight_kg = weight_kg
        self.height_cm = height_cm

    @property
    def id(self):
        return self._id

    @property
    def weight_kg(self):
        return self._weight_kg

    @weight_kg.setter
    def weight_kg(self, value):
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Cân nặng phải là số.") from error

        if number <= 0:
            raise ValueError("Cân nặng phải lớn hơn 0.")

        self._weight_kg = number

    @property
    def height_cm(self):
        return self._height_cm

    @height_cm.setter
    def height_cm(self, value):
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Chiều cao phải là số.") from error

        if number <= 0:
            raise ValueError("Chiều cao phải lớn hơn 0.")

        self._height_cm = number

    @property
    def bmi(self):
        """BMI = cân nặng(kg) / (chiều cao(m))^2 - tính động, không lưu file."""

        height_m = self._height_cm / 100
        return round(self._weight_kg / (height_m ** 2), 2)

    def to_dict(self):
        return {
            "id": self._id,
            "user_id": self.user_id,
            "date": self.date,
            "weight_kg": self._weight_kg,
            "height_cm": self._height_cm,
        }

    @staticmethod
    def from_dict(data):
        return BodyMetric(
            metric_id=data.get("id"),
            user_id=data.get("user_id"),
            date=data.get("date"),
            weight_kg=data.get("weight_kg", 0),
            height_cm=data.get("height_cm", 0),
        )

    def __repr__(self):
        return f"<BodyMetric {self._id} - {self.date} - BMI={self.bmi}>"
