"""AppContext: khởi tạo và giữ toàn bộ JsonManager + Service dùng chung.

Tạo 1 lần duy nhất khi ứng dụng khởi động, truyền xuống các cửa sổ GUI
để tránh mỗi màn hình tự tạo lại JsonManager (dễ gây lệch dữ liệu).
"""

from storage.json_manager import JsonManager
from services.auth_service import AuthService
from services.workout_service import WorkoutService
from services.goal_service import GoalService
from services.statistic_service import StatisticService
from services.body_metric_service import BodyMetricService

from utils.constants import (
    USERS_FILE,
    SPORTS_FILE,
    WORKOUTS_FILE,
    GOALS_FILE,
    BODY_METRICS_FILE,
    EXERCISES_FILE,
    EXERCISE_LIBRARY_FILE,
)


class AppContext:
    """Container chứa toàn bộ storage + service của ứng dụng."""

    def __init__(self):
        self.user_storage = JsonManager(USERS_FILE)
        self.sport_storage = JsonManager(SPORTS_FILE)
        self.workout_storage = JsonManager(WORKOUTS_FILE)
        self.goal_storage = JsonManager(GOALS_FILE)
        self.body_metric_storage = JsonManager(BODY_METRICS_FILE)
        self.exercise_storage = JsonManager(EXERCISES_FILE)
        self.exercise_library_storage = JsonManager(EXERCISE_LIBRARY_FILE)

        self.auth_service = AuthService(self.user_storage)
        self.workout_service = WorkoutService(self.workout_storage, self.sport_storage)
        self.goal_service = GoalService(self.goal_storage, self.workout_service)
        self.statistic_service = StatisticService(
            self.workout_service, self.goal_service
        )
        self.body_metric_service = BodyMetricService(self.body_metric_storage)
