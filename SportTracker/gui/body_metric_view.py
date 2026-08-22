"""BodyMetricView: theo dõi chỉ số cơ thể - CRUD + biểu đồ cân nặng.

Widget nâng cao: Treeview, DateEntry, Canvas (tự vẽ biểu đồ đường
thể hiện xu hướng cân nặng theo thời gian - không dùng thư viện ngoài).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from tkcalendar import DateEntry

from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_DANGER


class BodyMetricView(tk.Frame):
    def __init__(self, parent, user, context):
        super().__init__(parent, bg=COLOR_BACKGROUND)

        self._user = user
        self._context = context
        self._selected_metric_id = None

        self._build_ui()
        self._refresh_table()

    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_table()
        self._build_form()
        self._build_chart()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_table(self):
        table_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 5), pady=15)

        columns = ("id", "date", "weight", "height", "bmi")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=12
        )

        headings = {
            "id": "ID",
            "date": "Ngày",
            "weight": "Cân nặng (kg)",
            "height": "Chiều cao (cm)",
            "bmi": "BMI",
        }

        for col in columns:
            self._tree.heading(col, text=headings[col])
            self._tree.column(col, width=100, anchor="center")

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
            form_frame, text="Chỉ số cơ thể", font=("Segoe UI", 12, "bold"), bg="white"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tk.Label(form_frame, text="Ngày đo:", bg="white").grid(
            row=1, column=0, sticky="w", pady=6
        )
        self._form_date = DateEntry(form_frame, date_pattern="dd/mm/yyyy", width=17)
        self._form_date.grid(row=1, column=1, pady=6)

        tk.Label(form_frame, text="Cân nặng (kg):", bg="white").grid(
            row=2, column=0, sticky="w", pady=6
        )
        self._form_weight = tk.Entry(form_frame, width=20)
        self._form_weight.grid(row=2, column=1, pady=6)

        tk.Label(form_frame, text="Chiều cao (cm):", bg="white").grid(
            row=3, column=0, sticky="w", pady=6
        )
        self._form_height = tk.Entry(form_frame, width=20)
        self._form_height.grid(row=3, column=1, pady=6)

        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0))

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

    def _build_chart(self):
        """Canvas vẽ biểu đồ đường xu hướng cân nặng theo thời gian."""

        chart_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        chart_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))

        tk.Label(
            chart_frame,
            text="Biểu đồ cân nặng theo thời gian",
            font=("Segoe UI", 11, "bold"),
            bg="white",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._chart_canvas = tk.Canvas(
            chart_frame, width=760, height=220, bg="white", highlightthickness=1,
            highlightbackground="#E0E0E0",
        )
        self._chart_canvas.grid(row=1, column=0)

    # ------------------------------------------------------------------
    def _refresh_table(self):
        for row in self._tree.get_children():
            self._tree.delete(row)

        metrics = self._context.body_metric_service.get_metrics_by_user(self._user.id)

        # Sắp xếp theo ngày tăng dần để bảng và biểu đồ nhất quán
        metrics_sorted = sorted(metrics, key=lambda m: _to_date_object(m.date))

        for metric in metrics_sorted:
            self._tree.insert(
                "",
                "end",
                iid=metric.id,
                values=(
                    metric.id,
                    metric.date,
                    metric.weight_kg,
                    metric.height_cm,
                    metric.bmi,
                ),
            )

        self._draw_chart(metrics_sorted)

    def _draw_chart(self, metrics):
        """Vẽ biểu đồ đường bằng Canvas thuần (create_line, create_oval)."""

        canvas = self._chart_canvas
        canvas.delete("all")

        width = int(canvas["width"])
        height = int(canvas["height"])
        margin = 40

        if len(metrics) < 2:
            canvas.create_text(
                width / 2,
                height / 2,
                text="Cần ít nhất 2 lần đo để vẽ biểu đồ xu hướng.",
                fill="gray",
            )
            return

        weights = [m.weight_kg for m in metrics]
        min_weight = min(weights) - 1
        max_weight = max(weights) + 1

        if max_weight == min_weight:
            max_weight += 1

        chart_width = width - 2 * margin
        chart_height = height - 2 * margin
        step_x = chart_width / (len(metrics) - 1)

        def to_canvas_point(index, weight):
            x = margin + index * step_x
            ratio = (weight - min_weight) / (max_weight - min_weight)
            y = height - margin - ratio * chart_height
            return x, y

        # Trục ngang & dọc
        canvas.create_line(margin, height - margin, width - margin, height - margin, fill="#CCCCCC")
        canvas.create_line(margin, margin, margin, height - margin, fill="#CCCCCC")

        points = [to_canvas_point(i, m.weight_kg) for i, m in enumerate(metrics)]

        # Vẽ đường nối các điểm
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill=COLOR_PRIMARY, width=2)

        # Vẽ điểm tròn + nhãn cân nặng tại mỗi điểm
        for (x, y), metric in zip(points, metrics):
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=COLOR_PRIMARY, outline="")
            canvas.create_text(x, y - 14, text=f"{metric.weight_kg:g}", font=("Segoe UI", 8))
            canvas.create_text(x, height - margin + 15, text=metric.date, font=("Segoe UI", 7))

    # ------------------------------------------------------------------
    def _on_select_row(self, event):
        selected = self._tree.selection()

        if not selected:
            return

        metric_id = selected[0]
        values = self._tree.item(metric_id, "values")

        self._selected_metric_id = metric_id

        self._form_date.set_date(_to_date_object(values[1]))

        self._form_weight.delete(0, tk.END)
        self._form_weight.insert(0, str(values[2]))

        self._form_height.delete(0, tk.END)
        self._form_height.insert(0, str(values[3]))

    def _clear_form(self):
        self._selected_metric_id = None
        self._tree.selection_remove(self._tree.selection())
        self._form_weight.delete(0, tk.END)
        self._form_height.delete(0, tk.END)

    # ------------------------------------------------------------------
    def _handle_add(self):
        date_string = self._form_date.get()
        weight_text = self._form_weight.get().strip()
        height_text = self._form_height.get().strip()

        try:
            self._context.body_metric_service.add_metric(
                user_id=self._user.id,
                date_string=date_string,
                weight_kg=weight_text,
                height_cm=height_text,
            )
        except ValueError as error:
            messagebox.showerror("Không thể thêm", str(error))
            return

        messagebox.showinfo("Thành công", "Đã thêm chỉ số cơ thể.")
        self._clear_form()
        self._refresh_table()

    def _handle_update(self):
        if not self._selected_metric_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 dòng trong bảng để sửa.")
            return

        new_values = {
            "date": self._form_date.get(),
            "weight_kg": self._form_weight.get().strip(),
            "height_cm": self._form_height.get().strip(),
        }

        try:
            self._context.body_metric_service.update_metric(
                self._selected_metric_id, new_values
            )
        except ValueError as error:
            messagebox.showerror("Không thể cập nhật", str(error))
            return

        messagebox.showinfo("Thành công", "Đã cập nhật chỉ số cơ thể.")
        self._clear_form()
        self._refresh_table()

    def _handle_delete(self):
        if not self._selected_metric_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 dòng trong bảng để xóa.")
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa", "Bạn có chắc chắn muốn xóa chỉ số này không?"
        )

        if not confirm:
            return

        self._context.body_metric_service.delete_metric(self._selected_metric_id)

        messagebox.showinfo("Thành công", "Đã xóa chỉ số cơ thể.")
        self._clear_form()
        self._refresh_table()


def _to_date_object(date_string):
    from datetime import datetime

    return datetime.strptime(date_string, "%d/%m/%Y").date()
