"""GoalView: quản lý mục tiêu tập luyện - CRUD đầy đủ.

Mỗi mục tiêu gắn với 1 môn tập, có khoảng thời gian (từ ngày - đến ngày)
và số phút mục tiêu. Widget nâng cao: Treeview, Combobox, DateEntry,
CircularProgress (Custom Widget) để xem trước tiến độ khi chọn dòng.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from tkcalendar import DateEntry

from widgets.circular_progress import CircularProgress
from utils.constants import (
    COLOR_BACKGROUND,
    COLOR_PRIMARY,
    COLOR_DANGER,
    PERIOD_WEEKLY,
    PERIOD_MONTHLY,
)


class GoalView(tk.Frame):
    def __init__(self, parent, user, context):
        super().__init__(parent, bg=COLOR_BACKGROUND)

        self._user = user
        self._context = context
        self._selected_goal_id = None

        self._sport_name_to_id = {}
        self._sport_id_to_name = {}

        self._build_ui()
        self._load_sports()
        self._refresh_table()

    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_table()
        self._build_form()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_table(self):
        table_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 5), pady=15)

        columns = ("id", "sport", "target", "period", "start", "end", "percent")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=16
        )

        headings = {
            "id": "ID",
            "sport": "Môn tập",
            "target": "Mục tiêu (phút)",
            "period": "Chu kỳ",
            "start": "Từ ngày",
            "end": "Đến ngày",
            "percent": "Tiến độ",
        }
        widths = {
            "id": 55,
            "sport": 100,
            "target": 110,
            "period": 80,
            "start": 90,
            "end": 90,
            "percent": 70,
        }

        for col in columns:
            self._tree.heading(col, text=headings[col])
            self._tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._tree.bind("<<TreeviewSelect>>", self._on_select_row)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def _build_form(self):
        form_frame = tk.Frame(self, bg="white", padx=15, pady=15)
        form_frame.grid(row=0, column=1, sticky="n", padx=(5, 15), pady=15)

        tk.Label(
            form_frame, text="Thông tin mục tiêu", font=("Segoe UI", 12, "bold"), bg="white"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tk.Label(form_frame, text="Môn tập:", bg="white").grid(
            row=1, column=0, sticky="w", pady=6
        )
        self._form_sport_combo = ttk.Combobox(form_frame, state="readonly", width=18)
        self._form_sport_combo.grid(row=1, column=1, pady=6)

        tk.Label(form_frame, text="Mục tiêu (phút):", bg="white").grid(
            row=2, column=0, sticky="w", pady=6
        )
        self._form_target = tk.Entry(form_frame, width=20)
        self._form_target.grid(row=2, column=1, pady=6)

        tk.Label(form_frame, text="Chu kỳ:", bg="white").grid(
            row=3, column=0, sticky="w", pady=6
        )
        self._form_period = ttk.Combobox(
            form_frame,
            state="readonly",
            width=18,
            values=[PERIOD_WEEKLY, PERIOD_MONTHLY],
        )
        self._form_period.current(0)
        self._form_period.grid(row=3, column=1, pady=6)

        tk.Label(form_frame, text="Từ ngày:", bg="white").grid(
            row=4, column=0, sticky="w", pady=6
        )
        self._form_start_date = DateEntry(form_frame, date_pattern="dd/mm/yyyy", width=17)
        self._form_start_date.grid(row=4, column=1, pady=6)

        tk.Label(form_frame, text="Đến ngày:", bg="white").grid(
            row=5, column=0, sticky="w", pady=6
        )
        self._form_end_date = DateEntry(form_frame, date_pattern="dd/mm/yyyy", width=17)
        self._form_end_date.grid(row=5, column=1, pady=6)

        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(15, 10))

        tk.Button(
            btn_frame,
            text="Thêm mới",
            bg=COLOR_PRIMARY,
            fg="white",
            width=12,
            command=self._handle_add,
        ).grid(row=0, column=0, padx=4, pady=3)

        tk.Button(
            btn_frame, text="Cập nhật", width=12, command=self._handle_update
        ).grid(row=0, column=1, padx=4, pady=3)

        tk.Button(
            btn_frame,
            text="Xóa",
            bg=COLOR_DANGER,
            fg="white",
            width=12,
            command=self._handle_delete,
        ).grid(row=1, column=0, padx=4, pady=3)

        tk.Button(
            btn_frame, text="Làm mới form", width=12, command=self._clear_form
        ).grid(row=1, column=1, padx=4, pady=3)

        # Xem trước tiến độ bằng CircularProgress khi chọn 1 mục tiêu
        tk.Label(
            form_frame, text="Xem trước tiến độ", font=("Segoe UI", 10, "bold"), bg="white"
        ).grid(row=7, column=0, columnspan=2, pady=(10, 5))

        self._preview_progress = CircularProgress(
            form_frame, size=110, thickness=12, bg="white"
        )
        self._preview_progress.grid(row=8, column=0, columnspan=2)

    # ------------------------------------------------------------------
    def _load_sports(self):
        sports = self._context.sport_storage.read()

        self._sport_name_to_id = {}
        self._sport_id_to_name = {}

        for sport in sports:
            self._sport_name_to_id[sport["name"]] = sport["id"]
            self._sport_id_to_name[sport["id"]] = sport["name"]

        names = list(self._sport_name_to_id.keys())
        self._form_sport_combo["values"] = names

        if names:
            self._form_sport_combo.current(0)

    def _refresh_table(self):
        for row in self._tree.get_children():
            self._tree.delete(row)

        summary = self._context.statistic_service.goals_summary(self._user.id)

        for goal, percent, _current_minutes in summary:
            sport_name = self._sport_id_to_name.get(goal.sport_id, goal.sport_id)

            self._tree.insert(
                "",
                "end",
                iid=goal.id,
                values=(
                    goal.id,
                    sport_name,
                    goal.target_minutes,
                    goal.period,
                    goal.start_date,
                    goal.end_date,
                    f"{percent}%",
                ),
            )

        self._preview_progress.set_progress(0)

    # ------------------------------------------------------------------
    def _on_select_row(self, event):
        selected = self._tree.selection()

        if not selected:
            return

        goal_id = selected[0]
        values = self._tree.item(goal_id, "values")

        self._selected_goal_id = goal_id

        sport_name = values[1]
        if sport_name in self._sport_name_to_id:
            self._form_sport_combo.set(sport_name)

        self._form_target.delete(0, tk.END)
        self._form_target.insert(0, str(values[2]))

        self._form_period.set(values[3])

        self._form_start_date.set_date(_to_date_object(values[4]))
        self._form_end_date.set_date(_to_date_object(values[5]))

        percent_text = str(values[6]).replace("%", "")
        try:
            self._preview_progress.set_progress(float(percent_text))
        except ValueError:
            self._preview_progress.set_progress(0)

    def _clear_form(self):
        self._selected_goal_id = None
        self._tree.selection_remove(self._tree.selection())

        if self._form_sport_combo["values"]:
            self._form_sport_combo.current(0)

        self._form_target.delete(0, tk.END)
        self._form_period.current(0)
        self._preview_progress.set_progress(0)

    # ------------------------------------------------------------------
    def _handle_add(self):
        sport_name = self._form_sport_combo.get()

        if not sport_name:
            messagebox.showerror("Lỗi", "Vui lòng chọn môn tập.")
            return

        sport_id = self._sport_name_to_id.get(sport_name)
        target_text = self._form_target.get().strip()
        period = self._form_period.get()
        start_date = self._form_start_date.get()
        end_date = self._form_end_date.get()

        try:
            self._context.goal_service.add_goal(
                user_id=self._user.id,
                sport_id=sport_id,
                target_minutes=target_text,
                period=period,
                start_date=start_date,
                end_date=end_date,
            )
        except ValueError as error:
            messagebox.showerror("Không thể thêm mục tiêu", str(error))
            return

        messagebox.showinfo("Thành công", "Đã thêm mục tiêu mới.")
        self._clear_form()
        self._refresh_table()

    def _handle_update(self):
        if not self._selected_goal_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 mục tiêu trong bảng để sửa.")
            return

        sport_name = self._form_sport_combo.get()
        sport_id = self._sport_name_to_id.get(sport_name)

        new_values = {
            "sport_id": sport_id,
            "target_minutes": self._form_target.get().strip(),
            "period": self._form_period.get(),
            "start_date": self._form_start_date.get(),
            "end_date": self._form_end_date.get(),
        }

        try:
            self._context.goal_service.update_goal(self._selected_goal_id, new_values)
        except ValueError as error:
            messagebox.showerror("Không thể cập nhật", str(error))
            return

        messagebox.showinfo("Thành công", "Đã cập nhật mục tiêu.")
        self._clear_form()
        self._refresh_table()

    def _handle_delete(self):
        if not self._selected_goal_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 mục tiêu trong bảng để xóa.")
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa", "Bạn có chắc chắn muốn xóa mục tiêu này không?"
        )

        if not confirm:
            return

        self._context.goal_service.delete_goal(self._selected_goal_id)

        messagebox.showinfo("Thành công", "Đã xóa mục tiêu.")
        self._clear_form()
        self._refresh_table()


def _to_date_object(date_string):
    from datetime import datetime

    return datetime.strptime(date_string, "%d/%m/%Y").date()
