import re
from datetime import datetime


class Validator:

    @staticmethod
    def validate_email(email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if re.match(pattern, email):
            return True

        return False

    @staticmethod
    def validate_phone(phone):
        pattern = r"^0[0-9]{9}$"

        if re.match(pattern, phone):
            return True

        return False

    @staticmethod
    def validate_date(date_string):
        pattern = r"^\d{2}/\d{2}/\d{4}$"

        if not re.match(pattern, date_string):
            return False

        try:
            datetime.strptime(date_string, "%d/%m/%Y")
            return True

        except ValueError:
            return False

    @staticmethod
    def validate_username(username):
        if len(username) < 4:
            return False

        pattern = r"^[a-zA-Z0-9_]+$"

        if re.match(pattern, username):
            return True

        return False

    @staticmethod
    def validate_password(password):
        if len(password) < 6:
            return False

        return True

    @staticmethod
    def validate_required(value):
        if value is None:
            return False

        if str(value).strip() == "":
            return False

        return True

    @staticmethod
    def validate_positive_number(value):
        try:
            number = float(value)

            if number > 0:
                return True

            return False

        except (ValueError, TypeError):
            return False