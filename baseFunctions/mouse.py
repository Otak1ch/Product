from PyQt6 import QtCore, QtGui, QtWidgets


class mouseMove:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.resizing = False
        self.oldPos = None
        self.margin = 10

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.cursor().shape() != QtCore.Qt.CursorShape.ArrowCursor:
                self.resizing = True
            else:
                self.resizing = False
                self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        # --- ЛОГИКА ИЗМЕНЕНИЯ КУРСОРА ---
        if not event.buttons():
            pos = event.pos()
            is_right = pos.x() > self.width() - self.margin
            is_bottom = pos.y() > self.height() - self.margin

            if is_right and is_bottom:
                self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
            elif is_right:
                self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            elif is_bottom:
                self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            return

        # --- ЛОГИКА ИЗМЕНЕНИЯ РАЗМЕРА ---
        if self.resizing:
            pos = event.pos()
            new_w = max(150, pos.x())
            new_h = max(100, pos.y())
            self.setFixedSize(new_w, new_h)

        # --- ЛОГИКА ПЕРЕМЕЩЕНИЯ ---
        elif self.oldPos is not None:
            currentPos = event.globalPosition().toPoint()
            delta = currentPos - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = currentPos

    def mouseReleaseEvent(self, event):
        # --- СБРОС СОСТОЯНИЙ И КУРСОРA ---
        self.oldPos = None
        self.resizing = False
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        if hasattr(self, 'save_session'):
            self.save_session()