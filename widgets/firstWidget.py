import os
from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtCore import pyqtSignal, Qt
from baseFunctions.mouse import mouseMove


class FirstWidget(QtWidgets.QWidget, mouseMove):
    deleteRequest = pyqtSignal(object)

    def __init__(self,data=None):
        super().__init__(None)
        baseDir = os.path.dirname(__file__)
        ui_path = os.path.normpath(os.path.join(baseDir, '..', 'data','ui', 'firstWidget.ui'))

        if not os.path.exists(ui_path):
            print(f"Ошибка: UI файл виджета не найден: {ui_path}")
            return
        uic.loadUi(ui_path, self)

        self.oldPos = None



        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setObjectName("firstWidget")
        self.setWindowTitle("First Widget")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowStaysOnBottomHint |
            Qt.WindowType.FramelessWindowHint
        )

    def closeEvent(self, event):
        self.deleteRequest.emit(self)
        super().closeEvent(event)

    def paintEvent(self, event):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        # Действия в меню
        open_main = menu.addAction("Панель управления")
        menu.addSeparator()
        close_app = menu.addAction("Выйти из программы")

        # Выполняем меню в позиции курсора
        action = menu.exec(event.globalPos())

        if action == open_main:
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if widget.objectName() == "mainWindow":
                    widget.show()
                    widget.raise_()

        elif action == close_app:
            QtWidgets.QApplication.quit()





