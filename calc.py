"""Calorie, water and macro calculations (Mifflin-St Jeor)."""

ACTIVITY_WATER = {1.2: 0.0, 1.375: 0.3, 1.55: 0.5, 1.725: 0.7, 1.9: 1.0}  # extra liters
GOAL_DELTA = {"lose": -500, "keep": 0, "gain": 300}
PROTEIN_PER_KG = {"lose": 2.0, "keep": 1.6, "gain": 1.8}


def calculate(sex, age, height, weight, act, goal):
    if sex not in ("m", "f") or goal not in GOAL_DELTA:
        raise ValueError("بيانات غير صحيحة")
    act = float(act)
    if act not in ACTIVITY_WATER:
        raise ValueError("مستوى النشاط غير صحيح")
    age, height, weight = float(age), float(height), float(weight)
    if not (15 <= age <= 90 and 120 <= height <= 230 and 35 <= weight <= 250):
        raise ValueError("تأكد من العمر والطول والوزن")

    bmr = 10 * weight + 6.25 * height - 5 * age + (5 if sex == "m" else -161)
    tdee = bmr * act
    target = tdee + GOAL_DELTA[goal]
    floor = 1500 if sex == "m" else 1200
    floored = target < floor
    target = max(target, floor)

    protein = weight * PROTEIN_PER_KG[goal]
    fat = target * 0.25 / 9
    carbs = max(target - protein * 4 - fat * 9, 0) / 4
    water = weight * 0.033 + ACTIVITY_WATER[act]
    return {
        "bmr": round(bmr), "tdee": round(tdee), "kcal": round(target),
        "protein": round(protein), "carbs": round(carbs), "fat": round(fat),
        "water": round(water, 1), "bmi": round(weight / (height / 100) ** 2, 1),
        "floored": floored, "floor": floor,
    }
