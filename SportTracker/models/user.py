"""Model User: đóng gói thông tin người dùng và mật khẩu đã hash."""

from utils.constants import ROLE_ADMIN, ROLE_USER
from utils.helpers import hash_password


class User:
    def __init__(
        self,
        user_id,
        username,
        password_hash,
        full_name,
        email,
        phone,
        role=ROLE_USER,
    ):
        self._id = user_id
        self._username = username
        self._password_hash = password_hash
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self._role = role if role in (ROLE_ADMIN, ROLE_USER) else ROLE_USER

    # ---- Encapsulation: id và username chỉ đọc sau khi tạo ----
    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @property
    def role(self):
        return self._role

    @property
    def password_hash(self):
        return self._password_hash

    def is_admin(self):
        return self._role == ROLE_ADMIN

    def set_password(self, raw_password):
        """Đặt mật khẩu mới - luôn hash trước khi lưu."""
        self._password_hash = hash_password(raw_password)

    def check_password(self, raw_password):
        """So sánh mật khẩu người dùng nhập với hash đã lưu."""
        return hash_password(raw_password) == self._password_hash

    def to_dict(self):
        return {
            "id": self._id,
            "username": self._username,
            "password_hash": self._password_hash,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "role": self._role,
        }

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data.get("id"),
            username=data.get("username"),
            password_hash=data.get("password_hash"),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            role=data.get("role", ROLE_USER),
        )

    def __repr__(self):
        return f"<User {self._username} ({self._role})>"
