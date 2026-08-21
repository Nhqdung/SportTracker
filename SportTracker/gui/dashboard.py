"""DashboardView: trang tổng quan sau khi đăng nhập.

Hiển thị thống kê tổng thời gian/calo và tiến độ từng mục tiêu
bằng Custom Widget CircularProgress.
"""

import tkinter as tk

from widgets.circular_progress import CircularProgress
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY


class DashboardView(tk.Frame):
    def __init__(self, parent, user, context):
        super().__init__(parent, bg=COLOR_BACKGROUND)

        self._user = user
        self._context = context

        self._build_ui()

    def _build_ui(self):
        """Toàn bộ layout trong frame này chỉ dùng grid()."""

        tk.Label(
            self,
            text="Tổng quan tập luyện",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_BACKGROUND,
            fg=COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ---- Thống kê tổng ----
        stats_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        stats_frame.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))

        total_minutes = self._context.statistic_service.total_duration(self._user.id)
        total_calories = self._context.statistic_service.total_calories(self._user.id)

        tk.Label(
            stats_frame,
            text=f"Tổng thời gian tập: {total_minutes:.0f} phút",
            font=("Segoe UI", 12),
            bg=COLOR_BACKGROUND,
        ).grid(row=0, column=0, sticky="w", pady=3)

        tk.Label(
            stats_frame,
            text=f"Tổng calo tiêu thụ: {total_calories:.0f} kcal",
            font=("Segoe UI", 12),
            bg=COLOR_BACKGROUND,
        ).grid(row=1, column=0, sticky="w", pady=3)

        # ---- Tiến độ mục tiêu (CircularProgress) ----
        tk.Label(
            self,
            text="Tiến độ mục tiêu",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_BACKGROUND,
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(5, 10))

        self._render_goals()

    def _render_goals(self):
        goals_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        goals_frame.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 20))

        summary = self._context.statistic_service.goals_summary(self._user.id)

        if not summary:
            tk.Label(
                goals_frame,
                text="Chưa có mục tiêu nào. Vào tab 'Mục tiêu' để tạo mới.",
                bg=COLOR_BACKGROUND,
                fg="gray",
            ).grid(row=0, column=0, sticky="w")
            return

        for index, (goal, percent, current_minutes) in enumerate(summary):
            card = tk.Frame(goals_frame, bg="white", padx=15, pady=15)
            card.grid(row=0, column=index, padx=10, sticky="n")

            progress = CircularProgress(card, size=110, thickness=12, bg="white")
            progress.grid(row=0, column=0)
            progress.set_progress(percent)

            tk.Label(
                card,
                text=f"{current_minutes:.0f}/{goal.target_minutes:.0f} phút",
                bg="white",
                font=("Segoe UI", 9),
            ).grid(row=1, column=0, pady=(8, 0))

            tk.Label(
                card,
                text=f"Chu kỳ: {goal.period}",
                bg="white",
                font=("Segoe UI", 8),
                fg="gray",
            ).grid(row=2, column=0)
