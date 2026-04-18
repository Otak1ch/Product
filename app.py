import sys
import os
from PyQt6 import QtWidgets, uic, QtGui, QtCore
from PyQt6.QtCore import Qt

from widgets.colorPicker import ColorPicker
from widgets.todoWidget import TodoWidget
from widgets.linkWidget import LinkWidget
from baseFunctions.dataManager import DataManager


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        baseDir = os.path.dirname(__file__)
        self.data_manager = DataManager(os.path.join(baseDir, 'data', 'config.json'))
        self.widgets = []
        self.drag_pos = None

        uic.loadUi(os.path.join(baseDir, 'data', 'ui', 'app.ui'), self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Привязка кнопок
        if hasattr(self, 'btnClose'): self.btnClose.clicked.connect(self.close)
        if hasattr(self, 'addColorPicker'): self.addColorPicker.clicked.connect(lambda: self.spawn_widget(ColorPicker))
        if hasattr(self, 'TodoButton'): self.TodoButton.clicked.connect(lambda: self.spawn_widget(TodoWidget))
        if hasattr(self, 'LinkButton'): self.LinkButton.clicked.connect(lambda: self.spawn_widget(LinkWidget))
        if hasattr(self, 'btnDeleteAll'): self.btnDeleteAll.clicked.connect(self.close_all_widgets)

        self.load_session()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if isinstance(child, QtWidgets.QPushButton):
                super().mousePressEvent(event)
                return
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.save_session()
        super().mouseReleaseEvent(event)

    def spawn_widget(self, widget_class, x=None, y=None):
        for widget in self.widgets:
            if isinstance(widget, widget_class):
                widget.raise_();
                return widget

        new_widget = widget_class(main_app=self)
        w_type = widget_class.__name__
        lx, ly = self.data_manager.get_last_position(w_type)
        new_widget.move(int(x or lx or self.x() + 50), int(y or ly or self.y() + 50))

        if hasattr(new_widget, 'load_content'):
            new_widget.load_content(self.data_manager.get_widget_content(w_type))

        new_widget.show()
        self.widgets.append(new_widget)
        self.save_session()
        return new_widget

    def close_all_widgets(self):
        from PyQt6 import sip
        for w in self.widgets[:]:
            if not sip.isdeleted(w): w.close()
        self.widgets = []
        self.save_session()

    def save_session(self):
        from PyQt6 import sip
        data = self.data_manager.load_all_data()
        data["main_window"] = {"x": self.x(), "y": self.y()}
        self.widgets = [w for w in self.widgets if not sip.isdeleted(w)]
        data["opened_widgets"] = [{"type": w.__class__.__name__, "x": w.x(), "y": w.y()} for w in self.widgets]
        for w in self.widgets:
            if hasattr(w, 'get_content'):
                if "persistent_data" not in data: data["persistent_data"] = {}
                data["persistent_data"][w.__class__.__name__] = w.get_content()
        self.data_manager.save_all_data(data)

    def load_session(self):
        data = self.data_manager.load_all_data()
        if "main_window" in data:
            self.move(data["main_window"].get("x", 100), data["main_window"].get("y", 100))
        w_map = {"ColorPicker": ColorPicker, "TodoWidget": TodoWidget, "LinkWidget": LinkWidget}
        for item in data.get("opened_widgets", []):
            if item["type"] in w_map: self.spawn_widget(w_map[item["type"]], item["x"], item["y"])

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 20, 20)
        painter.fillPath(path, QtGui.QColor(30, 30, 30, 240))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())