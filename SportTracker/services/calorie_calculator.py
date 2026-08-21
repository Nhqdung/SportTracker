"""CalorieCalculator: điểm gọi trung tâm thể hiện tính đa hình.

Hàm calculate() nhận vào một đối tượng Sport (có thể là CardioSport,
StrengthSport hay FlexibilitySport) nhưng không cần biết nó là lớp con nào -
mỗi đối tượng tự biết cách tính calo của riêng mình khi calculate_calories()
được gọi (đa hình / polymorphism).
"""


class CalorieCalculator:

    @staticmethod
    def calculate(sport, weight_kg, duration_minutes, **kwargs):
        """Tính calo tiêu thụ dựa trên đối tượng Sport được truyền vào.

        sport: đối tượng Sport (hoặc lớp con) - lấy từ Sport.create(dict).
        weight_kg: cân nặng người tập.
        duration_minutes: thời lượng buổi tập.
        kwargs: tham số phụ tùy môn (VD: sets, reps cho StrengthSport).
        """

        if weight_kg is None or weight_kg <= 0:
            raise ValueError("Cân nặng phải lớn hơn 0 để tính calo.")

        if duration_minutes is None or duration_minutes <= 0:
            raise ValueError("Thời lượng phải lớn hơn 0 để tính calo.")

        # Cùng một lời gọi calculate_calories() nhưng kết quả và cách tính
        # sẽ khác nhau tùy theo sport thực sự là loại nào -> đa hình.
        return sport.calculate_calories(weight_kg, duration_minutes, **kwargs)
