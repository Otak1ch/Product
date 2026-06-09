import sys, os
from PyQt6 import QtWidgets, uic, QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

from widgets.colorPicker import ColorPicker
from widgets.todoWidget import TodoWidget
from widgets.linkWidget import LinkWidget
from baseFunctions.dataManager import DataManager

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_save_path(filename="config.json"):
    if hasattr(sys, '_MEIPASS'):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, filename)
    return os.path.join(os.path.abspath("."), filename)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        path_to_config = get_save_path("config.json")
        self.data_manager = DataManager(path_to_config)
        self.widgets = []
        self.drag_pos = None

        ui_path = resource_path('data/ui/app.ui')
        loadUi(ui_path, self)


        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if hasattr(self, 'btnClose'): self.btnClose.clicked.connect(self.close)
        if hasattr(self, 'addColorPicker'): self.addColorPicker.clicked.connect(lambda: self.spawn_widget(ColorPicker))
        if hasattr(self, 'TodoButton'): self.TodoButton.clicked.connect(lambda: self.spawn_widget(TodoWidget))
        if hasattr(self, 'LinkButton'): self.LinkButton.clicked.connect(lambda: self.spawn_widget(LinkWidget))
        if hasattr(self, 'btnDeleteAll'): self.btnDeleteAll.clicked.connect(self.close_all_widgets)

        self.load_session()

    def spawn_widget(self, widget_class, x=None, y=None, w=None, h=None):
        for widget in self.widgets:
            if isinstance(widget, widget_class):
                if widget.isHidden():
                    widget.show()
                widget.raise_()
                widget.activateWindow()
                return widget
        new_widget = widget_class(main_app=self)
        w_type = widget_class.__name__
        last_cfg = self.data_manager.load_all_data().get("last_settings", {}).get(w_type, {})
        final_x = x if x is not None else last_cfg.get("x", self.x() + 50)
        final_y = y if y is not None else last_cfg.get("y", self.y() + 50)
        final_w = w if w is not None else last_cfg.get("w", new_widget.width())
        final_h = h if h is not None else last_cfg.get("h", new_widget.height())
        new_widget.move(int(final_x), int(final_y))
        new_widget.resize(int(final_w), int(final_h))
        if hasattr(new_widget, 'load_content'):
            new_widget.load_content(self.data_manager.get_widget_content(w_type))
        new_widget.show()
        self.widgets.append(new_widget)
        self.save_session()
        return new_widget

    def save_session(self):
        from PyQt6 import sip
        data = self.data_manager.load_all_data()

        if "last_settings" not in data: data["last_settings"] = {}

        self.widgets = [w for w in self.widgets if not sip.isdeleted(w)]


        data["opened_widgets"] = []
        for w in self.widgets:
            w_type = w.__class__.__name__
            w_info = {"type": w_type, "x": w.x(), "y": w.y(), "w": w.width(), "h": w.height()}
            data["opened_widgets"].append(w_info)


            data["last_settings"][w_type] = {"x": w.x(), "y": w.y(), "w": w.width(), "h": w.height()}

            if hasattr(w, 'get_content'):
                if "persistent_data" not in data: data["persistent_data"] = {}
                data["persistent_data"][w_type] = w.get_content()

        data["main_window"] = {"x": self.x(), "y": self.y()}
        self.data_manager.save_all_data(data)

    def load_session(self):
        data = self.data_manager.load_all_data()
        if "main_window" in data:
            m = data["main_window"]
            self.move(m.get("x", 100), m.get("y", 100))

        w_map = {"ColorPicker": ColorPicker, "TodoWidget": TodoWidget, "LinkWidget": LinkWidget}
        for item in data.get("opened_widgets", []):
            if item["type"] in w_map:
                self.spawn_widget(w_map[item["type"]], item["x"], item["y"], item.get("w"), item.get("h"))


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if not isinstance(child, QtWidgets.QPushButton):
                self.drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None;
        self.save_session()

    def close_all_widgets(self):
        for w in self.widgets[:]: w.close()
        self.widgets = [];
        self.save_session()

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