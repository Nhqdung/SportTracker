"""Model Exercise: một bài tập cụ thể thuộc về một môn tập (Sport)."""


class Exercise:
    def __init__(self, exercise_id, name, sport_id, description="", equipment=None):
        self._id = exercise_id
        self.name = name
        self.sport_id = sport_id
        self.description = description
        self._equipment = equipment if equipment is not None else []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or not str(value).strip():
            raise ValueError("Tên bài tập không được để trống.")
        self._name = str(value).strip()

    @property
    def equipment(self):
        return list(self._equipment)

    def to_dict(self):
        return {
            "id": self._id,
            "name": self._name,
            "sport_id": self.sport_id,
            "description": self.description,
            "equipment": self._equipment,
        }

    @staticmethod
    def from_dict(data):
        return Exercise(
            exercise_id=data.get("id"),
            name=data.get("name"),
            sport_id=data.get("sport_id"),
            description=data.get("description", ""),
            equipment=data.get("equipment", []),
        )

    def __repr__(self):
        return f"<Exercise {self._id} - {self._name}>"
