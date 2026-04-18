from PyQt6 import QtCore, QtWidgets


class mouseMove:
    def __init__(self, widget):
        self.widget = widget
        self.drag_start_pos = None

    def handle_press(self, event):
        # Реагируем ТОЛЬКО на левую кнопку мыши
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            child = self.widget.childAt(event.position().toPoint())
            # Если нажали на кнопку, список или поле ввода — не начинаем тащить
            if isinstance(child, (QtWidgets.QPushButton, QtWidgets.QListWidget,
                                  QtWidgets.QLineEdit, QtWidgets.QAbstractItemView)):
                return False

            self.drag_start_pos = event.globalPosition().toPoint()
            event.accept()
            return True
        return False

    def handle_move(self, event):
        if self.drag_start_pos is not None:
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self.drag_start_pos
            self.widget.move(self.widget.pos() + delta)
            self.drag_start_pos = current_pos
            event.accept()
            return True
        return False

    def handle_release(self):
        self.drag_start_pos = None