"""RegisterWindow: cửa sổ đăng ký tài khoản mới (dạng popup - Toplevel)."""

import tkinter as tk
from tkinter import messagebox

from utils.constants import COLOR_PRIMARY, COLOR_BACKGROUND


class RegisterWindow(tk.Toplevel):
    def __init__(self, parent, auth_service):
        super().__init__(parent)

        self._auth_service = auth_service

        self.title("Đăng ký tài khoản")
        self.geometry("380x440")
        self.resizable(False, False)
        self.configure(bg=COLOR_BACKGROUND)

        # Modal: khóa tương tác với cửa sổ cha cho đến khi đóng cửa sổ này
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Toàn bộ layout trong frame này chỉ dùng grid()."""

        container = tk.Frame(self, bg=COLOR_BACKGROUND)
        container.grid(row=0, column=0, padx=25, pady=20)

        tk.Label(
            container,
            text="Đăng ký tài khoản mới",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_BACKGROUND,
            fg=COLOR_PRIMARY,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        fields = [
            ("Tên đăng nhập:", "username", None),
            ("Mật khẩu:", "password", "*"),
            ("Xác nhận mật khẩu:", "confirm", "*"),
            ("Họ và tên:", "full_name", None),
            ("Email:", "email", None),
            ("Số điện thoại:", "phone", None),
        ]

        self._entries = {}

        for offset, (label_text, key, show_char) in enumerate(fields):
            row = offset + 1

            tk.Label(container, text=label_text, bg=COLOR_BACKGROUND).grid(
                row=row, column=0, sticky="w", pady=6
            )

            entry = tk.Entry(container, width=25, show=show_char)
            entry.grid(row=row, column=1, pady=6)
            self._entries[key] = entry

        submit_btn = tk.Button(
            container,
            text="Đăng ký",
            bg=COLOR_PRIMARY,
            fg="white",
            width=22,
            command=self._handle_register,
        )
        submit_btn.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(18, 0))

        self._entries["username"].focus_set()

    def _handle_register(self):
        values = {
            key: entry.get().strip() for key, entry in self._entries.items()
        }

        if values["password"] != values["confirm"]:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp.")
            return

        try:
            self._auth_service.register(
                username=values["username"],
                password=values["password"],
                full_name=values["full_name"],
                email=values["email"],
                phone=values["phone"],
            )
        except ValueError as error:
            messagebox.showerror("Đăng ký thất bại", str(error))
            return

        messagebox.showinfo(
            "Thành công", "Đăng ký thành công! Vui lòng đăng nhập."
        )
        self.destroy()
