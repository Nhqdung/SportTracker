"""Custom Widget: CircularProgress - vòng tròn hiển thị % hoàn thành.

Widget tự viết bằng Canvas (không có sẵn trong Tkinter chuẩn),
dùng create_arc() để vẽ cung tròn theo phần trăm, create_text()
để hiển thị số % ở giữa.
"""

import tkinter as tk


class CircularProgress(tk.Canvas):
    """Vòng tròn tiến độ, kế thừa trực tiếp từ tk.Canvas.

    Cách dùng:
        progress = CircularProgress(parent, size=150, thickness=14)
        progress.pack()
        progress.set_progress(65)   # cập nhật lên 65%
    """

    def __init__(
        self,
        parent,
        size=150,
        thickness=14,
        track_color="#E0E0E0",
        progress_color="#4CAF50",
        text_color="#2C3E50",
        font=("Segoe UI", 16, "bold"),
        **kwargs,
    ):
        super().__init__(
            parent,
            width=size,
            height=size,
            highlightthickness=0,
            bg=kwargs.pop("bg", parent["bg"] if "bg" in parent.keys() else "white"),
            **kwargs,
        )

        self._size = size
        self._thickness = thickness
        self._track_color = track_color
        self._progress_color = progress_color
        self._text_color = text_color
        self._font = font
        self._percent = 0.0

        self._draw()

    # ---- Encapsulation: percent chỉ được set qua phương thức kiểm soát ----
    @property
    def percent(self):
        return self._percent

    def set_progress(self, percent):
        """Cập nhật % tiến độ (0-100) và vẽ lại vòng tròn."""

        try:
            value = float(percent)
        except (TypeError, ValueError):
            raise ValueError("Phần trăm tiến độ phải là số.")

        if value < 0:
            value = 0.0
        elif value > 100:
            value = 100.0

        self._percent = value
        self._draw()

    def _color_for_percent(self):
        """Đổi màu vòng tròn theo mức độ hoàn thành để trực quan hơn."""

        if self._percent >= 100:
            return "#4CAF50"  # xanh lá - đã hoàn thành
        if self._percent >= 50:
            return self._progress_color
        return "#E67E22"  # cam - còn xa mục tiêu

    def _draw(self):
        """Vẽ lại toàn bộ vòng tròn (track nền + cung tiến độ + chữ %)."""

        self.delete("all")

        padding = self._thickness / 2 + 2
        x0, y0 = padding, padding
        x1, y1 = self._size - padding, self._size - padding

        # Vòng nền (track) - vẽ đủ 360 độ, màu xám nhạt
        self.create_oval(
            x0, y0, x1, y1,
            outline=self._track_color,
            width=self._thickness,
        )

        # Cung tiến độ - bắt đầu từ 90 độ (đỉnh) vẽ theo chiều kim đồng hồ
        extent = -(self._percent / 100) * 360

        if self._percent > 0:
            self.create_arc(
                x0, y0, x1, y1,
                start=90,
                extent=extent,
                style="arc",
                outline=self._color_for_percent(),
                width=self._thickness,
            )

        # Số % hiển thị giữa vòng tròn
        center = self._size / 2
        self.create_text(
            center, center,
            text=f"{self._percent:.0f}%",
            font=self._font,
            fill=self._text_color,
        )


# ---- Demo chạy độc lập để xem trực quan khi cần kiểm tra riêng widget ----
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo CircularProgress")
    root.geometry("300x300")

    progress = CircularProgress(root, size=180, thickness=16)
    progress.pack(pady=20)
    progress.set_progress(65)

    def increase():
        new_value = min(progress.percent + 10, 100)
        progress.set_progress(new_value)

    tk.Button(root, text="+10%", command=increase).pack()

    root.mainloop()
