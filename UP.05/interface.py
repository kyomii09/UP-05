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
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QDialog
)

from algorithm import calc_all


def fmt_int(value: float) -> str:
    return str(int(round(value)))

# хранит информацию о том, как должен выглядеть макроэлемент
@dataclass(frozen=True)
class MacroVisual:
    name: str
    color: str

class MacroBlock(QWidget):
    def __init__(self, visual: MacroVisual, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.visual = visual     #сохраняем данные внутри объекта
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)  #расстояние между элементами
        # верхняя строка
        top_row = QHBoxLayout()
        self.name_label = QLabel(self.visual.name)
        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top_row.addWidget(self.name_label, 1)
        top_row.addWidget(self.percent_label, 0)
        self.percent_label.setVisible(False)

        self.grams_label = QLabel("0 г")
        self.grams_label.setFont(QFont("Arial", 20, QFont.Bold))

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(18)

        self.apply_progress_style()

        layout.addLayout(top_row)
        layout.addWidget(self.grams_label)
        layout.addWidget(self.progress)

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
    # обновить данные на карточке БЖУ после расчёта.
    def set_values(self, percent: float, grams: float) -> None:
        pct_int = int(round(percent))
        grams_int = int(round(grams))
        self.percent_label.setText(f"{pct_int}%")
        self.grams_label.setText(f"{grams_int} г")
        self.progress.setValue(pct_int)
# стиль текста
HELP_BODY_STYLE = (
    "font-family: 'Segoe UI', Arial; font-size: 14px; font-weight: 400; "
    "color: #1e293b; line-height: 1.4; border: none; background: transparent;"
)
# стиль заголовков
HELP_TITLE_STYLE = (
    "font-family: 'Segoe UI', Arial; font-size: 14px; font-weight: 800; "
    "color: #1e293b; border: none; background: transparent;"
)
# стиль заголовков предупреждения
HELP_WARNING_TITLE_STYLE = (
    "font-family: 'Segoe UI', Arial; font-size: 14px; font-weight: 800; "
    "color: #f59e0b; border: none; background: transparent;"
)
# стиль текста предупреждения
HELP_WARNING_BODY_STYLE = (
    "font-family: 'Segoe UI', Arial; font-size: 14px; font-weight: 400; "
    "color: #6b7280; line-height: 1.4; border: none; background: transparent;"
)


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справочная информация")
        self.setMinimumSize(700, 600)
        self.resize(720, 780)
        self.setStyleSheet(
            "QDialog { background-color: #f8fafc; font-family: 'Segoe UI', Arial; }"
            "QScrollArea { border: none; background: transparent; }"
        )
        # главный контейнер окна
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # создаем верхнюю панель
        header = QWidget()
        header.setStyleSheet("background-color: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 10)

        title = QLabel("Справочная информация")
        title.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 24px; font-weight: 800; color: #0f172a;"
        )

        header_layout.addWidget(title) # доб заголовок в панель
        main_layout.addWidget(header)  # панель в окно

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # виджет в котором лежит весь текст справки
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(8)

        self.cards()
        self.content_layout.addStretch()  # пустое растягивающее пространство

        scroll.setWidget(content_widget) # содержимое области прокрутки это content_widget.
        main_layout.addWidget(scroll)

    def cards(self):
        content_blocks = [
            ("Что такое BMR и TDEE?",
             "BMR (Basal Metabolic Rate) — базовый обмен веществ. Это минимальное количество энергии, "
             "которое организм тратит в состоянии полного покоя на поддержание жизни "
             "(дыхание, кровообращение, работу мозга и внутренних органов).\n\n"
             "TDEE (Total Daily Energy Expenditure) — общий суточный расход энергии. "
             "Это полная сумма калорий, которую вы сжигаете за сутки. Рассчитывается как базовый метаболизм, "
             "умноженный на коэффициент вашей физической активности."),
            ("Уровень активности",
             "Коэффициент активности — это числовой множитель, который учитывает ваши движения в течение дня. "
             "Без его учёта расчёт будет неточным: вы либо будете недополучать энергию, либо наберёте лишний вес. "
             "В приложении используется 5 официальных уровней активности: от сидячего образа жизни (1.2) "
             "до экстремальных нагрузок (1.9)."),
            ("Формулы расчёта BMR (базового метаболизма)",
             "Для расчёта базовых калорий в приложении реализованы 4 признанные научные методики. "
             "Вы можете выбрать любую в зависимости от ваших особенностей:\n\n"
             "• Миффлин-Сан Жеор (современный стандарт)\n"
             "Разработана в 1990 году и на сегодняшний день признана диетологами как самая точная формула "
             "для большинства взрослых людей, ведущих обычный образ жизни. Учитывает пол, возраст, рост и вес. "
             "В калькуляторе используется по умолчанию.\n\n"
             "• Шофилд (детская и подростковая)\n"
             "Специализированная формула, одобренная Всемирной организацией здравоохранения (ВОЗ) "
             "для детей и подростков от 3 до 17 лет. Учитывает потребности активно растущего организма, "
             "предотвращая опасный дефицит энергии в период созревания.\n\n"
             "• Формула ВОЗ (медицинская база)\n"
             "Классический алгоритм Всемирной организации здравоохранения, построенный на масштабных "
             "популяционных исследованиях. Расчёт опирается на массу тела и фиксированные возрастные группы. "
             "Отлично подходит для стандартизированной оценки и людей с выраженным избыточным весом.\n\n"
             "• Кетч-МакАрдл (экспертный метод)\n"
             "Самая точная формула для тех, кто знает свой состав тела. Рассчитывает метаболизм "
             "исключительно по сухой мышечной массе (LBM), игнорируя жировую ткань. "
             "Идеально подходит для спортсменов с развитой мускулатурой или людей с ожирением. "
             "Требует обязательного ввода процента жира."),
            ("Влияние цели на рацион (дефицит и профицит)",
             "Вместо небезопасных жёстких ограничений в калькуляторе применяется гибкая процентная система "
             "от индивидуального TDEE:\n\n"
             "• Сброс веса: безопасный дефицит 15% от нормы суточных затрат (TDEE × 0.85).\n"
             "• Набор массы: умеренный профицит 10% (TDEE × 1.10).\n"
             "• Поддержание: потребление калорий строго равняется суточным затратам (TDEE).\n\n"
             "⚠ Важно для пользователей младше 18 лет:\n"
             "По рекомендациям ВОЗ для растущего организма агрессивные диеты не рекомендуются. "
             "При выборе целей «Сброс веса» или «Набор массы» для лиц младше 18 лет система автоматически "
             "ограничит дефицит/профицит безопасными рамками — не более 10%."),
            ("Как рассчитываются макронутриенты (БЖУ)?",
             "В калькуляторе реализован профессиональный диетологический расчёт макронутриентов "
             "в граммах на каждый килограмм веса тела (а не деление итоговой калорийности на проценты):\n\n"
             "• Белки: 2.0 г/кг при сбросе веса (для защиты мышц), 1.8 г/кг при поддержании "
             "и 1.5 г/кг при наборе массы.\n"
             "• Жиры: 1.0 г/кг для мужчин и 0.8 г/кг для женщин.\n"
             "• Углеводы: рассчитываются по остаточному принципу — из суточной нормы вычитается "
             "калорийность белков и жиров, оставшаяся энергия переводится в углеводы."),
            ("Защита минимальной калорийности",
             "В калькулятор встроена защита от экстремального голодания для пользователей старше 18 лет. "
             "Если при сильном дефиците расчётная норма оказывается ниже физиологического минимума, "
             "программа показывает предупреждение и предлагает выбор:\n\n"
             "• 1200 ккал — рекомендуемый минимум для женщин.\n"
             "• 1500 ккал — рекомендуемый минимум для мужчин.\n\n"
             "Вы можете применить безопасный порог или оставить расчётное значение — "
             "калькулятор предупреждает о рисках, но уважает ваше решение."),
            ("Обратите внимание",
             "Все результаты, выдаваемые программой, основаны на математических моделях и носят "
             "исключительно ознакомительный и рекомендательный характер. Перед кардинальным изменением "
             "рациона питания, изменением уровня физических нагрузок, а также при составлении меню "
             "для детей и подростков настоятельно рекомендуется проконсультироваться "
             "со специалистом или лечащим врачом."),
        ]
        # создаёт карточки справки
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
            # Создаётся текстовый элемент.
            lbl_title = QLabel(title)
            lbl_title.setWordWrap(True)
            is_warning = title == "Обратите внимание"
            lbl_title.setStyleSheet(HELP_WARNING_TITLE_STYLE if is_warning else HELP_TITLE_STYLE)

            lbl_text = QLabel(text)
            lbl_text.setWordWrap(True)
            lbl_text.setStyleSheet(HELP_WARNING_BODY_STYLE if is_warning else HELP_BODY_STYLE)

            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_text)
            self.content_layout.addWidget(card) # добавляем в главный контейнер окна справки
# создание, настройка главного окна
class CalorieCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор Калорий")
        self.setFixedSize(1400, 900)
        self._last_results: Optional[Dict[str, Any]] = None
        self._last_under_18: Optional[bool] = None
        self._build_ui()
        self._apply_styles()
        self._wire_events()
    # инициализирует центральный виджет и делит окно на две панели (ввод и вывод)
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

        root_layout.addWidget(self.left_panel, 1)
        root_layout.addWidget(self.right_panel, 1)
    # собирает и группирует все элементы управления на левой панели приложения
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
        self.age_input.setObjectName("metricInput")
        self.age_input.setPlaceholderText("Диапазон: 3-100")
        self.age_input.setValidator(QIntValidator(3, 100, self))

        self.weight_input = QLineEdit()
        self.weight_input.setObjectName("metricInput")
        self.weight_input.setPlaceholderText("Диапазон: 1–500 кг")
        self.weight_input.setValidator(QDoubleValidator(1.0, 500.0, 2, self))

        self.height_input = QLineEdit()
        self.height_input.setObjectName("metricInput")
        self.height_input.setPlaceholderText("Диапазон: 30–300 см")
        self.height_input.setValidator(QDoubleValidator(30.0, 300.0, 1, self))

        self.fat_input = QLineEdit()
        self.fat_input.setObjectName("metricInput")
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

        self.rb_lose = QRadioButton("Сброс веса")
        self.rb_maintain = QRadioButton("Поддержание веса")
        self.rb_gain = QRadioButton("Набор массы")
        self.rb_maintain.setChecked(True)
        self.goal_group = QButtonGroup(self)
        for rb in (self.rb_lose, self.rb_maintain, self.rb_gain):
            self.goal_group.addButton(rb)
            layout.addWidget(rb)

        self.activity_combo = QComboBox()
        self.activity_combo.setObjectName("metricInput")
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

        self.rb_mifflin = QRadioButton("Миффлин-Сан Жеор (для взрослых)")
        self.rb_schofield = QRadioButton("Шофилд (для детей и подростков до 18 лет)")
        self.rb_katch = QRadioButton("Кетч-МакАрдл (требуется указать процент жира)")
        self.rb_who = QRadioButton("Формула ВОЗ (универсальная формула)")
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
    # карточка главной суточной нормы
    def _build_target_card(self) -> None:
        layout = QVBoxLayout(self.group_target)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("СУТОЧНАЯ НОРМА")
        title.setObjectName("cardHeader")
        layout.addWidget(title)

        layout.addSpacing(10)
        # скрывается, когда расчет готов
        self.target_placeholder = QLabel("Нажмите «Рассчитать», чтобы увидеть результат.")
        self.target_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.target_placeholder)

        # контейнер с результатами
        self.target_results_widget = QWidget()
        self.target_results_widget.setObjectName("targetResultsWidget")
        res_layout = QVBoxLayout(self.target_results_widget)
        res_layout.setContentsMargins(0, 0, 0, 0)
        res_layout.setSpacing(0)

        self.daily_calories_label = QLabel("— ккал")
        self.daily_calories_label.setObjectName("bigKcal")
        self.daily_calories_label.setAlignment(Qt.AlignCenter)

        # горизонтальный ряд для размещения макронутриентов
        macro_row = QHBoxLayout()
        macro_row.setContentsMargins(0, 0, 0, 0)
        self.block_protein = MacroBlock(MacroVisual("Белки", "#1E88E5"))
        self.block_fat = MacroBlock(MacroVisual("Жиры", "#FB8C00"))
        self.block_carbs = MacroBlock(MacroVisual("Углеводы", "#8E24AA"))
        macro_row.addWidget(self.block_protein)
        macro_row.addWidget(self.block_fat)
        macro_row.addWidget(self.block_carbs)

        res_layout.addWidget(self.daily_calories_label)
        res_layout.addSpacing(15)
        self.macro_title_label = QLabel("Распределение БЖУ:")
        self.macro_title_label.setObjectName("macroTitle")
        self.macro_title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        res_layout.addWidget(self.macro_title_label)
        res_layout.addSpacing(10)
        res_layout.addLayout(macro_row)

        layout.addWidget(self.target_results_widget)
        self.target_results_widget.setVisible(False)

    # карточка промежуточных деталей расчета
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

        # контейнер с результатами
        self.calc_results_widget = QWidget()
        det_layout = QFormLayout(self.calc_results_widget)
        det_layout.setContentsMargins(0, 0, 0, 0)
        det_layout.setSpacing(10)
        # создаем текстовые метки
        self.bmr_value_label = QLabel("—")
        self.tdee_value_label = QLabel("—")
        self.formula_value_label = QLabel("—")
        self.activity_value_label = QLabel("—")
        #  наполняем макет addRow делит строку на две колонки
        det_layout.addRow("Базовый метаболизм (BMR):", self.bmr_value_label)
        det_layout.addRow("Общие энергозатраты (TDEE):", self.tdee_value_label)
        det_layout.addRow("Используемая формула:", self.formula_value_label)
        det_layout.addRow("Коэффициент активности:", self.activity_value_label)

        layout.addWidget(self.calc_results_widget)
        self.calc_results_widget.setVisible(False)
    # оформление приложения
    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: 'Segoe UI', Arial; }
            /* Главный заголовок приложения */
            QLabel#leftMainTitle { 
                font-size: 26px; font-weight: 800; color: #1e293b; 
                margin-bottom: 5px; 
            }
            /* Карточка левой панели*/
            QFrame#inputContainer {
                background-color: #f8f4f9;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
            }
            /* Текстовые подзаголовки разделов внутри левой панели */
            QLabel#sectionTitle {
                font-size: 14px; font-weight: 800; color: #1e293b;
                margin-top: 10px;
            }
            /* Карточка суточной нормы и деталей расчета*/
            QFrame#targetCard {
                background-color: #f1faf6;
                border-radius: 16px;
            }
            QFrame#detailsCard {
                background-color: #f0f5fb;
                border-radius: 16px;
            }

            QWidget#targetResultsWidget { border: none; background: transparent;}
            /* Настройка надписей внутри карточе*/
            QLabel#cardHeader { font-size: 18px; font-weight: 800; color: #0f172a; border: none; background: transparent;}
            QLabel#bigKcal { font-size: 34px; font-weight: 900; color: #0f172a; margin: 10px 0; border: none; background: transparent;}
            QLabel#macroTitle { font-size: 15px; font-weight: 700; color: #0f172a; border: none; background: transparent;}
            /* Делаем фон абсолютно всех надписей прозрачным*/
            QLabel { background: transparent; }

            QLineEdit, QComboBox {
                border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; background: white;
            }
            QLineEdit#metricInput, QComboBox#metricInput {
                padding: 9px 8px;
                min-height: 18px;
            }
            /*  когда пользователь кликает в полео рамка становится синей и выделенной */
            QLineEdit:focus { border: 2px solid #3b82f6; }

            QPushButton#calcButton {
                background-color: #0f172a; color: white; border-radius: 12px;
                font-weight: 700; font-size: 15px; height: 48px;
            }
            /* Эффект наведения мыши для кнопки сброс */
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

    # привязка событий
    def _wire_events(self) -> None:
        # привязка главных кнопок управления к их функционалу
        self.btn_calc.clicked.connect(self.calculate)
        self.btn_reset.clicked.connect(self.reset_fields)
        self.btn_help.clicked.connect(self.show_help_from_file)
        # отслеживание кликов по радиокнопкам формул
        self.rb_mifflin.clicked.connect(self._check_formula_age_warning)
        self.rb_schofield.clicked.connect(self._check_formula_age_warning)
        self.rb_who.clicked.connect(self._check_formula_age_warning)
        self.rb_katch.clicked.connect(self._check_formula_age_warning)
        # контроль ввода возраст
        self.age_input.textChanged.connect(self._enforce_age_restrictions)
        self.age_input.editingFinished.connect(self._age_editing_finished)
        self._enforce_age_restrictions()
    # выводит предупреждающее окно с кнопками да и нет
    def _confirm_da_net(self, title: str, text: str) -> bool:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        da_btn = msg.addButton("Да", QMessageBox.YesRole)
        net_btn = msg.addButton("Нет", QMessageBox.NoRole)
        msg.setDefaultButton(net_btn)
        msg.exec_()
        return msg.clickedButton() == da_btn

    # Отображает стандартное всплывающее уведомление или ошибку с кнопкой ок
    def _show_message(self, title: str, text: str, icon: QMessageBox.Icon = QMessageBox.Information) -> None:
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.addButton("ОК", QMessageBox.AcceptRole)
        msg.exec_()

    # выводит подсказку, если выбрана неподходящая по возрасту формула
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
            self._show_message(
                "Внимание",
                "Формула Шофилда предназначена для детей и подростков (до 18 лет).\n\n"
                "Для взрослых рекомендуется Миффлин-Сан Жеор или иная.",
            )
        elif not self.rb_schofield.isChecked() and age < 18:
            self._show_message(
                "Внимание",
                "Для детей и подростков (до 18 лет) рекомендуется использовать формулу Шофилда.\n\n"
                "Взрослые формулы могут дать неверный результат.",
            )
    #  переключает радиокнопки формул в зависимости от возраста
    def _enforce_age_restrictions(self) -> None:
        age_text = self.age_input.text().strip()
        try:
            age = int(age_text) if age_text else None
        except ValueError:
            age = None

        under_18 = (age is not None and age < 18)
        if under_18 and not self.rb_schofield.isChecked():
            self.rb_schofield.setChecked(True)
        elif age is not None and not under_18 and self.rb_schofield.isChecked():
            self.rb_mifflin.setChecked(True)

        self._last_under_18 = under_18
    # уведомление о неподходящем возрасте
    def _age_editing_finished(self) -> None:
        if not self.age_input.text().strip():
            return
        if not self.age_input.hasAcceptableInput():
            return

        age = int(self.age_input.text().strip())
        under_18 = age < 18

        if under_18 and not self.rb_schofield.isChecked():
            self.rb_schofield.setChecked(True)
            self._show_message(
                "Рекомендация",
                "Для детей и подростков (до 18 лет) автоматически выбрана формула Шофилда (рекомендации ВОЗ).",
            )
    # извлекает значение из текста выпадающего списка с помощью поиска скобок
    def _get_actv_factor(self) -> float:
        text = self.activity_combo.currentText()
        try:
            return float(text[text.find("(") + 1: text.find(")")])
        except:
            return 1.55
    # идентификатор выбранной цели возвращает
    def _get_goal_code(self) -> str:
        if self.rb_lose.isChecked(): return "lose"
        if self.rb_gain.isChecked(): return "gain"
        return "maintain"
    # идентификатор выбранной формулы возвращает
    def _get_formula_code(self) -> str:
        if self.rb_mifflin.isChecked(): return "mifflin"
        if self.rb_schofield.isChecked(): return "schofield"
        if self.rb_katch.isChecked(): return "katch"
        return "who"
    # валидация полей ввода
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
                raise ValueError("Некорректный вес. Введите число в диапазоне 1–500 кг.")
            weight = float(weight_text_raw.replace(",", "."))

            f_code = self._get_formula_code()

            if f_code == "who":
                if height_text_raw:
                    self._show_message(
                        "Информация",
                        "Для формулы ВОЗ рост не нужен.",
                    )
                height = None
            elif not height_text_raw:
                raise ValueError("Поле «Рост» обязательно для заполнения.")
            else:
                if not self.height_input.hasAcceptableInput():
                    raise ValueError("Некорректный рост. Введите число в диапазоне 30–300 см.")
                height = float(height_text_raw.replace(",", "."))

            fat: Optional[float]
            if fat_text_raw:
                if not self.fat_input.hasAcceptableInput():
                    raise ValueError("Некорректный процент жира. Введите число в диапазоне 5–50%.")
                fat = float(fat_text_raw.replace(",", "."))
            else:
                fat = None

            if height is not None:
                height_m = height / 100.0
                bmi = weight / (height_m ** 2)

                if bmi < 15 or bmi > 45:
                    if not self._confirm_da_net(
                        "Проверка ИМТ",
                        f"Ваш ИМТ ({bmi:.1f}) находится вне типового диапазона (15–45).\n"
                        f"Пожалуйста, убедитесь, что рост ({height} см) и вес ({weight} кг) введены верно.\n\n"
                        f"Продолжить расчёт?",
                    ):
                        return

            if age < 18 and self._get_goal_code() != "maintain":
                if not self._confirm_da_net(
                    "Предупреждение",
                    "Изменение массы тела (сброс/набор) не рекомендуется для лиц младше 18 лет "
                    "без назначения врача.\n\n"
                    "Дефицит/профицит будет ограничен безопасными 10%. Продолжить расчёт?",
                ):
                    self.rb_maintain.setChecked(True)
                    return

            if age < 18 and f_code != "schofield":
                if not self._confirm_da_net(
                    "Подтверждение",
                    "Вы используете взрослую формулу для ребёнка. Это может исказить норму питания. Продолжить?",
                ):
                    return

            if age >= 18 and f_code == "schofield":
                if not self._confirm_da_net(
                    "Подтверждение",
                    "Вы используете детскую формулу для взрослого. Продолжить?",
                ):
                    return

            if f_code == "katch" and fat is None:
                raise ValueError("Для формулы Кетча-МакАрдла требуется указать процент жира.")

            gender = "male" if self.rb_male.isChecked() else "female"
            goal = self._get_goal_code()

            results = calc_all(
                weight=weight,
                age=age,
                gender=gender,
                actv_factor=self._get_actv_factor(),
                goal=goal,
                formula=f_code,
                height=height,
                fat_percent=fat,
            )

            if results.get("adjusted_min"):
                self._show_message(
                    "Защита минимальной калорийности",
                    f"Расчётное значение калорий оказалось ниже безопасного медицинского минимума "
                    f"(1200 ккал для женщин, 1500 ккал для мужчин).\n"
                    f"Значение было автоматически скорректировано до "
                    f"{fmt_int(results['target_calories'])} ккал.",
                )

            self._apply_results(results)

        except ValueError as e:
            self._show_message("Ошибка ввода", str(e), QMessageBox.Warning)
        except Exception as e:
            self._show_message("Ошибка", f"Произошла непредвиденная ошибка: {e}", QMessageBox.Critical)
    # обновление текстовых меток
    def _apply_results(self, results: Dict[str, Any]) -> None:
        self._last_results = results
        self.daily_calories_label.setText(f"{fmt_int(results['target_calories'])} ккал")

        self.block_protein.set_values(results["protein_pct"], results["protein"])
        self.block_fat.set_values(results["fat_pct"], results["fat"])
        self.block_carbs.set_values(results["carbs_pct"], results["carbs"])

        self.bmr_value_label.setText(f"{fmt_int(results['bmr'])} ккал/день")
        self.tdee_value_label.setText(f"{fmt_int(results['tdee'])} ккал/день")
        self.formula_value_label.setText(results["formula_name"])
        self.activity_value_label.setText(str(self._get_actv_factor()))
        self.target_placeholder.setVisible(False)
        self.target_results_widget.setVisible(True)
        self.calc_placeholder.setVisible(False)
        self.calc_results_widget.setVisible(True)
    # очистка полей и возврат к исходному состоянию
    def reset_fields(self) -> None:
        for widget in [self.age_input, self.weight_input, self.height_input, self.fat_input]:
            widget.clear()
    # возврат переключателей к дефолтным значениям
        self.rb_maintain.setChecked(True)
        self.rb_mifflin.setChecked(True)
        self.activity_combo.setCurrentIndex(2)
        #  Скрытие виджетов с результатами и возвращение текстовых подсказок
        self.target_results_widget.setVisible(False)
        self.target_placeholder.setVisible(True)
        self.calc_results_widget.setVisible(False)
        self.calc_placeholder.setVisible(True)
    # вызов окна справки
    def show_help_from_file(self) -> None:
        dialog = HelpDialog(self)
        dialog.exec_()