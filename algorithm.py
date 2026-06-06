from __future__ import annotations
from typing import Optional, Dict, Any, Tuple


def mifflin(weight: float, height: float, age: int, gender: str) -> float:
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    return (10 * weight) + (6.25 * height) - (5 * age) - 161


def schofield(weight: float, height: float, age: int, gender: str) -> float:
    calc_age = min(age, 17)
    if gender == "male":
        if calc_age < 10:
            return (22.7 * weight) + 495
        return (17.5 * weight) + 651
    if calc_age < 10:
        return (22.5 * weight) + 499
    return (12.2 * weight) + 746


def katch_mcardle(weight: float, fat_percent: float) -> float:
    lbm = weight * (1 - (fat_percent / 100))
    return 370 + (21.6 * lbm)


def who_formula(weight: float, age: int, gender: str) -> float:
    # ВОЗ: 18–30, 31–60, старше 60; для <18 — младшая взрослая группа (18–30)
    calc_age = max(age, 18)
    if gender == "male":
        if calc_age <= 30:
            return (15.3 * weight) + 679
        if calc_age <= 60:
            return (11.6 * weight) + 879
        return (13.5 * weight) + 487
    if calc_age <= 30:
        return (14.7 * weight) + 496
    if calc_age <= 60:
        return (8.7 * weight) + 829
    return (10.5 * weight) + 596


def calculate_tdee(bmr: float, activity_factor: float) -> float:
    return bmr * activity_factor


def adjust_goal(tdee: float, goal: str, age: int) -> float:
    if age < 18:
        if goal == "lose": return tdee * 0.90
        if goal == "gain": return tdee * 1.10
        return tdee
    else:
        if goal == "lose": return tdee * 0.85
        if goal == "gain": return tdee * 1.10
        return tdee


def calculate_macros(target_calories: float, weight: float, goal: str, gender: str) -> Tuple[
    float, float, float, int, int, int]:
    if goal == "lose":
        protein_g = 2.0 * weight
    elif goal == "gain":
        protein_g = 1.5 * weight
    else:
        protein_g = 1.8 * weight

    fat_g = 0.8 * weight if gender == "female" else 1.0 * weight

    p_cal = protein_g * 4
    f_cal = fat_g * 9

    remaining_cal = target_calories - p_cal - f_cal
    if remaining_cal < 0:
        remaining_cal = 0

    carbs_g = remaining_cal / 4

    total_macro_cals = p_cal + f_cal + remaining_cal
    if total_macro_cals == 0:
        return 0, 0, 0, 0, 0, 0

    p_pct = int(round((p_cal / total_macro_cals) * 100))
    f_pct = int(round((f_cal / total_macro_cals) * 100))
    c_pct = int(round((remaining_cal / total_macro_cals) * 100))

    return protein_g, fat_g, carbs_g, p_pct, f_pct, c_pct


def get_min_calories(gender: str) -> int:
    return 1200 if gender == "female" else 1500


def apply_target_calories(
        results: Dict[str, Any],
        target_calories: float,
        weight: float,
        goal: str,
        gender: str,
) -> Dict[str, Any]:
    protein_g, fat_g, carbs_g, p_pct, f_pct, c_pct = calculate_macros(
        target_calories, weight, goal, gender
    )
    updated = dict(results)
    updated.update({
        "target_calories": target_calories,
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carbs_g": carbs_g,
        "protein_pct": p_pct,
        "fat_pct": f_pct,
        "carbs_pct": c_pct,
    })
    return updated


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
    target_calories = adjust_goal(tdee, goal, age)

    min_cal: Optional[int] = get_min_calories(gender) if age >= 18 else None
    below_min = min_cal is not None and target_calories < min_cal

    protein_g, fat_g, carbs_g, p_pct, f_pct, c_pct = calculate_macros(target_calories, weight, goal, gender)

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
        "below_min": below_min,
        "min_cal": min_cal,
    }