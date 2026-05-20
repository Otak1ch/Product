from PyQt6 import QtCore, QtWidgets


class mouseMove:
    def __init__(self, widget):
        self.widget = widget
        self.drag_start_pos = None
        self.resize_mode = None
        self.margin = 12

    def handle_press(self, event):
        pos = event.position().toPoint()
        self.resize_mode = self._get_resize_mode(pos)

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            child = self.widget.childAt(pos)
            if not self.resize_mode and isinstance(child, (QtWidgets.QPushButton, QtWidgets.QListWidget,
                                                           QtWidgets.QLineEdit, QtWidgets.QAbstractItemView)):
                return False

            self.drag_start_pos = event.globalPosition().toPoint()
            self.start_geometry = self.widget.geometry()
            event.accept()
            return True
        return False

    def handle_move(self, event):
        pos = event.position().toPoint()
        if event.buttons() == QtCore.Qt.MouseButton.NoButton:
            mode = self._get_resize_mode(pos)
            if mode == 'right':
                self.widget.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            elif mode == 'bottom':
                self.widget.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            elif mode == 'both':
                self.widget.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
            else:
                self.widget.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            return False

        if self.drag_start_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            if self.resize_mode:
                w = max(180, self.start_geometry.width() + (
                    delta.x() if 'right' in self.resize_mode or self.resize_mode == 'both' else 0))
                h = max(120, self.start_geometry.height() + (
                    delta.y() if 'bottom' in self.resize_mode or self.resize_mode == 'both' else 0))
                self.widget.resize(w, h)
            else:
                self.widget.move(self.start_geometry.topLeft() + delta)
            event.accept()
            return True
        return False

    def _get_resize_mode(self, pos):
        rect = self.widget.rect()
        r = pos.x() >= rect.width() - self.margin
        b = pos.y() >= rect.height() - self.margin
        if r and b: return 'both'
        if r: return 'right'
        if b: return 'bottom'
        return None

    def handle_release(self):
        self.drag_start_pos = None
        self.resize_mode = None

    # Исправленный вызов меню: используем переданную позицию
    def show_context_menu(self, pos):
        global_pos = self.widget.mapToGlobal(pos)
        menu = QtWidgets.QMenu(self.widget)
        # ... стили меню ...

        if hasattr(self.widget, "add_custom_actions"):
            self.widget.add_custom_actions(menu)

        close_action = menu.addAction("Закрыть виджет")
        action = menu.exec(global_pos)

        if action == close_action:
            # Вместо простого close() используем более надежный метод
            self.widget.close()
            # Явно скрываем, чтобы пользователь сразу видел результат
            self.widget.hide()