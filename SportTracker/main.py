<<<<<<< HEAD
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
=======
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
>>>>>>> 58a8b8e94acf496039f1249903decba46af786fd
    )