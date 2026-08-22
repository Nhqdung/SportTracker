"""AdminView: quản lý người dùng - chỉ hiển thị với tài khoản role = admin.

Cho phép admin xem danh sách người dùng, xóa tài khoản (trừ chính mình),
và đổi quyền user <-> admin.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_DANGER, ROLE_ADMIN, ROLE_USER


class AdminView(tk.Frame):
    def __init__(self, parent, current_user, context):
        super().__init__(parent, bg=COLOR_BACKGROUND)

        self._current_user = current_user
        self._context = context

        self._build_ui()
        self._refresh_table()

    # ------------------------------------------------------------------
    def _build_ui(self):
        tk.Label(
            self,
            text="Quản trị người dùng",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_BACKGROUND,
            fg=COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        table_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))

        columns = ("id", "username", "full_name", "email", "phone", "role")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=16
        )

        headings = {
            "id": "ID",
            "username": "Tên đăng nhập",
            "full_name": "Họ tên",
            "email": "Email",
            "phone": "SĐT",
            "role": "Vai trò",
        }
        widths = {
            "id": 60,
            "username": 110,
            "full_name": 150,
            "email": 170,
            "phone": 100,
            "role": 80,
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

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        btn_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        btn_frame.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="Đổi quyền (User <-> Admin)",
            command=self._handle_toggle_role,
        ).grid(row=0, column=0, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="Xóa người dùng",
            bg=COLOR_DANGER,
            fg="white",
            command=self._handle_delete_user,
        ).grid(row=0, column=1, padx=(0, 10))

        tk.Button(
            btn_frame, text="Làm mới danh sách", command=self._refresh_table
        ).grid(row=0, column=2)

    # ------------------------------------------------------------------
    def _refresh_table(self):
        for row in self._tree.get_children():
            self._tree.delete(row)

        users = self._context.auth_service.get_all_users()

        for user in users:
            self._tree.insert(
                "",
                "end",
                iid=user.id,
                values=(
                    user.id,
                    user.username,
                    user.full_name,
                    user.email,
                    user.phone,
                    user.role,
                ),
            )

    def _get_selected_user_id(self):
        selected = self._tree.selection()

        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 người dùng trong bảng.")
            return None

        return selected[0]

    def _handle_toggle_role(self):
        user_id = self._get_selected_user_id()

        if user_id is None:
            return

        if user_id == self._current_user.id:
            messagebox.showerror("Không hợp lệ", "Không thể tự đổi quyền của chính mình.")
            return

        user_data = self._context.user_storage.find_by_id(user_id)

        if user_data is None:
            messagebox.showerror("Lỗi", "Không tìm thấy người dùng.")
            return

        new_role = ROLE_USER if user_data["role"] == ROLE_ADMIN else ROLE_ADMIN

        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Đổi quyền của '{user_data['username']}' thành '{new_role}'?",
        )

        if not confirm:
            return

        user_data["role"] = new_role
        self._context.user_storage.update(user_id, user_data)

        messagebox.showinfo("Thành công", "Đã đổi quyền người dùng.")
        self._refresh_table()

    def _handle_delete_user(self):
        user_id = self._get_selected_user_id()

        if user_id is None:
            return

        if user_id == self._current_user.id:
            messagebox.showerror("Không hợp lệ", "Không thể xóa chính tài khoản đang đăng nhập.")
            return

        user_data = self._context.user_storage.find_by_id(user_id)
        username = user_data["username"] if user_data else user_id

        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa người dùng '{username}' không?\n"
            "Hành động này không thể hoàn tác.",
        )

        if not confirm:
            return

        self._context.user_storage.delete(user_id)

        messagebox.showinfo("Thành công", "Đã xóa người dùng.")
        self._refresh_table()
