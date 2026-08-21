"""MainWindow: cửa sổ chính sau khi đăng nhập thành công.

Dùng ttk.Notebook làm menu điều hướng dạng tab tới các view nghiệp vụ.
Tab "Quản trị" chỉ hiện với tài khoản role = admin (phân quyền).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from gui.dashboard import DashboardView
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

        self._add_placeholder_tabs(notebook)

        if self._user.is_admin():
            admin_tab = self._placeholder_tab(notebook, "Quản trị người dùng")
            notebook.add(admin_tab, text="Quản trị")

    def _add_placeholder_tabs(self, notebook):
        """Các tab nghiệp vụ sẽ được hoàn thiện ở các bước tiếp theo."""

        tab_titles = [
            ("Buổi tập", "Quản lý buổi tập (CRUD)"),
            ("Mục tiêu", "Quản lý mục tiêu (CRUD)"),
            ("Chỉ số cơ thể", "Theo dõi chỉ số cơ thể (CRUD)"),
            ("Bài tập", "Thư viện bài tập (từ API)"),
        ]

        for tab_text, title in tab_titles:
            frame = self._placeholder_tab(notebook, title)
            notebook.add(frame, text=tab_text)

    def _placeholder_tab(self, parent, title):
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
