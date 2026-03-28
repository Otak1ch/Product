import os
from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtWidgets import QColorDialog, QApplication
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from baseFunctions.mouse import mouseMove


class ColorPicker(QtWidgets.QWidget, mouseMove):
    deleteRequest = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        # 1. Загрузка интерфейса
        baseDir = os.path.dirname(__file__)
        ui_path = os.path.normpath(os.path.join(baseDir, '..', 'data', 'ui', 'colorPicker.ui'))
        uic.loadUi(ui_path, self)

        # 2. Настройки окна (Без рамок, прозрачный фон, поверх всех окон)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.oldPos = None
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowStaysOnBottomHint |
            Qt.WindowType.FramelessWindowHint
        )

        # 3. Данные
        self.history = ["#303030"] * 5
        self.history_buttons = [self.clr1, self.clr2, self.clr3, self.clr4, self.clr5]

        # 4. Инициализация коннектов
        self.setup_connections()
        self.update_history_ui()

    def setup_connections(self):
        """Привязка событий к функциям"""
        self.btnPick.clicked.connect(self.pick_color)
        self.colorHex.selectionChanged.connect(self.copy_to_clipboard)
        for btn in self.history_buttons:
            btn.clicked.connect(self.use_history_color)

    # --- ЛОГИКА ВЫБОРА ЦВЕТА ---

    def pick_color(self):
        """Выбор нового цвета"""
        initial_color = QtGui.QColor(self.colorHex.text() if self.colorHex.text() else "#303030")
        color = QColorDialog.getColor(initial_color, self, "Выбор цвета")

        if color.isValid():
            hex_name = color.name().upper()

            # 1. Визуально отображаем
            self.colorHex.setText(hex_name)
            self.colorPreview.setStyleSheet(f"background-color: {hex_name}; border-radius: 5px;")

            # 2. Обновляем историю (только для новых цветов из палитры)
            self.add_to_history(hex_name)

            # 3. Копируем
            self.copy_to_clipboard()

    def apply_new_color(self, hex_code):
        """Обновляет интерфейс и добавляет цвет в историю"""
        self.colorHex.setText(hex_code)
        self.colorPreview.setStyleSheet(f"background-color: {hex_code}; border-radius: 5px;")


        self.add_to_history(hex_code)
        self.copy_to_clipboard()

    # --- РАБОТА С ИСТОРИЕЙ ---

    def add_to_history(self, new_color):
        """Сдвигает историю и добавляет новый цвет в начало"""
        if new_color in self.history:
            self.history.remove(new_color)

        self.history.insert(0, new_color)

        if len(self.history) > 5:
            self.history.pop()

        self.update_history_ui()

    def update_history_ui(self):
        """Красит кнопки истории в актуальные цвета"""
        for i, color in enumerate(self.history):
            self.history_buttons[i].setStyleSheet(f"background-color: {color}; border: none; border-radius: 3px;")
            self.history_buttons[i].setToolTip(color)

    def use_history_color(self):
        """Просто использует цвет из истории без перетасовки кнопок"""
        button = self.sender()
        color = button.toolTip()
        self.colorHex.setText(color)
        self.colorPreview.setStyleSheet(f"background-color: {color}; border-radius: 5px;")

        # Копируем в буфер
        self.copy_to_clipboard()
    # --- СЛУЖЕБНЫЕ ФУНКЦИИ ---

    def copy_to_clipboard(self):
        """Копирует текст в буфер обмена и показывает статус"""
        text = self.colorHex.text()
        if text:
            QApplication.clipboard().setText(text)
            self.copyStatusLbl.setText("Copied!")
            QTimer.singleShot(1500, lambda: self.copyStatusLbl.setText(""))

    def closeEvent(self, event):
        self.deleteRequest.emit(self)
        super().closeEvent(event)

    def get_content(self):
        """Возвращает данные для сохранения в JSON"""
        return {
            "history": self.history,
            "current": self.colorHex.text()
        }

    def load_content(self, data):
        """Загружает данные из JSON обратно в виджет"""
        if not data: return

        self.history = data.get("history", ["#303030"] * 5)
        last_color = data.get("current", "#303030")

        # Обновляем визуальную часть
        self.colorHex.setText(last_color)
        self.colorPreview.setStyleSheet(f"background-color: {last_color}; border-radius: 5px;")
        self.update_history_ui()