"""ExerciseView: thư viện bài tập lấy từ API (wger.de), lưu vào JSON.

Widget: Treeview hiển thị danh sách, Entry tìm kiếm nhanh theo tên,
Button gọi API để làm mới dữ liệu.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from api.exercise_api import ExerciseAPI
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY


class ExerciseView(tk.Frame):
    def __init__(self, parent, user, context):
        super().__init__(parent, bg=COLOR_BACKGROUND)

        self._user = user
        self._context = context
        self._api = ExerciseAPI()
        self._all_exercises = []

        self._build_ui()
        self._load_from_storage()

    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_toolbar()
        self._build_table()
        self._build_detail_panel()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=COLOR_BACKGROUND)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=10)

        tk.Label(toolbar, text="Tìm kiếm:", bg=COLOR_BACKGROUND).grid(
            row=0, column=0, padx=(0, 5)
        )

        self._search_entry = tk.Entry(toolbar, width=25)
        self._search_entry.grid(row=0, column=1, padx=(0, 10))
        self._search_entry.bind("<KeyRelease>", self._handle_search)

        tk.Button(
            toolbar,
            text="Làm mới từ API",
            bg=COLOR_PRIMARY,
            fg="white",
            command=self._handle_fetch_from_api,
        ).grid(row=0, column=2, padx=(0, 10))

        self._status_label = tk.Label(
            toolbar, text="", bg=COLOR_BACKGROUND, fg="gray"
        )
        self._status_label.grid(row=0, column=3, padx=(10, 0))

    def _build_table(self):
        table_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=(0, 15))

        columns = ("id", "name", "category", "equipment")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=18
        )

        headings = {
            "id": "ID",
            "name": "Tên bài tập",
            "category": "Danh mục",
            "equipment": "Dụng cụ",
        }
        widths = {"id": 80, "name": 220, "category": 110, "equipment": 150}

        for col in columns:
            self._tree.heading(col, text=headings[col])
            self._tree.column(col, width=widths[col], anchor="w" if col != "id" else "center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._tree.bind("<<TreeviewSelect>>", self._on_select_row)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def _build_detail_panel(self):
        detail_frame = tk.Frame(self, bg="white", padx=15, pady=15, width=260)
        detail_frame.grid(row=1, column=1, sticky="n", padx=(5, 15), pady=(0, 15))

        tk.Label(
            detail_frame, text="Chi tiết bài tập", font=("Segoe UI", 12, "bold"), bg="white"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self._detail_text = tk.Text(
            detail_frame, width=32, height=20, wrap="word", bg="white",
            relief="flat", font=("Segoe UI", 9),
        )
        self._detail_text.grid(row=1, column=0)
        self._detail_text.insert("1.0", "Chọn 1 bài tập trong danh sách để xem chi tiết.")
        self._detail_text.configure(state="disabled")

    # ------------------------------------------------------------------
    def _load_from_storage(self):
        """Nạp dữ liệu đã lưu sẵn trong data/exercise_library.json (nếu có)."""

        data = self._context.exercise_library_storage.read()

        if data:
            self._all_exercises = data
            self._populate_table(self._all_exercises)
            self._status_label.config(text=f"Đã nạp {len(data)} bài tập từ dữ liệu đã lưu.")
        else:
            self._status_label.config(
                text="Chưa có dữ liệu. Bấm 'Làm mới từ API' để tải bài tập."
            )

    def _handle_fetch_from_api(self):
        self._status_label.config(text="Đang tải dữ liệu từ API...")
        self.update_idletasks()

        exercises = self._api.get_exercises(limit=30)

        self._all_exercises = exercises
        self._populate_table(exercises)
        self._status_label.config(text=f"Đã tải và lưu {len(exercises)} bài tập.")

        messagebox.showinfo(
            "Hoàn tất", f"Đã tải {len(exercises)} bài tập và lưu vào exercise_library.json."
        )

    def _populate_table(self, exercises):
        for row in self._tree.get_children():
            self._tree.delete(row)

        for exercise in exercises:
            equipment_text = ", ".join(exercise.get("equipment", []))

            self._tree.insert(
                "",
                "end",
                iid=exercise["id"],
                values=(
                    exercise["id"],
                    exercise.get("name", ""),
                    exercise.get("category", ""),
                    equipment_text,
                ),
            )

    def _handle_search(self, event):
        keyword = self._search_entry.get().strip().lower()

        if not keyword:
            self._populate_table(self._all_exercises)
            return

        filtered = [
            exercise
            for exercise in self._all_exercises
            if keyword in exercise.get("name", "").lower()
        ]
        self._populate_table(filtered)

    def _on_select_row(self, event):
        selected = self._tree.selection()

        if not selected:
            return

        exercise_id = selected[0]
        exercise = next(
            (e for e in self._all_exercises if e["id"] == exercise_id), None
        )

        if exercise is None:
            return

        equipment_text = ", ".join(exercise.get("equipment", [])) or "Không có"

        detail = (
            f"Tên: {exercise.get('name', '')}\n\n"
            f"Danh mục: {exercise.get('category', '')}\n\n"
            f"Dụng cụ: {equipment_text}\n\n"
            f"Mô tả:\n{exercise.get('description', 'Không có mô tả.')}"
        )

        self._detail_text.configure(state="normal")
        self._detail_text.delete("1.0", tk.END)
        self._detail_text.insert("1.0", detail)
        self._detail_text.configure(state="disabled")
