import json
import shutil
from pathlib import Path
from datetime import datetime


class JsonManager:
    def __init__(self, file_path, backup_folder="backup"):
        self.file_path = Path(file_path)
        self.backup_folder = Path(backup_folder)

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_folder.mkdir(parents=True, exist_ok=True)

    def read(self):
        """Đọc dữ liệu từ file JSON."""

        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data

        except json.JSONDecodeError as error:
            raise ValueError(
                f"File JSON bị lỗi: {self.file_path}"
            ) from error

        except OSError as error:
            raise OSError(
                f"Không thể đọc file: {self.file_path}"
            ) from error

    def backup(self):
        """Sao lưu file JSON trước khi ghi dữ liệu mới."""

        if not self.file_path.exists():
            return None

        try:
            time_string = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_name = (
                f"{self.file_path.stem}_{time_string}.json"
            )

            backup_path = self.backup_folder / backup_name

            shutil.copy2(self.file_path, backup_path)

            return backup_path

        except OSError as error:
            raise OSError(
                f"Không thể tạo backup cho: {self.file_path}"
            ) from error

    def write(self, data):
        """Ghi toàn bộ dữ liệu vào JSON."""

        try:
            self.backup()

            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError as error:
            raise OSError(
                f"Không thể ghi file: {self.file_path}"
            ) from error

    def add(self, item):
        """Thêm một phần tử vào JSON."""

        data = self.read()

        if not isinstance(data, list):
            raise TypeError("Dữ liệu JSON phải là một danh sách.")

        data.append(item)
        self.write(data)

    def update(self, item_id, new_data):
        """Cập nhật phần tử theo ID."""

        data = self.read()

        if not isinstance(data, list):
            raise TypeError("Dữ liệu JSON phải là một danh sách.")

        found = False

        for index, item in enumerate(data):
            if item.get("id") == item_id:
                data[index] = new_data
                found = True
                break

        if not found:
            raise ValueError(
                f"Không tìm thấy dữ liệu có ID: {item_id}"
            )

        self.write(data)

    def delete(self, item_id):
        """Xóa phần tử theo ID."""

        data = self.read()

        if not isinstance(data, list):
            raise TypeError("Dữ liệu JSON phải là một danh sách.")

        new_data = []

        found = False

        for item in data:
            if item.get("id") == item_id:
                found = True
            else:
                new_data.append(item)

        if not found:
            raise ValueError(
                f"Không tìm thấy dữ liệu có ID: {item_id}"
            )

        self.write(new_data)

    def find_by_id(self, item_id):
        """Tìm một phần tử theo ID."""

        data = self.read()

        if not isinstance(data, list):
            raise TypeError("Dữ liệu JSON phải là một danh sách.")

        for item in data:
            if item.get("id") == item_id:
                return item

        return None