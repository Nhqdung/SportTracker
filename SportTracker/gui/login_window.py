"""LoginWindow: cửa sổ đăng nhập - điểm khởi đầu của ứng dụng."""

import tkinter as tk
from tkinter import messagebox

from utils.app_context import AppContext
from utils.constants import COLOR_PRIMARY, COLOR_BACKGROUND


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SportTracker - Đăng nhập")
        self.geometry("380x340")
        self.resizable(False, False)
        self.configure(bg=COLOR_BACKGROUND)

        # Tạo AppContext 1 lần duy nhất, dùng xuyên suốt sau khi đăng nhập
        self._context = AppContext()

        self._build_ui()

    def _build_ui(self):
        """Toàn bộ layout trong frame này chỉ dùng grid() - không trộn với pack()."""

        container = tk.Frame(self, bg=COLOR_BACKGROUND)
        container.grid(row=0, column=0, padx=30, pady=30)

        tk.Label(
            container,
            text="SportTracker",
            font=("Segoe UI", 20, "bold"),
            bg=COLOR_BACKGROUND,
            fg=COLOR_PRIMARY,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 25))

        tk.Label(container, text="Tên đăng nhập:", bg=COLOR_BACKGROUND).grid(
            row=1, column=0, sticky="w", pady=8
        )
        self._username_entry = tk.Entry(container, width=25)
        self._username_entry.grid(row=1, column=1, pady=8)

        tk.Label(container, text="Mật khẩu:", bg=COLOR_BACKGROUND).grid(
            row=2, column=0, sticky="w", pady=8
        )
        self._password_entry = tk.Entry(container, width=25, show="*")
        self._password_entry.grid(row=2, column=1, pady=8)

        login_btn = tk.Button(
            container,
            text="Đăng nhập",
            bg=COLOR_PRIMARY,
            fg="white",
            width=22,
            command=self._handle_login,
        )
        login_btn.grid(row=3, column=0, columnspan=2, pady=(20, 8))

        register_btn = tk.Button(
            container,
            text="Chưa có tài khoản? Đăng ký ngay",
            relief="flat",
            fg=COLOR_PRIMARY,
            bg=COLOR_BACKGROUND,
            command=self._open_register,
        )
        register_btn.grid(row=4, column=0, columnspan=2)

        hint = tk.Label(
            container,
            text="(Tài khoản admin mặc định: admin / admin123)",
            bg=COLOR_BACKGROUND,
            fg="gray",
            font=("Segoe UI", 8),
        )
        hint.grid(row=5, column=0, columnspan=2, pady=(15, 0))

        # Cho phép nhấn Enter để đăng nhập nhanh
        self.bind("<Return>", lambda event: self._handle_login())
        self._username_entry.focus_set()

    def _handle_login(self):
        username = self._username_entry.get().strip()
        password = self._password_entry.get()

        try:
            user = self._context.auth_service.login(username, password)
        except ValueError as error:
            messagebox.showerror("Đăng nhập thất bại", str(error))
            return

        self.destroy()

        # Import trễ (lazy import) để tránh vòng lặp import giữa các module GUI
        from gui.main_window import MainWindow

        MainWindow(user, self._context).mainloop()

    def _open_register(self):
        from gui.register_window import RegisterWindow

        RegisterWindow(self, self._context.auth_service)


if __name__ == "__main__":
    LoginWindow().mainloop()
