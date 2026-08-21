"""GoalService: CRUD mục tiêu tập luyện và tính % tiến độ hoàn thành."""

from models.goal import Goal
from validators.validator import Validator
from utils.helpers import generate_id, parse_date


class GoalService:
    def __init__(self, goal_json_manager, workout_service):
        self._goal_storage = goal_json_manager
        self._workout_service = workout_service

    def add_goal(
        self, user_id, sport_id, target_minutes, period, start_date, end_date
    ):
        if not Validator.validate_positive_number(target_minutes):
            raise ValueError("Mục tiêu (phút) phải là số dương.")

        if not Validator.validate_date(start_date):
            raise ValueError("Ngày bắt đầu không đúng định dạng.")

        if not Validator.validate_date(end_date):
            raise ValueError("Ngày kết thúc không đúng định dạng.")

        existing = self._goal_storage.read()
        new_id = generate_id("G", existing)

        goal = Goal(
            goal_id=new_id,
            user_id=user_id,
            sport_id=sport_id,
            target_minutes=float(target_minutes),
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

        self._goal_storage.add(goal.to_dict())
        return goal

    def update_goal(self, goal_id, new_values):
        current = self._goal_storage.find_by_id(goal_id)

        if current is None:
            raise ValueError(f"Không tìm thấy mục tiêu ID: {goal_id}")

        current.update(new_values)
        self._goal_storage.update(goal_id, current)
        return Goal.from_dict(current)

    def delete_goal(self, goal_id):
        self._goal_storage.delete(goal_id)

    def get_goals_by_user(self, user_id):
        data = self._goal_storage.read()
        return [
            Goal.from_dict(item)
            for item in data
            if item.get("user_id") == user_id
        ]

    def calculate_progress(self, goal):
        """Tính tổng phút đã tập trong khoảng thời gian của mục tiêu,
        rồi trả về % hoàn thành (dùng cho widget CircularProgress)."""

        workouts = self._workout_service.filter_by_date_range(
            goal.user_id, goal.start_date, goal.end_date
        )

        relevant = [w for w in workouts if w.sport_id == goal.sport_id]

        total_minutes = sum(w.duration_minutes for w in relevant)

        return goal.progress_percent(total_minutes), total_minutes
