from dataclasses import dataclass
from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QIntValidator
from PyQt5.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QRadioButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QDialog
)

from algorithm import calculate_all


def fmt_int(value: float) -> str:
    return str(int(round(value)))


#визуальные настройки БЖУ
@dataclass(frozen=True)
class MacroVisual:
    name: str
    color: str

#  шаблон отображения белков, жиров или углеводов.


class MacroBlock(QWidget):
    def __init__(self, visual: MacroVisual, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.visual = visual
        # QVBoxLayout организует элементы вертикально
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        # организует элементы горизонтально
        top_row = QHBoxLayout()
        self.name_label = QLabel(self.visual.name)
        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top_row.addWidget(self.name_label, 1)
        top_row.addWidget(self.percent_label, 0)
        self.percent_label.setVisible(False)

        self.grams_label = QLabel("0 г")
        self.grams_label.setFont(QFont("Arial", 20, QFont.Bold))
        # Визуальные доли нутриентов
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(18)

        self.apply_progress_style()

        layout.addLayout(top_row)
        layout.addWidget(self.grams_label)
        layout.addWidget(self.progress)
    # стилизации
    def apply_progress_style(self) -> None:
        self.progress.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 9px;
                background: rgba(255,255,255,0.6);
            }}
            QProgressBar::chunk {{
                background-color: {self.visual.color};
                border-radius: 9px;
            }}
            """
        )
    # принимает новые данные и  обновляет текст и длину полоски
    def set_values(self, percent: float, grams: float) -> None:
        pct_int = int(round(percent))
        grams_int = int(round(grams))
        self.percent_label.setText(f"{pct_int}%")
        self.grams_label.setText(f"{grams_int} г")
        self.progress.setValue(pct_int)

# диалоговое окно справки


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справочная информация")
        self.setMinimumSize(700, 850)
        self.setStyleSheet("QDialog { background-color: #f8fafc; font-family: 'Segoe UI', Arial; }")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background-color: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 10)

        title = QLabel("Справочная информация")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")

        header_layout.addWidget(title)
        main_layout.addWidget(header)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(8)

        self.cards()
        self.content_layout.addStretch()

        main_layout.addWidget(content_widget)

    def cards(self):
        content_blocks = [
            ("Что такое BMR и TDEE?",
             "BMR — базовая энергия для жизни (дыхание, работа сердца, обмен веществ).\n\n"
             "TDEE — ваши полные энергозатраты за сутки (BMR × активность)."),
            ("Уровень активности",
             "Множитель, учитывающий движение. Без него расчет будет неверным: вы либо не доберете энергии, либо получите избыток."),
            ("Влияние цели на рацион (Дефицит и Профицит)",
             "Для изменения веса мы корректируем норму TDEE:\n\n"
             "Сброс веса: дефицит калорий от нормы TDEE.\n\n"
             "Набор массы: профицит калорий к норме TDEE.\n\n"
             "Поддержание: потребление строго по норме TDEE."),
            ("Почему ±500 ккал?",
             "Это «золотой стандарт» диетологии. Дефицит в 500 ккал позволяет сжигать примерно 0.5 кг жира в неделю — "
             "это считается самой безопасной и стабильной скоростью похудения для взрослого человека без вреда для здоровья."),
            ("Формулы расчета BMR",
             "Миффлин-Сан Жеор: современный стандарт для взрослых (с 1990 г.).\n\n"
             "Шофилд: официальная формула ВОЗ для детей и подростков до 18 лет.\n\n"
             "Кетч-МакАрдл: расчет по сухой мышечной массе (для атлетов).\n\n"
             "ВОЗ (Всемирная орг. здравоохранения): универсальная медицинская база."),
            ("Обратите внимание",
             "Результаты являются оценочными. Перед кардинальным изменением рациона, особенно для ребенка, проконсультируйтесь с врачом.")
        ]

        for title, text in content_blocks:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 12)
            card_layout.setSpacing(6)

            lbl_title = QLabel(title)
            lbl_title.setWordWrap(True)
            lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #364153; border: none;")

            lbl_text = QLabel(text)
            lbl_text.setWordWrap(True)
            lbl_text.setStyleSheet("font-size: 14px; color: #334155; line-height: 1.4; border: none;")

            if title == "Обратите внимание":
                lbl_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #f59e0b; border: none;")
                lbl_text.setStyleSheet("font-size: 13px; color: #6b7280; border: none;")

            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_text)
            self.content_layout.addWidget(card)

# Это основной модуль, который объединяет интерфейс и расчеты.
class CalorieCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор Калорий")
        self.setFixedSize(1400, 900)
        # Переменные для кэширования последних расчетов
        self._last_results: Optional[Dict[str, Any]] = None
        self._last_under_18: Optional[bool] = None
        # Последовательный запуск настройки:
        self._build_ui() #кнопки и поля
        self._apply_styles() # цвета и шрифты
        self._wire_events() # привязываем функции

    # окно делим на 2 части
    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        # делим
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(25, 25, 25, 25)
        root_layout.setSpacing(30)

        self.left_panel = QWidget()
        self.left_panel.setObjectName("leftPanel")
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(20)

        self.left_title = QLabel("КАЛЬКУЛЯТОР КАЛОРИЙ")
        self.left_title.setObjectName("leftMainTitle")
        # Контейнер для всех полей ввода
        self.input_container = QFrame()
        self.input_container.setObjectName("inputContainer")
        self._build_consolidated_inputs()

        self.left_layout.addWidget(self.left_title)
        self.left_layout.addWidget(self.input_container)
        self.left_layout.addStretch(1)

        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightPanel")
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(15)

        self.right_top_row = QHBoxLayout()
        self.right_top_row.addStretch(1)
        self.btn_help = QPushButton("Справка")
        self.btn_help.setObjectName("helpButton")
        self.btn_help.setFixedSize(140, 32)
        self.right_top_row.addWidget(self.btn_help)

        # Две карточки для результатов
        self.group_target = QFrame()
        self.group_target.setObjectName("targetCard")
        self._build_target_card()

        self.group_intermediate = QFrame()
        self.group_intermediate.setObjectName("detailsCard")
        self._build_details_card()

        self.right_layout.addLayout(self.right_top_row)
        self.right_layout.addWidget(self.group_target)
        self.right_layout.addWidget(self.group_intermediate)
        self.right_layout.addStretch(1)

        # Добавляем панели в главный макет с коэффициентом растяжения 1:1
        root_layout.addWidget(self.left_panel, 1)
        root_layout.addWidget(self.right_panel, 1)

    # заполняем элементами картички
    def _build_consolidated_inputs(self) -> None:
        layout = QVBoxLayout(self.input_container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        specs_title = QLabel("Физические параметры")
        specs_title.setObjectName("sectionTitle")
        layout.addWidget(specs_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Диапазон: 3-100")
        self.age_input.setValidator(QIntValidator(3, 100, self))

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Вес (кг)")
        self.weight_input.setValidator(QDoubleValidator(35.0, 250.0, 2, self))

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Рост (см)")
        self.height_input.setValidator(QDoubleValidator(80.0, 250.0, 1, self))

        self.fat_input = QLineEdit()
        self.fat_input.setPlaceholderText("Обязательно для Кетча-МакАрдла")
        self.fat_input.setValidator(QDoubleValidator(5.0, 50.0, 2, self))

        form_layout.addRow("Возраст (лет):", self.age_input)
        form_layout.addRow("Вес (кг):", self.weight_input)
        form_layout.addRow("Рост (см):", self.height_input)
        form_layout.addRow("% жира в теле:", self.fat_input)

        gender_widget = QWidget()
        gender_layout = QHBoxLayout(gender_widget)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        self.rb_male = QRadioButton("Мужской")
        self.rb_female = QRadioButton("Женский")
        self.rb_male.setChecked(True)
        gender_layout.addWidget(self.rb_male)
        gender_layout.addWidget(self.rb_female)
        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.rb_male)
        self.gender_group.addButton(self.rb_female)
        form_layout.addRow("Пол:", gender_widget)

        layout.addLayout(form_layout)

        goal_title = QLabel("Цели и образ жизни")
        goal_title.setObjectName("sectionTitle")
        layout.addWidget(goal_title)

        self.rb_lose = QRadioButton("Сброс веса (-500 ккал)")
        self.rb_maintain = QRadioButton("Поддержание веса")
        self.rb_gain = QRadioButton("Набор массы (+500 ккал)")
        self.rb_maintain.setChecked(True)
        self.goal_group = QButtonGroup(self)
        for rb in (self.rb_lose, self.rb_maintain, self.rb_gain):
            self.goal_group.addButton(rb)
            layout.addWidget(rb)

        self.activity_combo = QComboBox()
        self.activity_combo.addItems([
            "Сидячий (1.2) - Без нагрузок",
            "Низкая активность (1.375) - Занятия 1-3 дня в неделю",
            "Средняя активность (1.55) - Занятия 3-5 дней в неделю",
            "Высокая активность (1.725) - Занятия 6-7 дней в неделю",
            "Экстремальная активность (1.9) - Тяжелая работа / 2 тренировки в день",
        ])
        self.activity_combo.setCurrentIndex(2)
        layout.addWidget(self.activity_combo)

        method_title = QLabel("Формула BMR")
        method_title.setObjectName("sectionTitle")
        layout.addWidget(method_title)

        self.rb_mifflin = QRadioButton("Миффлин-Сан Жеор (Взрослые)")
        self.rb_schofield = QRadioButton("Шофилд (Дети и подростки до 18)")
        self.rb_katch = QRadioButton("Кетч-МакАрдл (Нужен % жира)")
        self.rb_who = QRadioButton("Формула ВОЗ (медицинская, для людей с ожирением)")
        self.rb_mifflin.setChecked(True)
        self.formula_group = QButtonGroup(self)
        for rb in (self.rb_mifflin, self.rb_schofield, self.rb_katch, self.rb_who):
            self.formula_group.addButton(rb)
            layout.addWidget(rb)

        layout.addSpacing(10)
        self.buttons_row = QHBoxLayout()
        self.btn_calc = QPushButton("Рассчитать")
        self.btn_calc.setObjectName("calcButton")
        self.btn_reset = QPushButton("Сброс")
        self.btn_reset.setObjectName("resetButton")

        self.buttons_row.addWidget(self.btn_calc, 4)
        self.buttons_row.addWidget(self.btn_reset, 1)
        layout.addLayout(self.buttons_row)

    # создание блока с главным результатом.
    def _build_target_card(self) -> None:
        layout = QVBoxLayout(self.group_target)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("СУТОЧНАЯ НОРМА")
        title.setObjectName("cardHeader")
        layout.addWidget(title)

        layout.addSpacing(10)

        self.target_placeholder = QLabel("Нажмите «Рассчитать», чтобы увидеть результат.")
        self.target_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.target_placeholder)

        # Контейнер для результатов
        self.target_results_widget = QWidget()
        self.target_results_widget.setObjectName("targetResultsWidget")
        res_layout = QVBoxLayout(self.target_results_widget)
        res_layout.setContentsMargins(0, 0, 0, 0)
        res_layout.setSpacing(0)

        self.daily_calories_label = QLabel("— ккал")
        self.daily_calories_label.setObjectName("bigKcal")
        self.daily_calories_label.setAlignment(Qt.AlignCenter)

        macro_row = QHBoxLayout()
        macro_row.setContentsMargins(0, 0, 0, 0)
        self.block_protein = MacroBlock(MacroVisual("Белки", "#1E88E5"))
        self.block_fat = MacroBlock(MacroVisual("Жиры", "#FB8C00"))
        self.block_carbs = MacroBlock(MacroVisual("Углеводы", "#8E24AA"))
        macro_row.addWidget(self.block_protein)
        macro_row.addWidget(self.block_fat)
        macro_row.addWidget(self.block_carbs)

        # Сборка макета карточки
        res_layout.addWidget(self.daily_calories_label)
        res_layout.addSpacing(15)
        self.macro_title_label = QLabel("Распределение БЖУ:")
        self.macro_title_label.setObjectName("macroTitle")
        self.macro_title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        res_layout.addWidget(self.macro_title_label)
        res_layout.addSpacing(10)
        res_layout.addLayout(macro_row)

        layout.addWidget(self.target_results_widget)
        self.target_results_widget.setVisible(False) # Инкапсуляция: скрываем виджет результатов до момента вычислени

    def _build_details_card(self) -> None:
        layout = QVBoxLayout(self.group_intermediate)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("ДЕТАЛИ РАСЧЕТА")
        title.setObjectName("cardHeader")
        layout.addWidget(title)

        layout.addSpacing(10)

        self.calc_placeholder = QLabel("Здесь появятся подробности расчета.")
        self.calc_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.calc_placeholder)

        self.calc_results_widget = QWidget()
        det_layout = QFormLayout(self.calc_results_widget)
        det_layout.setContentsMargins(0, 0, 0, 0)
        det_layout.setSpacing(10)

        self.bmr_value_label = QLabel("—")
        self.tdee_value_label = QLabel("—")
        self.formula_value_label = QLabel("—")
        self.activity_value_label = QLabel("—")

        det_layout.addRow("Базовый метаболизм (BMR):", self.bmr_value_label)
        det_layout.addRow("Общие энергозатраты (TDEE):", self.tdee_value_label)
        det_layout.addRow("Используемая формула:", self.formula_value_label)
        det_layout.addRow("Коэффициент активности:", self.activity_value_label)

        layout.addWidget(self.calc_results_widget)
        self.calc_results_widget.setVisible(False)

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: 'Segoe UI', Arial; }

            QLabel#leftMainTitle { 
                font-size: 26px; font-weight: 800; color: #1e293b; 
                margin-bottom: 5px; 
            }

            QFrame#inputContainer {
                background-color: #f8f4f9;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
            }

            QLabel#sectionTitle {
                font-size: 14px; font-weight: 800; color: #1e293b;
                margin-top: 10px;
            }

            QFrame#targetCard {
                background-color: #f1faf6;
                border-radius: 16px;
            }
            QFrame#detailsCard {
                background-color: #f0f5fb;
                border-radius: 16px;
            }

            QWidget#targetResultsWidget { border: none; background: transparent;}

            QLabel#cardHeader { font-size: 18px; font-weight: 800; color: #0f172a; border: none; background: transparent;}
            QLabel#bigKcal { font-size: 34px; font-weight: 900; color: #0f172a; margin: 10px 0; border: none; background: transparent;}
            QLabel#macroTitle { font-size: 15px; font-weight: 700; color: #0f172a; border: none; background: transparent;}
            QLabel { background: transparent; }

            QLineEdit, QComboBox {
                border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; background: white;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; }

            QPushButton#calcButton {
                background-color: #0f172a; color: white; border-radius: 12px;
                font-weight: 700; font-size: 15px; height: 48px;
            }
            QPushButton#calcButton:hover { background-color: #1e293b; }

            QPushButton#resetButton {
                background-color: #e2e8f0; color: #475569; border-radius: 12px;
                font-weight: 600; font-size: 14px; height: 48px;
            }
            QPushButton#resetButton:hover { background-color: #cbd5e1; }

            QPushButton#helpButton {
                background-color: #e2e8f0; border: none; border-radius: 10px;
                color: #475569; font-weight: 600;
            }
            QPushButton#helpButton:hover {
                background-color: #cbd5e1;
            }
        """)

    # привязка кнопок к действиям
    def _wire_events(self) -> None:
        # Связывание сигналов интерфейса с логическими методами
        self.btn_calc.clicked.connect(self.calculate)
        self.btn_reset.clicked.connect(self.reset_fields)
        self.btn_help.clicked.connect(self.show_help_from_file)

        self.rb_mifflin.clicked.connect(self._check_formula_age_warning)
        self.rb_schofield.clicked.connect(self._check_formula_age_warning)
        self.rb_who.clicked.connect(self._check_formula_age_warning)
        self.rb_katch.clicked.connect(self._check_formula_age_warning)
        # Моментальная реакция на ввод возраста для соблюдения ограничений ВОЗ
        self.age_input.textChanged.connect(self._enforce_age_restrictions)
        self.age_input.editingFinished.connect(self._age_editing_finished)
        self.rb_lose.toggled.connect(self._enforce_age_restrictions)
        self.rb_gain.toggled.connect(self._enforce_age_restrictions)
        self._enforce_age_restrictions()

    def _check_formula_age_warning(self):
        age_text = self.age_input.text()
        if not age_text:
            return

        if not self.age_input.hasAcceptableInput():
            return

        try:
            age = int(age_text)
        except ValueError:
            return

        if self.rb_schofield.isChecked() and age >= 18:
            QMessageBox.information(self, "Внимание",
                                    "Формула Шофилда предназначена для детей и подростков (до 18 лет).\n\nДля взрослых рекомендуется Миффлин-Сан Жеор.")
        elif not self.rb_schofield.isChecked() and age < 18:
            QMessageBox.information(self, "Внимание",
                                    "Для детей и подростков (до 18 лет) рекомендуется использовать формулу Шофилда.\n\nВзрослые формулы могут дать неверный результат.")

    # Реализует запрет на выбор
    def _enforce_age_restrictions(self) -> None:
        age_text = self.age_input.text().strip()
        try:
            age = int(age_text) if age_text else None
        except ValueError:
            age = None

        under_18 = (age is not None and age < 18)
        if under_18 and not self.rb_schofield.isChecked():
            self.rb_schofield.setChecked(True)

        self.rb_lose.setEnabled(not under_18)
        self.rb_gain.setEnabled(not under_18)

        if under_18 and (self.rb_lose.isChecked() or self.rb_gain.isChecked()):
            self.rb_maintain.setChecked(True)
            QMessageBox.warning(
                self,
                "Ограничение по возрасту",
                "Для лиц младше 18 лет расчёт дефицита/профицита калорий не выполняется (рекомендации ВОЗ).\n"
                "Доступна только цель «Поддержание веса».",
            )

        if age is not None:
            w_min, w_max = self._get_weight_bounds_for_age(age)
            validator = self.weight_input.validator()
            if isinstance(validator, QDoubleValidator):
                validator.setBottom(float(w_min))
                validator.setTop(float(w_max))

        self._last_under_18 = under_18

    # Помогает пользователю выбрать правильную формулу.
    def _age_editing_finished(self) -> None:
        if not self.age_input.text().strip():
            return
        if not self.age_input.hasAcceptableInput():
            return

        age = int(self.age_input.text().strip())
        under_18 = age < 18

        if under_18 and not self.rb_schofield.isChecked():
            self.rb_schofield.setChecked(True)
            QMessageBox.information(
                self,
                "Рекомендация",
                "Для детей и подростков (до 18 лет) автоматически выбрана формула Шофилда (рекомендации ВОЗ).",
            )

    # Возвращает допустимый диапазон веса (мин, макс) в зависимости от возраста.
    def _get_weight_bounds_for_age(self, age: int) -> tuple[float, float]:
        if age < 10:
            return 3.0, 60.0
        if age < 18:
            return 25.0, 150.0
        return 35.0, 250.0

    # извлекает числовой коэффициент активности из выбранной строки
    def _get_activity_factor(self) -> float:
        text = self.activity_combo.currentText()
        try:
            return float(text[text.find("(") + 1: text.find(")")])
        except:
            return 1.55

    # превращает выбранную кнопку цели в понятный коду
    def _get_goal_code(self) -> str:
        if self.rb_lose.isChecked(): return "lose"
        if self.rb_gain.isChecked(): return "gain"
        return "maintain"

    # превращает выбранную кнопку формулы в идентификатор
    def _get_formula_code(self) -> str:
        if self.rb_mifflin.isChecked(): return "mifflin"
        if self.rb_schofield.isChecked(): return "schofield"
        if self.rb_katch.isChecked(): return "katch"
        return "who"

    # Выполняет сбор данных, финальную валидацию и передачу
    def calculate(self) -> None:
        try:
            age_text = self.age_input.text().strip()
            weight_text_raw = self.weight_input.text().strip()
            height_text_raw = self.height_input.text().strip()
            fat_text_raw = self.fat_input.text().strip()

            if not age_text:
                raise ValueError("Поле «Возраст» обязательно для заполнения.")
            if not self.age_input.hasAcceptableInput():
                raise ValueError("Некорректный возраст. Введите целое число в диапазоне 3–100.")
            age = int(age_text)

            if not weight_text_raw:
                raise ValueError("Поле «Вес» обязательно для заполнения.")
            if not self.weight_input.hasAcceptableInput():
                w_min, w_max = self._get_weight_bounds_for_age(age)
                raise ValueError(f"Некорректный вес. Введите число в диапазоне {w_min:g}–{w_max:g} кг для указанного возраста.")
            weight = float(weight_text_raw.replace(",", "."))

            if not height_text_raw:
                raise ValueError("Поле «Рост» обязательно для заполнения.")
            if not self.height_input.hasAcceptableInput():
                raise ValueError("Некорректный рост. Введите число в диапазоне 80–250 см.")
            height = float(height_text_raw.replace(",", "."))

            fat: Optional[float]
            if fat_text_raw:
                if not self.fat_input.hasAcceptableInput():
                    raise ValueError("Некорректный процент жира. Введите число в диапазоне 5–50%.")
                fat = float(fat_text_raw.replace(",", "."))
            else:
                fat = None

            if age < 18 and self._get_goal_code() != "maintain":
                self.rb_maintain.setChecked(True)
                raise ValueError(
                    "Для лиц младше 18 лет расчёт дефицита/профицита калорий не выполняется (рекомендации ВОЗ). "
                    "Выберите цель «Поддержание веса»."
                )

            f_code = self._get_formula_code()

            if age < 18 and f_code != "schofield":
                reply = QMessageBox.warning(self, "Подтверждение",
                                            "Вы используете взрослую формулу для ребенка. Это может исказить норму питания. Продолжить?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No: return

            if age >= 18 and f_code == "schofield":
                reply = QMessageBox.warning(self, "Подтверждение",
                                            "Вы используете детскую формулу для взрослого. Продолжить?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No: return

            if f_code == "katch" and fat is None:
                raise ValueError("Для формулы Кетча-МакАрдла требуется указать процент жира.")

            results = calculate_all(
                weight=weight, height=height, age=age,
                gender="male" if self.rb_male.isChecked() else "female",
                activity_factor=self._get_activity_factor(),
                goal=self._get_goal_code(),
                formula=f_code, fat_percent=fat
            )

            self._apply_results(results)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла непредвиденная ошибка: {e}")

    # Переносит данные результатов в окна
    def _apply_results(self, results: Dict[str, Any]) -> None:
        self._last_results = results
        self.daily_calories_label.setText(f"{fmt_int(results['target_calories'])} ккал")

        self.block_protein.set_values(results["protein_pct"], results["protein_g"])
        self.block_fat.set_values(results["fat_pct"], results["fat_g"])
        self.block_carbs.set_values(results["carbs_pct"], results["carbs_g"])

        self.bmr_value_label.setText(f"{fmt_int(results['bmr'])} ккал/день")
        self.tdee_value_label.setText(f"{fmt_int(results['tdee'])} ккал/день")
        self.formula_value_label.setText(results["formula_name"])
        self.activity_value_label.setText(str(self._get_activity_factor()))
        # Скрываем надписи "Нажмите..."
        self.target_placeholder.setVisible(False)
        self.target_results_widget.setVisible(True)
        self.calc_placeholder.setVisible(False)
        self.calc_results_widget.setVisible(True)

    # Возвращает интерфейс к начальному виду
    def reset_fields(self) -> None:
        for widget in [self.age_input, self.weight_input, self.height_input, self.fat_input]:
            widget.clear()
        self.rb_maintain.setChecked(True)
        self.rb_mifflin.setChecked(True)
        self.activity_combo.setCurrentIndex(2)

        self.target_results_widget.setVisible(False)
        self.target_placeholder.setVisible(True)
        self.calc_results_widget.setVisible(False)
        self.calc_placeholder.setVisible(True)

    def show_help_from_file(self) -> None:
        dialog = HelpDialog(self)
        dialog.exec_()
