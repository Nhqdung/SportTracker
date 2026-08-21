"""WorkoutService: CRUD buổi tập, lọc theo môn/ngày, tính calo tự động."""

from models.workout import Workout
from models.sport import Sport
from services.calorie_calculator import CalorieCalculator
from validators.validator import Validator
from utils.helpers import generate_id, parse_date


class WorkoutService:
    def __init__(self, workout_json_manager, sport_json_manager):
        self._workout_storage = workout_json_manager
        self._sport_storage = sport_json_manager

    def _get_sport_object(self, sport_id):
        sport_data = self._sport_storage.find_by_id(sport_id)

        if sport_data is None:
            raise ValueError(f"Không tìm thấy môn tập có ID: {sport_id}")

        return Sport.create(sport_data)

    def add_workout(
        self,
        user_id,
        sport_id,
        date_string,
        duration_minutes,
        weight_kg,
        note="",
        **extra_params,
    ):
        """Thêm buổi tập mới, tự động tính calo theo đa hình của Sport."""

        if not Validator.validate_date(date_string):
            raise ValueError("Ngày không đúng định dạng dd/mm/yyyy.")

        if not Validator.validate_positive_number(duration_minutes):
            raise ValueError("Thời lượng tập phải là số dương.")

        sport = self._get_sport_object(sport_id)

        calories = CalorieCalculator.calculate(
            sport, float(weight_kg), float(duration_minutes), **extra_params
        )

        existing = self._workout_storage.read()
        new_id = generate_id("W", existing)

        workout = Workout(
            workout_id=new_id,
            user_id=user_id,
            sport_id=sport_id,
            date=date_string,
            duration_minutes=float(duration_minutes),
            calories_burned=calories,
            note=note,
        )

        self._workout_storage.add(workout.to_dict())
        return workout

    def update_workout(self, workout_id, new_values):
        """Cập nhật buổi tập (new_values là dict các trường cần đổi)."""

        current = self._workout_storage.find_by_id(workout_id)

        if current is None:
            raise ValueError(f"Không tìm thấy buổi tập ID: {workout_id}")

        current.update(new_values)

        # Nếu thời lượng hoặc môn tập thay đổi -> tính lại calo
        if "duration_minutes" in new_values or "sport_id" in new_values:
            if not Validator.validate_positive_number(current["duration_minutes"]):
                raise ValueError("Thời lượng tập phải là số dương.")

            sport = self._get_sport_object(current["sport_id"])
            weight_kg = new_values.get("weight_kg", 60)
            current["calories_burned"] = CalorieCalculator.calculate(
                sport, float(weight_kg), float(current["duration_minutes"])
            )

        self._workout_storage.update(workout_id, current)
        return Workout.from_dict(current)

    def delete_workout(self, workout_id):
        """Xóa buổi tập theo ID (xác nhận trước khi gọi phải xử lý ở GUI)."""
        self._workout_storage.delete(workout_id)

    def get_workouts_by_user(self, user_id):
        data = self._workout_storage.read()
        return [
            Workout.from_dict(item)
            for item in data
            if item.get("user_id") == user_id
        ]

    def filter_by_sport(self, user_id, sport_id):
        workouts = self.get_workouts_by_user(user_id)
        return [w for w in workouts if w.sport_id == sport_id]

    def filter_by_date_range(self, user_id, start_date_string, end_date_string):
        """Lọc buổi tập trong khoảng ngày [start, end] (dd/mm/yyyy)."""

        if not Validator.validate_date(start_date_string):
            raise ValueError("Ngày bắt đầu không đúng định dạng.")

        if not Validator.validate_date(end_date_string):
            raise ValueError("Ngày kết thúc không đúng định dạng.")

        start = parse_date(start_date_string)
        end = parse_date(end_date_string)

        workouts = self.get_workouts_by_user(user_id)
        result = []

        for workout in workouts:
            try:
                workout_date = parse_date(workout.date)
            except ValueError:
                continue

            if start <= workout_date <= end:
                result.append(workout)

        return result
