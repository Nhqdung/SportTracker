import requests

from storage.json_manager import JsonManager


class ExerciseAPI:

    def __init__(self):
        self.api_url = "https://wger.de/api/v2/exerciseinfo/"
        self.json_manager = JsonManager("data/exercise_library.json")

    def fetch_exercises(self, limit=20):
        """Lấy danh sách bài tập từ API."""

        try:
            params = {
                "language": 2,
                "limit": limit
            }

            response = requests.get(
                self.api_url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            return data.get("results", [])

        except requests.exceptions.Timeout as error:
            print("API phản hồi quá lâu.")
            print("Chi tiết:", error)
            return []

        except requests.exceptions.ConnectionError as error:
            print("Không thể kết nối đến API.")
            print("Chi tiết:", error)
            return []

        except requests.exceptions.HTTPError as error:
            print("API trả về lỗi HTTP.")
            print("Chi tiết:", error)
            return []

        except requests.exceptions.RequestException as error:
            print("Có lỗi khi gọi API.")
            print("Chi tiết:", error)
            return []

        except ValueError as error:
            print("Dữ liệu API không đúng định dạng JSON.")
            print("Chi tiết:", error)
            return []

    def clean_data(self, exercises):
        """Làm sạch dữ liệu bài tập từ API."""

        cleaned_exercises = []

        for exercise in exercises:
            exercise_id = exercise.get("id")
            name = exercise.get("name", "")
            description = exercise.get("description", "")
            category = exercise.get("category", {})
            equipment = exercise.get("equipment", [])

            if isinstance(category, dict):
                category_name = category.get("name", "Unknown")
            else:
                category_name = str(category)

            equipment_names = []

            if isinstance(equipment, list):
                for item in equipment:
                    if isinstance(item, dict):
                        equipment_name = item.get("name", "")
                    else:
                        equipment_name = str(item)

                    if equipment_name:
                        equipment_names.append(equipment_name)

            description = self.remove_html(description)

            cleaned_exercise = {
                "id": f"API{exercise_id}",
                "name": name.strip(),
                "category": category_name.strip(),
                "description": description.strip(),
                "equipment": equipment_names
            }

            if cleaned_exercise["name"]:
                cleaned_exercises.append(cleaned_exercise)

        return cleaned_exercises

    def remove_html(self, text):
        """Xóa các thẻ HTML đơn giản trong mô tả."""

        if not text:
            return ""

        result = text

        while "<" in result and ">" in result:
            start = result.find("<")
            end = result.find(">")

            if start < end:
                result = result[:start] + result[end + 1:]
            else:
                break

        return result

    def save_exercises(self, exercises):
        """Lưu danh sách bài tập vào JSON."""

        self.json_manager.write(exercises)

    def get_exercises(self, limit=20):
        """Lấy, làm sạch và lưu bài tập."""

        exercises = self.fetch_exercises(limit)

        if exercises:
            cleaned_exercises = self.clean_data(exercises)
            self.save_exercises(cleaned_exercises)

            return cleaned_exercises

        print("Không lấy được dữ liệu từ API.")
        print("Sử dụng dữ liệu mẫu.")

        mock_exercises = self.get_mock_data()
        self.save_exercises(mock_exercises)

        return mock_exercises

    def get_mock_data(self):
        """Dữ liệu mẫu khi API không hoạt động."""

        return [
            {
                "id": "MOCK001",
                "name": "Push Up",
                "category": "Strength",
                "description": "Bài tập chống đẩy.",
                "equipment": ["None"]
            },
            {
                "id": "MOCK002",
                "name": "Squat",
                "category": "Strength",
                "description": "Bài tập squat cơ bản.",
                "equipment": ["None"]
            },
            {
                "id": "MOCK003",
                "name": "Running",
                "category": "Cardio",
                "description": "Bài tập chạy bộ.",
                "equipment": ["None"]
            },
            {
                "id": "MOCK004",
                "name": "Plank",
                "category": "Core",
                "description": "Bài tập plank tăng cường cơ bụng.",
                "equipment": ["None"]
            },
            {
                "id": "MOCK005",
                "name": "Jumping Jack",
                "category": "Cardio",
                "description": "Bài tập jumping jack.",
                "equipment": ["None"]
            }
        ]