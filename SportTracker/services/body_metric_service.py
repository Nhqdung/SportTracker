"""BodyMetricService: CRUD chỉ số cơ thể (cân nặng, chiều cao, BMI)."""

from models.body_metric import BodyMetric
from validators.validator import Validator
from utils.helpers import generate_id


class BodyMetricService:
    def __init__(self, body_metric_json_manager):
        self._storage = body_metric_json_manager

    def add_metric(self, user_id, date_string, weight_kg, height_cm):
        if not Validator.validate_date(date_string):
            raise ValueError("Ngày không đúng định dạng dd/mm/yyyy.")

        if not Validator.validate_positive_number(weight_kg):
            raise ValueError("Cân nặng phải là số dương.")

        if not Validator.validate_positive_number(height_cm):
            raise ValueError("Chiều cao phải là số dương.")

        existing = self._storage.read()
        new_id = generate_id("B", existing)

        metric = BodyMetric(
            metric_id=new_id,
            user_id=user_id,
            date=date_string,
            weight_kg=float(weight_kg),
            height_cm=float(height_cm),
        )

        self._storage.add(metric.to_dict())
        return metric

    def update_metric(self, metric_id, new_values):
        current = self._storage.find_by_id(metric_id)

        if current is None:
            raise ValueError(f"Không tìm thấy chỉ số cơ thể ID: {metric_id}")

        current.update(new_values)

        if not Validator.validate_positive_number(current["weight_kg"]):
            raise ValueError("Cân nặng phải là số dương.")

        if not Validator.validate_positive_number(current["height_cm"]):
            raise ValueError("Chiều cao phải là số dương.")

        self._storage.update(metric_id, current)
        return BodyMetric.from_dict(current)

    def delete_metric(self, metric_id):
        self._storage.delete(metric_id)

    def get_metrics_by_user(self, user_id):
        data = self._storage.read()
        return [
            BodyMetric.from_dict(item)
            for item in data
            if item.get("user_id") == user_id
        ]
