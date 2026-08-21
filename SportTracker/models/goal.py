"""Model Goal: mục tiêu tập luyện của người dùng (theo tuần/tháng)."""

from utils.constants import PERIOD_WEEKLY, PERIOD_MONTHLY


class Goal:
    def __init__(
        self,
        goal_id,
        user_id,
        sport_id,
        target_minutes,
        period,
        start_date,
        end_date,
    ):
        self._id = goal_id
        self.user_id = user_id
        self.sport_id = sport_id
        self.target_minutes = target_minutes
        self._period = period if period in (PERIOD_WEEKLY, PERIOD_MONTHLY) else PERIOD_WEEKLY
        self.start_date = start_date
        self.end_date = end_date

    @property
    def id(self):
        return self._id

    @property
    def period(self):
        return self._period

    @property
    def target_minutes(self):
        return self._target_minutes

    @target_minutes.setter
    def target_minutes(self, value):
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Mục tiêu phải là số.") from error

        if number <= 0:
            raise ValueError("Mục tiêu phải lớn hơn 0.")

        self._target_minutes = number

    def progress_percent(self, current_minutes):
        """Tính % hoàn thành mục tiêu, tối đa 100%.

        Dùng làm dữ liệu đầu vào cho widget CircularProgress.
        """

        if self._target_minutes <= 0:
            return 0.0

        percent = (current_minutes / self._target_minutes) * 100
        return round(min(percent, 100.0), 1)

    def to_dict(self):
        return {
            "id": self._id,
            "user_id": self.user_id,
            "sport_id": self.sport_id,
            "target_minutes": self._target_minutes,
            "period": self._period,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    @staticmethod
    def from_dict(data):
        return Goal(
            goal_id=data.get("id"),
            user_id=data.get("user_id"),
            sport_id=data.get("sport_id"),
            target_minutes=data.get("target_minutes", 0),
            period=data.get("period", PERIOD_WEEKLY),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )

    def __repr__(self):
        return f"<Goal {self._id} - {self._target_minutes}p/{self._period}>"
