import os
from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtWidgets import QColorDialog, QApplication
from PyQt6.QtCore import Qt
from baseFunctions.mouse import mouseMove
from baseFunctions.utils import UIScaler

class ColorPicker(QtWidgets.QWidget, UIScaler):
    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app
        # Инициализируем логику перемещения
        self.mouse_move = mouseMove(self)

        baseDir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(baseDir, '..', 'data', 'ui', 'colorPicker.ui'), self)

        if hasattr(self, 'mainFrame'):
            self.mainFrame.setObjectName("colorMainFrame")
            self.mainFrame.setStyleSheet(
                "#colorMainFrame { background-color: #18181c; border-radius: 15px; border: 1px solid #333; }")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.history = ["#303030"] * 5
        self.history_buttons = [self.clr1, self.clr2, self.clr3, self.clr4, self.clr5]

        self.btnPick.clicked.connect(self.pick_color)
        for btn in self.history_buttons:
            btn.clicked.connect(self.use_history_color)

    # Методы событий мыши перенаправляем в наш класс-помощник
    def mousePressEvent(self, event):
        if not self.mouse_move.handle_press(event):
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.mouse_move.handle_move(event):
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_move.handle_release()
        if self.main_app: self.main_app.save_session()
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        if hasattr(self, 'mainFrame'): self.mainFrame.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def apply_new_color(self, hex_code):
        self.colorHex.setText(hex_code)
        if hasattr(self, 'colorPreview'):
            self.colorPreview.setStyleSheet(f"background-color: {hex_code}; border-radius: 5px; border: 1px solid #444;")
        self.add_to_history(hex_code)
        QApplication.clipboard().setText(hex_code)
        if self.main_app: self.main_app.save_session()

    def pick_color(self):
        color = QColorDialog.getColor(QtGui.QColor("#303030"), self, "Цвет")
        if color.isValid(): self.apply_new_color(color.name().upper())

    def use_history_color(self):
        self.apply_new_color(self.sender().toolTip())

    def add_to_history(self, new_color):
        if new_color in self.history: self.history.remove(new_color)
        self.history.insert(0, new_color)
        if len(self.history) > 5: self.history.pop()
        for i, color in enumerate(self.history):
            self.history_buttons[i].setStyleSheet(f"background-color: {color}; border: none; border-radius: 3px;")
            self.history_buttons[i].setToolTip(color)

    def get_content(self):
        return {"history": self.history, "current": self.colorHex.text()}

    def load_content(self, data):
        if not data: return
        self.history = data.get("history", ["#303030"] * 5)
        self.apply_new_color(data.get("current", "#303030"))