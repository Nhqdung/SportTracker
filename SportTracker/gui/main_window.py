"""MainWindow: cửa sổ chính sau khi đăng nhập thành công.

Dùng ttk.Notebook làm menu điều hướng dạng tab tới các view nghiệp vụ.
Tab "Quản trị" chỉ hiện với tài khoản role = admin (phân quyền).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from gui.dashboard import DashboardView
from gui.workout_view import WorkoutView
from gui.goal_view import GoalView
from gui.body_metric_view import BodyMetricView
from gui.exercise_view import ExerciseView
from gui.admin_view import AdminView
from utils.constants import COLOR_PRIMARY, COLOR_BACKGROUND


class MainWindow(tk.Tk):
    def __init__(self, user, context):
        super().__init__()

        self._user = user
        self._context = context

        self.title(f"SportTracker - {user.full_name}")
        self.geometry("950x650")
        self.configure(bg=COLOR_BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        # ---- Thanh trên cùng: dùng pack() riêng trong frame này ----
        top_bar = tk.Frame(self, bg=COLOR_PRIMARY, height=50)
        top_bar.pack(side="top", fill="x")

        role_label = "Quản trị viên" if self._user.is_admin() else "Người dùng"

        tk.Label(
            top_bar,
            text=f"Xin chào, {self._user.full_name}  ({role_label})",
            bg=COLOR_PRIMARY,
            fg="white",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", padx=15, pady=10)

        tk.Button(
            top_bar, text="Đăng xuất", command=self._logout, bg="white"
        ).pack(side="right", padx=15, pady=8)

        # ---- Notebook (menu tab) điều hướng tới từng view ----
        notebook = ttk.Notebook(self)
        notebook.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        dashboard_tab = DashboardView(notebook, self._user, self._context)
        notebook.add(dashboard_tab, text="Tổng quan")

        workout_tab = WorkoutView(notebook, self._user, self._context)
        notebook.add(workout_tab, text="Buổi tập")

        goal_tab = GoalView(notebook, self._user, self._context)
        notebook.add(goal_tab, text="Mục tiêu")

        body_tab = BodyMetricView(notebook, self._user, self._context)
        notebook.add(body_tab, text="Chỉ số cơ thể")

        exercise_tab = ExerciseView(notebook, self._user, self._context)
        notebook.add(exercise_tab, text="Bài tập")

        if self._user.is_admin():
            admin_tab = AdminView(notebook, self._user, self._context)
            notebook.add(admin_tab, text="Quản trị")

    def _placeholder_tab(self, parent, title):
        """Giữ lại để dự phòng cho các tab chưa hoàn thiện (hiện không còn dùng)."""

        frame = tk.Frame(parent, bg="white")

        tk.Label(
            frame,
            text=f"{title}\n\n(Sẽ hoàn thiện ở bước tiếp theo)",
            font=("Segoe UI", 12),
            bg="white",
            fg="gray",
        ).grid(row=0, column=0, padx=30, pady=30)

        return frame

    def _logout(self):
        if not messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            return

        self.destroy()

        from gui.login_window import LoginWindow

        LoginWindow().mainloop()
