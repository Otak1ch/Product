from PyQt6 import QtWidgets, QtCore

class mouseMove:
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            currentPos = event.globalPosition().toPoint()
            delta = currentPos - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = currentPos
    def mouseReleaseEvent(self, event):
        self.oldPos = None