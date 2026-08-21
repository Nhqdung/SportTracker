"""StatisticService: tổng hợp thống kê và xuất báo cáo CSV / TXT."""

import csv

from utils.helpers import today_string


class StatisticService:
    def __init__(self, workout_service, goal_service):
        self._workout_service = workout_service
        self._goal_service = goal_service

    def total_duration(self, user_id):
        """Tổng số phút đã tập của người dùng (tất cả buổi tập)."""

        workouts = self._workout_service.get_workouts_by_user(user_id)
        return sum(w.duration_minutes for w in workouts)

    def total_calories(self, user_id):
        workouts = self._workout_service.get_workouts_by_user(user_id)
        return sum(w.calories_burned for w in workouts)

    def goals_summary(self, user_id):
        """Trả về danh sách (goal, percent, current_minutes) cho mỗi mục tiêu."""

        goals = self._goal_service.get_goals_by_user(user_id)
        summary = []

        for goal in goals:
            percent, current_minutes = self._goal_service.calculate_progress(goal)
            summary.append((goal, percent, current_minutes))

        return summary

    def export_report_csv(self, file_path, user_id):
        """Xuất báo cáo buổi tập ra file CSV."""

        workouts = self._workout_service.get_workouts_by_user(user_id)

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["ID", "Ngày", "Môn tập", "Thời lượng (phút)", "Calo", "Ghi chú"]
                )

                for workout in workouts:
                    writer.writerow(
                        [
                            workout.id,
                            workout.date,
                            workout.sport_id,
                            workout.duration_minutes,
                            workout.calories_burned,
                            workout.note,
                        ]
                    )

        except OSError as error:
            raise OSError(f"Không thể ghi file báo cáo CSV: {error}") from error

    def export_report_txt(self, file_path, user_id):
        """Xuất báo cáo tổng hợp dạng văn bản (.txt)."""

        total_minutes = self.total_duration(user_id)
        total_cal = self.total_calories(user_id)
        summary = self.goals_summary(user_id)

        lines = []
        lines.append("BÁO CÁO TẬP LUYỆN")
        lines.append(f"Ngày xuất báo cáo: {today_string()}")
        lines.append(f"Người dùng: {user_id}")
        lines.append("-" * 40)
        lines.append(f"Tổng thời gian tập: {total_minutes} phút")
        lines.append(f"Tổng calo tiêu thụ: {total_cal} kcal")
        lines.append("-" * 40)
        lines.append("Tiến độ mục tiêu:")

        for goal, percent, current_minutes in summary:
            lines.append(
                f"  - {goal.id}: {current_minutes}/{goal.target_minutes} phút "
                f"({percent}%)"
            )

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(lines))

        except OSError as error:
            raise OSError(f"Không thể ghi file báo cáo TXT: {error}") from error
