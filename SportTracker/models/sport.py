"""Model Sport: lớp cha và các lớp con thể hiện Kế thừa + Đa hình.

Mỗi môn tập là một đối tượng của Sport hoặc lớp con của nó.
Phương thức calculate_calories() được override khác nhau ở mỗi lớp con
-> khi gọi cùng một lời gọi hàm trên các đối tượng khác nhau,
kết quả tính toán sẽ khác nhau (đa hình - polymorphism).
"""

from utils.constants import (
    SPORT_TYPE_CARDIO,
    SPORT_TYPE_STRENGTH,
    SPORT_TYPE_FLEXIBILITY,
)


class Sport:
    """Lớp cha (abstract theo quy ước) đại diện cho một môn thể thao."""

    def __init__(self, sport_id, name, sport_type, met):
        self._id = sport_id
        self.name = name  # dùng qua property để validate
        self._sport_type = sport_type
        self._met = met

    # ---- Encapsulation: thuộc tính id chỉ đọc ----
    @property
    def id(self):
        return self._id

    # ---- Encapsulation: name có kiểm tra dữ liệu qua property ----
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or not str(value).strip():
            raise ValueError("Tên môn tập không được để trống.")
        self._name = str(value).strip()

    @property
    def sport_type(self):
        return self._sport_type

    @property
    def met(self):
        return self._met

    @met.setter
    def met(self, value):
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Hệ số MET phải là số.") from error

        if number <= 0:
            raise ValueError("Hệ số MET phải lớn hơn 0.")

        self._met = number

    def calculate_calories(self, weight_kg, duration_minutes, **kwargs):
        """Phương thức sẽ được các lớp con override (đa hình).

        Lớp cha không biết cách tính cụ thể -> báo lỗi nếu bị gọi trực tiếp.
        """

        raise NotImplementedError(
            "Lớp con của Sport phải cài đặt calculate_calories()."
        )

    def to_dict(self):
        return {
            "id": self._id,
            "name": self._name,
            "type": self._sport_type,
            "met": self._met,
        }

    @staticmethod
    def create(data):
        """Factory method: tạo đúng lớp con dựa trên trường 'type' trong JSON.

        Đây là nơi thể hiện đa hình khi đọc dữ liệu từ file:
        cùng một hàm create() nhưng trả về các kiểu đối tượng khác nhau.
        """

        sport_type = data.get("type", SPORT_TYPE_CARDIO)
        sport_id = data.get("id")
        name = data.get("name")
        met = data.get("met", 1.0)

        if sport_type == SPORT_TYPE_STRENGTH:
            return StrengthSport(sport_id, name, met)

        if sport_type == SPORT_TYPE_FLEXIBILITY:
            return FlexibilitySport(sport_id, name, met)

        return CardioSport(sport_id, name, met)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._id} - {self._name}>"


class CardioSport(Sport):
    """Môn tập Cardio (chạy bộ, đạp xe, nhảy dây...)."""

    def __init__(self, sport_id, name, met):
        super().__init__(sport_id, name, SPORT_TYPE_CARDIO, met)

    def calculate_calories(self, weight_kg, duration_minutes, **kwargs):
        """Công thức MET chuẩn: calo = MET * weight(kg) * time(giờ)."""

        hours = duration_minutes / 60
        calories = self.met * weight_kg * hours
        return round(calories, 2)


class StrengthSport(Sport):
    """Môn tập cử tạ / sức mạnh (có thể có số set, số rep)."""

    def __init__(self, sport_id, name, met):
        super().__init__(sport_id, name, SPORT_TYPE_STRENGTH, met)

    def calculate_calories(self, weight_kg, duration_minutes, **kwargs):
        """Cử tạ: dùng công thức MET nhưng cộng thêm hệ số theo số set.

        Nếu người dùng nhập sets/reps thì tính thêm hệ số cường độ,
        khác biệt rõ với công thức Cardio thuần theo thời gian.
        """

        hours = duration_minutes / 60
        base_calories = self.met * weight_kg * hours

        sets = kwargs.get("sets", 0)
        reps = kwargs.get("reps", 0)

        # Mỗi set*rep tăng thêm cường độ nhẹ so với chỉ tính theo thời gian
        intensity_bonus = sets * reps * 0.05

        calories = base_calories + intensity_bonus
        return round(calories, 2)


class FlexibilitySport(Sport):
    """Môn tập dẻo dai (yoga, giãn cơ...) - cường độ thấp hơn."""

    def __init__(self, sport_id, name, met):
        super().__init__(sport_id, name, SPORT_TYPE_FLEXIBILITY, met)

    def calculate_calories(self, weight_kg, duration_minutes, **kwargs):
        """Yoga/giãn cơ: MET thường thấp, không có hệ số phụ."""

        hours = duration_minutes / 60
        calories = self.met * weight_kg * hours * 0.9
        return round(calories, 2)
