"""WorkoutView: quản lý buổi tập - CRUD đầy đủ + lọc theo môn/ngày.

Widget nâng cao dùng: Treeview (danh sách), Combobox (chọn môn tập),
tkcalendar.DateEntry (chọn ngày), Messagebox (xác nhận xóa, báo lỗi).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from tkcalendar import DateEntry

from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_DANGER


class WorkoutView(tk.Frame):
    def __init__(self, parent, user, context):
        super().__init__(parent, bg=COLOR_BACKGROUND)

        self._user = user
        self._context = context
        self._selected_workout_id = None

        # sport_id -> tên môn tập, dùng để hiển thị & tra cứu ngược
        self._sport_name_to_id = {}
        self._sport_id_to_name = {}

        self._build_ui()
        self._load_sports()
        self._refresh_table()

    # ------------------------------------------------------------------
    # Xây dựng giao diện
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Layout tổng: mỗi frame con chỉ dùng 1 loại geometry manager."""

        self._build_filter_bar()
        self._build_table()
        self._build_form()

    def _build_filter_bar(self):
        """Thanh lọc - dùng grid() riêng trong frame này."""

        filter_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        filter_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=10)

        tk.Label(filter_frame, text="Môn tập:", bg=COLOR_BACKGROUND).grid(
            row=0, column=0, padx=(0, 5)
        )
        self._filter_sport_combo = ttk.Combobox(
            filter_frame, state="readonly", width=15
        )
        self._filter_sport_combo.grid(row=0, column=1, padx=(0, 15))

        tk.Label(filter_frame, text="Từ ngày:", bg=COLOR_BACKGROUND).grid(
            row=0, column=2, padx=(0, 5)
        )
        self._filter_start_date = DateEntry(
            filter_frame, date_pattern="dd/mm/yyyy", width=12
        )
        self._filter_start_date.grid(row=0, column=3, padx=(0, 15))

        tk.Label(filter_frame, text="Đến ngày:", bg=COLOR_BACKGROUND).grid(
            row=0, column=4, padx=(0, 5)
        )
        self._filter_end_date = DateEntry(
            filter_frame, date_pattern="dd/mm/yyyy", width=12
        )
        self._filter_end_date.grid(row=0, column=5, padx=(0, 15))

        tk.Button(
            filter_frame, text="Lọc theo ngày", command=self._apply_date_filter
        ).grid(row=0, column=6, padx=(0, 8))

        tk.Button(
            filter_frame, text="Xem tất cả", command=self._refresh_table
        ).grid(row=0, column=7)

    def _build_table(self):
        """Bảng danh sách buổi tập (Treeview) + thanh cuộn."""

        table_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=5)

        columns = ("id", "date", "sport", "duration", "calories", "note")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=16
        )

        headings = {
            "id": "ID",
            "date": "Ngày",
            "sport": "Môn tập",
            "duration": "Thời lượng (phút)",
            "calories": "Calo",
            "note": "Ghi chú",
        }
        widths = {
            "id": 60,
            "date": 90,
            "sport": 110,
            "duration": 120,
            "calories": 80,
            "note": 160,
        }

        for col in columns:
            self._tree.heading(col, text=headings[col])
            self._tree.column(col, width=widths[col], anchor="center")

        self._tree.column("note", anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._tree.bind("<<TreeviewSelect>>", self._on_select_row)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_form(self):
        """Form Thêm/Sửa/Xóa buổi tập - dùng grid() riêng."""

        form_frame = tk.Frame(self, bg="white", padx=15, pady=15)
        form_frame.grid(row=1, column=1, sticky="n", padx=(5, 15), pady=5)

        tk.Label(
            form_frame, text="Thông tin buổi tập", font=("Segoe UI", 12, "bold"), bg="white"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tk.Label(form_frame, text="Môn tập:", bg="white").grid(
            row=1, column=0, sticky="w", pady=6
        )
        self._form_sport_combo = ttk.Combobox(form_frame, state="readonly", width=18)
        self._form_sport_combo.grid(row=1, column=1, pady=6)

        tk.Label(form_frame, text="Ngày tập:", bg="white").grid(
            row=2, column=0, sticky="w", pady=6
        )
        self._form_date = DateEntry(form_frame, date_pattern="dd/mm/yyyy", width=17)
        self._form_date.grid(row=2, column=1, pady=6)

        tk.Label(form_frame, text="Thời lượng (phút):", bg="white").grid(
            row=3, column=0, sticky="w", pady=6
        )
        self._form_duration = tk.Entry(form_frame, width=20)
        self._form_duration.grid(row=3, column=1, pady=6)

        tk.Label(form_frame, text="Cân nặng (kg):", bg="white").grid(
            row=4, column=0, sticky="w", pady=6
        )
        self._form_weight = tk.Entry(form_frame, width=20)
        self._form_weight.grid(row=4, column=1, pady=6)

        tk.Label(form_frame, text="Số set (nếu cử tạ):", bg="white").grid(
            row=5, column=0, sticky="w", pady=6
        )
        self._form_sets = tk.Entry(form_frame, width=20)
        self._form_sets.grid(row=5, column=1, pady=6)

        tk.Label(form_frame, text="Số rep (nếu cử tạ):", bg="white").grid(
            row=6, column=0, sticky="w", pady=6
        )
        self._form_reps = tk.Entry(form_frame, width=20)
        self._form_reps.grid(row=6, column=1, pady=6)

        tk.Label(form_frame, text="Ghi chú:", bg="white").grid(
            row=7, column=0, sticky="w", pady=6
        )
        self._form_note = tk.Entry(form_frame, width=20)
        self._form_note.grid(row=7, column=1, pady=6)

        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(15, 0))

        tk.Button(
            btn_frame,
            text="Thêm mới",
            bg=COLOR_PRIMARY,
            fg="white",
            width=12,
            command=self._handle_add,
        ).grid(row=0, column=0, padx=4, pady=3)

        tk.Button(
            btn_frame,
            text="Cập nhật",
            width=12,
            command=self._handle_update,
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
            btn_frame,
            text="Làm mới form",
            width=12,
            command=self._clear_form,
        ).grid(row=1, column=1, padx=4, pady=3)

    # ------------------------------------------------------------------
    # Dữ liệu môn tập cho Combobox
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
        self._filter_sport_combo["values"] = ["Tất cả"] + names
        self._filter_sport_combo.set("Tất cả")

        if names:
            self._form_sport_combo.current(0)

    # ------------------------------------------------------------------
    # Nạp / lọc dữ liệu bảng
    # ------------------------------------------------------------------
    def _refresh_table(self):
        workouts = self._context.workout_service.get_workouts_by_user(self._user.id)
        self._populate_table(workouts)

    def _apply_date_filter(self):
        start_date = self._filter_start_date.get()
        end_date = self._filter_end_date.get()

        try:
            workouts = self._context.workout_service.filter_by_date_range(
                self._user.id, start_date, end_date
            )
        except ValueError as error:
            messagebox.showerror("Lỗi lọc", str(error))
            return

        sport_name = self._filter_sport_combo.get()

        if sport_name and sport_name != "Tất cả":
            sport_id = self._sport_name_to_id.get(sport_name)
            workouts = [w for w in workouts if w.sport_id == sport_id]

        self._populate_table(workouts)

    def _populate_table(self, workouts):
        for row in self._tree.get_children():
            self._tree.delete(row)

        for workout in workouts:
            sport_name = self._sport_id_to_name.get(workout.sport_id, workout.sport_id)

            self._tree.insert(
                "",
                "end",
                iid=workout.id,
                values=(
                    workout.id,
                    workout.date,
                    sport_name,
                    workout.duration_minutes,
                    workout.calories_burned,
                    workout.note,
                ),
            )

    # ------------------------------------------------------------------
    # Chọn dòng -> đổ dữ liệu vào form để sửa
    # ------------------------------------------------------------------
    def _on_select_row(self, event):
        selected = self._tree.selection()

        if not selected:
            return

        workout_id = selected[0]
        values = self._tree.item(workout_id, "values")

        self._selected_workout_id = workout_id

        sport_name = values[2]

        if sport_name in self._sport_name_to_id:
            self._form_sport_combo.set(sport_name)

        self._form_date.set_date(_to_date_object(values[1]))

        self._form_duration.delete(0, tk.END)
        self._form_duration.insert(0, str(values[3]))

        self._form_note.delete(0, tk.END)
        self._form_note.insert(0, values[5])

        # Cân nặng, set, rep không lưu trong Workout -> để trống, người dùng
        # nhập lại nếu muốn tính lại calo khi cập nhật.
        self._form_weight.delete(0, tk.END)
        self._form_sets.delete(0, tk.END)
        self._form_reps.delete(0, tk.END)

    def _clear_form(self):
        self._selected_workout_id = None
        self._tree.selection_remove(self._tree.selection())

        if self._form_sport_combo["values"]:
            self._form_sport_combo.current(0)

        self._form_duration.delete(0, tk.END)
        self._form_weight.delete(0, tk.END)
        self._form_sets.delete(0, tk.END)
        self._form_reps.delete(0, tk.END)
        self._form_note.delete(0, tk.END)

    # ------------------------------------------------------------------
    # CRUD - Thêm / Sửa / Xóa
    # ------------------------------------------------------------------
    def _read_extra_params(self):
        """Đọc sets/reps từ form nếu người dùng có nhập (dùng cho cử tạ)."""

        extra = {}

        sets_text = self._form_sets.get().strip()
        reps_text = self._form_reps.get().strip()

        if sets_text:
            try:
                extra["sets"] = int(sets_text)
            except ValueError:
                raise ValueError("Số set phải là số nguyên.")

        if reps_text:
            try:
                extra["reps"] = int(reps_text)
            except ValueError:
                raise ValueError("Số rep phải là số nguyên.")

        return extra

    def _handle_add(self):
        sport_name = self._form_sport_combo.get()

        if not sport_name:
            messagebox.showerror("Lỗi", "Vui lòng chọn môn tập.")
            return

        sport_id = self._sport_name_to_id.get(sport_name)
        date_string = self._form_date.get()
        duration_text = self._form_duration.get().strip()
        weight_text = self._form_weight.get().strip()
        note = self._form_note.get().strip()

        if not weight_text:
            messagebox.showerror("Lỗi", "Vui lòng nhập cân nặng để tính calo.")
            return

        try:
            weight_kg = float(weight_text)
            extra_params = self._read_extra_params()

            self._context.workout_service.add_workout(
                user_id=self._user.id,
                sport_id=sport_id,
                date_string=date_string,
                duration_minutes=duration_text,
                weight_kg=weight_kg,
                note=note,
                **extra_params,
            )
        except ValueError as error:
            messagebox.showerror("Không thể thêm buổi tập", str(error))
            return

        messagebox.showinfo("Thành công", "Đã thêm buổi tập mới.")
        self._clear_form()
        self._refresh_table()

    def _handle_update(self):
        if not self._selected_workout_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 buổi tập trong bảng để sửa.")
            return

        sport_name = self._form_sport_combo.get()
        sport_id = self._sport_name_to_id.get(sport_name)
        date_string = self._form_date.get()
        duration_text = self._form_duration.get().strip()
        weight_text = self._form_weight.get().strip()
        note = self._form_note.get().strip()

        new_values = {
            "sport_id": sport_id,
            "date": date_string,
            "duration_minutes": duration_text,
            "note": note,
        }

        if weight_text:
            new_values["weight_kg"] = weight_text

        try:
            self._context.workout_service.update_workout(
                self._selected_workout_id, new_values
            )
        except ValueError as error:
            messagebox.showerror("Không thể cập nhật", str(error))
            return

        messagebox.showinfo("Thành công", "Đã cập nhật buổi tập.")
        self._clear_form()
        self._refresh_table()

    def _handle_delete(self):
        if not self._selected_workout_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 buổi tập trong bảng để xóa.")
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa", "Bạn có chắc chắn muốn xóa buổi tập này không?"
        )

        if not confirm:
            return

        try:
            self._context.workout_service.delete_workout(self._selected_workout_id)
        except ValueError as error:
            messagebox.showerror("Không thể xóa", str(error))
            return

        messagebox.showinfo("Thành công", "Đã xóa buổi tập.")
        self._clear_form()
        self._refresh_table()


def _to_date_object(date_string):
    """Chuyển 'dd/mm/yyyy' thành đối tượng date cho DateEntry.set_date()."""

    from datetime import datetime

    return datetime.strptime(date_string, "%d/%m/%Y").date()
