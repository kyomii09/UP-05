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

# формула воз
def who_formula(weight: float, age: int, gender: str) -> float:
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

# начисление сут. расхода энергии
def calc_tdee(bmr: float, actv_factor: float) -> float:
    return bmr * actv_factor

# определяет целевую калорийность от цели
def calc_goal(tdee: float, goal: str, age: int) -> float:
    if age < 18:
        if goal == "lose": return tdee * 0.90
        if goal == "gain": return tdee * 1.10
        return tdee
    else:
        if goal == "lose": return tdee * 0.85
        if goal == "gain": return tdee * 1.10
        return tdee
# расчет БЖУ
def calc_macros(target_calories: float, weight: float, goal: str, gender: str) -> Tuple[
    float, float, float, int, int, int]:
    # выбор нормы белка
    if goal == "lose":
        protein = 2.0 * weight
    elif goal == "gain":
        protein = 1.5 * weight
    else:
        protein = 1.8 * weight

    fat = 0.8 * weight if gender == "female" else 1.0 * weight
    # перевод в калории
    p_cal = protein * 4
    f_cal = fat * 9
    #расчет углеводов
    remaining_cal = target_calories - p_cal - f_cal
    if remaining_cal < 0:
        remaining_cal = 0
    # переводим в граммы
    carbs = remaining_cal / 4

    total_macro_cals = p_cal + f_cal + remaining_cal

    if total_macro_cals <= 0:
        return 0.0, 0.0, 0.0, 0, 0, 0
    # переводим в проценты доли
    p_pct = int(round((p_cal / total_macro_cals) * 100))
    f_pct = int(round((f_cal / total_macro_cals) * 100))
    c_pct = 100 - p_pct - f_pct
    return protein, fat, carbs, p_pct, f_pct, c_pct

# безопасность мин калорийности
def min_calories(gender: str) -> int:
    return 1200 if gender == "female" else 1500

#перенаправление данных функциям расчета
def calс_bmr(
        weight: float,
        age: int,
        gender: str,
        formula: str,
        height: Optional[float] = None,
        fat_percent: Optional[float] = None,
) -> Tuple[float, str]:
    if formula == "mifflin": return mifflin(weight, height, age, gender), "Миффлин-Сан Жеор"
    if formula == "schofield": return schofield(weight, height, age, gender), "Шофилд (Детская)"
    if formula == "katch":
        if fat_percent is None: raise ValueError("Для Кетча-МакАрдла требуется процент жира")
        return katch_mcardle(weight, fat_percent), "Кетч-МакАрдл"
    if formula == "who": return who_formula(weight, age, gender), "Формула ВОЗ"
    raise ValueError("Неизвестная формула")

#осн. вычислительная функция
def calc_all(
        weight: float,
        age: int,
        gender: str,
        actv_factor: float,
        goal: str,
        formula: str = "mifflin",
        height: Optional[float] = None,
        fat_percent: Optional[float] = None,
) -> Dict[str, Any]:
    # проверка корректности типов данных веса и роста
    if not isinstance(weight, (int, float)):
        raise TypeError("Вес должен быть числовым значением")
    if formula in ("mifflin", "schofield"):
        if height is None or not isinstance(height, (int, float)):
            raise TypeError("Вес и рост должны быть числовыми значениями")
    elif height is not None and not isinstance(height, (int, float)):
        raise TypeError("Рост должен быть числовым значением")
    if not isinstance(age, int):
        raise TypeError("Возраст должен быть целым числом")
    # расчёт базового обмена и получение названия формулы
    bmr, formula_name = calс_bmr(weight, age, gender, formula, height, fat_percent)
    tdee = calc_tdee(bmr, actv_factor) # расчёт общего суточного расхода
    target_calories = calc_goal(tdee, goal, age)  # определение целевой калорийности

    adjusted_min = False
    if age >= 18:
        min_cal = min_calories(gender)
        if target_calories < min_cal:
            target_calories = float(min_cal)
            adjusted_min = True
    # расчёт белков, жиров, углеводов и процентное значение
    protein, fat, carbs, p_pct, f_pct, c_pct = calc_macros(
        target_calories, weight, goal, gender
    )

    return {
        "bmr": bmr,   # базовый уровень метаболизма
        "tdee": tdee,  #суточный расход энергии
        "target_calories": target_calories,  #рекомендуемая калорийность
        "protein": protein,      #белки
        "fat": fat,               #жиры
        "carbs": carbs,           # углеводы
        "protein_pct": p_pct,
        "fat_pct": f_pct,
        "carbs_pct": c_pct,
        "formula_name": formula_name,
        "adjusted_min": adjusted_min,
    }