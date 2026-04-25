from __future__ import annotations
from typing import Optional, Dict, Any, Tuple


def mifflin(weight: float, height: float, age: int, gender: str) -> float:
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    return (10 * weight) + (6.25 * height) - (5 * age) - 161


def schofield(weight: float, height_cm: float, age: int, gender: str) -> float:
    h_m = height_cm / 100.0
    if gender == "male":
        if age < 10:
            return (4.4 * weight) + (495 * h_m) + 499
        else:
            return (16.6 * weight) + (77 * h_m) + 572
    else:
        if age < 10:
            return (8.4 * weight) + (465 * h_m) + 200
        else:
            return (7.4 * weight) + (482 * h_m) + 217


def katch_mcardle(weight: float, fat_percent: float) -> float:
    lbm = weight * (1 - (fat_percent / 100))
    return 370 + (21.6 * lbm)


def who_formula(weight: float, age: int, gender: str) -> float:
    if gender == "male":
        if age < 18: return (17.5 * weight) + 651
        if age < 30: return (15.3 * weight) + 679
        if age < 60: return (11.6 * weight) + 879
        return (13.5 * weight) + 487
    else:
        if age < 18: return (12.2 * weight) + 746
        if age < 30: return (14.7 * weight) + 496
        if age < 60: return (8.7 * weight) + 829
        return (10.5 * weight) + 596


def calculate_tdee(bmr: float, activity_factor: float) -> float:
    return bmr * activity_factor


def adjust_goal(tdee: float, goal: str) -> float:
    if goal == "lose": return tdee - 500
    if goal == "gain": return tdee + 500
    return tdee


def calculate_macros(calories: float) -> Tuple[float, float, float, int, int, int]:
    # Стандарт: 30% белки, 30% жиры, 40% углеводы
    p_cal = calories * 0.30
    f_cal = calories * 0.30
    c_cal = calories * 0.40
    return p_cal / 4, f_cal / 9, c_cal / 4, 30, 30, 40


def calculate_bmr(
    weight: float,
    height: float,
    age: int,
    gender: str,
    formula: str,
    fat_percent: Optional[float] = None,
) -> Tuple[float, str]:
    if formula == "mifflin": return mifflin(weight, height, age, gender), "Миффлин-Сан Жеор"
    if formula == "schofield": return schofield(weight, height, age, gender), "Шофилд (Детская)"
    if formula == "katch":
        if fat_percent is None: raise ValueError("Для Кетча-МакАрдла требуется процент жира")
        return katch_mcardle(weight, fat_percent), "Кетч-МакАрдл"
    if formula == "who": return who_formula(weight, age, gender), "Формула ВОЗ"
    raise ValueError("Unknown formula")


def calculate_all(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_factor: float,
    goal: str,
    formula: str = "mifflin",
    fat_percent: Optional[float] = None,
) -> Dict[str, Any]:
    if not isinstance(weight, (int, float)) or not isinstance(height, (int, float)):
        raise TypeError("Вес и рост должны быть числовыми значениями")
    if not isinstance(age, int):
        raise TypeError("Возраст должен быть целым числом")

    bmr, formula_name = calculate_bmr(weight, height, age, gender, formula, fat_percent)
    tdee = calculate_tdee(bmr, activity_factor)
    target_calories = adjust_goal(tdee, goal)
    protein_g, fat_g, carbs_g, p_pct, f_pct, c_pct = calculate_macros(target_calories)

    return {
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carbs_g": carbs_g,
        "protein_pct": p_pct,
        "fat_pct": f_pct,
        "carbs_pct": c_pct,
        "formula_name": formula_name,
    }