"""Các hàm tiện ích dùng chung: hash mật khẩu, sinh ID tự động."""

import hashlib

from utils.constants import DATE_FORMAT
from datetime import datetime


def hash_password(raw_password):
    """Mã hóa mật khẩu bằng SHA-256 (mã hóa cơ bản theo yêu cầu đề bài)."""

    if raw_password is None:
        raise ValueError("Mật khẩu không được để trống.")

    encoded = raw_password.encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def generate_id(prefix, existing_items):
    """Sinh ID mới dạng PREFIX + số thứ tự (VD: U001, W012...).

    existing_items: list các dict đã có, mỗi dict có khóa "id".
    """

    max_number = 0

    for item in existing_items:
        item_id = item.get("id", "")

        if item_id.startswith(prefix):
            number_part = item_id[len(prefix):]

            try:
                number = int(number_part)

                if number > max_number:
                    max_number = number

            except ValueError:
                continue

    new_number = max_number + 1
    return f"{prefix}{new_number:03d}"


def today_string():
    """Trả về ngày hôm nay theo định dạng chuẩn của ứng dụng (dd/mm/yyyy)."""

    return datetime.now().strftime(DATE_FORMAT)


def parse_date(date_string):
    """Chuyển chuỗi 'dd/mm/yyyy' thành đối tượng datetime.

    Ném ValueError nếu sai định dạng (được gọi sau khi đã Validator kiểm tra).
    """

    return datetime.strptime(date_string, DATE_FORMAT)
