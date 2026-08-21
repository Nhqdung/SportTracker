"""File test nhanh - chạy thử models & services vừa thêm.

Cách chạy trong VS Code: mở file này, bấm nút Run (▷) góc trên phải,
hoặc chuột phải -> Run Python File in Terminal.

Sau khi test xong có thể xóa file này, không phải một phần chính thức
của ứng dụng.
"""

from storage.json_manager import JsonManager
from services.auth_service import AuthService
from services.workout_service import WorkoutService
from services.goal_service import GoalService
from services.statistic_service import StatisticService


def main():
    # Dùng file JSON riêng để test, không đụng vào data/ thật
    sport_storage = JsonManager("data/sports.json")
    user_storage = JsonManager("data/test_users.json")
    workout_storage = JsonManager("data/test_workouts.json")
    goal_storage = JsonManager("data/test_goals.json")

    auth = AuthService(user_storage)
    workout_service = WorkoutService(workout_storage, sport_storage)
    goal_service = GoalService(goal_storage, workout_service)
    stats = StatisticService(workout_service, goal_service)

    print("--- 1. Đăng ký & đăng nhập ---")
    user = auth.register(
        "testuser", "pass123", "Nguyen Van A", "a@test.com", "0912345678"
    )
    print("Đăng ký OK:", user)

    logged_in = auth.login("testuser", "pass123")
    print("Đăng nhập OK:", logged_in)

    print("\n--- 2. Thêm buổi tập (kiểm tra đa hình tính calo) ---")
    w1 = workout_service.add_workout(
        user.id, "S001", "21/08/2026", 30, weight_kg=65
    )
    print(f"Chạy bộ (cardio) 30 phút -> {w1.calories_burned} calo")

    w2 = workout_service.add_workout(
        user.id, "S003", "21/08/2026", 30, weight_kg=65, sets=4, reps=10
    )
    print(f"Cử tạ (strength) 30 phút, 4 set x 10 rep -> {w2.calories_burned} calo")

    print("\n--- 3. Mục tiêu & tiến độ ---")
    goal = goal_service.add_goal(
        user.id, "S001", 60, "weekly", "18/08/2026", "24/08/2026"
    )
    percent, minutes = goal_service.calculate_progress(goal)
    print(f"Mục tiêu chạy bộ: {minutes}/{goal.target_minutes} phút = {percent}%")

    print("\n--- 4. Xuất báo cáo ---")
    stats.export_report_csv("data/test_report.csv", user.id)
    stats.export_report_txt("data/test_report.txt", user.id)
    print("Đã xuất data/test_report.csv và data/test_report.txt")

    print("\n--- 5. Kiểm tra validation bắt lỗi ---")
    try:
        workout_service.add_workout(user.id, "S001", "ngay-sai", 30, weight_kg=65)
    except ValueError as error:
        print("Bắt lỗi đúng như mong đợi:", error)

    print("\n=== TẤT CẢ TEST ĐỀU PASS ===")


if __name__ == "__main__":
    main()
