from api.exercise_api import ExerciseAPI


print("===== TEST EXERCISE API =====")

api = ExerciseAPI()

exercises = api.get_exercises(10)

print("Số bài tập:", len(exercises))

for exercise in exercises:
    print(
        exercise["id"],
        "-",
        exercise["name"],
        "-",
        exercise["category"]
    )