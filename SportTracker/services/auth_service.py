"""AuthService: đăng ký, đăng nhập, kiểm tra quyền."""

from models.user import User
from validators.validator import Validator
from utils.helpers import hash_password, generate_id
from utils.constants import ROLE_USER


class AuthService:
    def __init__(self, user_json_manager):
        self._storage = user_json_manager

    def register(self, username, password, full_name, email, phone):
        """Đăng ký tài khoản mới (mặc định role = user).

        Ném ValueError với thông báo cụ thể nếu dữ liệu không hợp lệ.
        """

        if not Validator.validate_username(username):
            raise ValueError(
                "Tên đăng nhập phải >= 4 ký tự, chỉ gồm chữ, số, dấu gạch dưới."
            )

        if not Validator.validate_password(password):
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự.")

        if not Validator.validate_email(email):
            raise ValueError("Email không đúng định dạng.")

        if not Validator.validate_phone(phone):
            raise ValueError("Số điện thoại không đúng định dạng (10 số, bắt đầu 0).")

        if not Validator.validate_required(full_name):
            raise ValueError("Họ tên không được để trống.")

        existing_users = self._storage.read()

        for item in existing_users:
            if item.get("username") == username:
                raise ValueError("Tên đăng nhập đã tồn tại.")

        new_id = generate_id("U", existing_users)

        new_user = User(
            user_id=new_id,
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            email=email,
            phone=phone,
            role=ROLE_USER,
        )

        self._storage.add(new_user.to_dict())
        return new_user

    def login(self, username, password):
        """Đăng nhập, trả về đối tượng User nếu thành công."""

        if not Validator.validate_required(username):
            raise ValueError("Vui lòng nhập tên đăng nhập.")

        if not Validator.validate_required(password):
            raise ValueError("Vui lòng nhập mật khẩu.")

        users = self._storage.read()

        for item in users:
            if item.get("username") == username:
                user = User.from_dict(item)

                if user.check_password(password):
                    return user

                raise ValueError("Sai mật khẩu.")

        raise ValueError("Tài khoản không tồn tại.")

    def get_user_by_id(self, user_id):
        data = self._storage.find_by_id(user_id)

        if data is None:
            return None

        return User.from_dict(data)

    def get_all_users(self):
        return [User.from_dict(item) for item in self._storage.read()]
