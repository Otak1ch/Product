import sys
import os
import json
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTranslator, QLibraryInfo, QLocale

# Импорты проектных классов
from widgets.colorPicker import ColorPicker
from widgets.linkWidget import LinkWidget
from baseFunctions.mouse import mouseMove
from baseFunctions.utils import UIScaler, apply_adaptive_geometry

class MainWindow(QWidget, mouseMove):
    def __init__(self):
        super().__init__()

        # 1. Настройка путей
        baseDir = os.path.dirname(__file__)
        uiPath = os.path.join(baseDir, 'data', 'ui', 'app.ui')
        self.config_path = os.path.join(baseDir, 'data', 'config.json')



        self.widgets = []

        # 2. Загрузка интерфейса
        if not os.path.exists(uiPath):
            print(f"Критическая ошибка: Не найден {uiPath}")
            return
        uic.loadUi(uiPath, self)

        # 3. Настройка окна
        self.setObjectName("MainUI")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        apply_adaptive_geometry(self, 800, 500)

        # 4. Привязка кнопок
        self.btnClose.clicked.connect(self.close)
        self.addColorPicker.clicked.connect(lambda: self.spawn_widget(ColorPicker))
        self.btnAddLinks.clicked.connect(lambda: self.spawn_widget(LinkWidget))
        self.delWidgetBtn.clicked.connect(self.clear_all_widgets)

        # 5. Восстановление сессии
        self.load_session()

    # --- УПРАВЛЕНИЕ ВИДЖЕТАМИ ---

    def spawn_widget(self, widget_class, x=None, y=None):
        try:
            # 1. Создаем виджет БЕЗ родителя (parent=None), чтобы он был отдельным окном
            new_widget = widget_class()

            # 2. Убираем рамки (если они не прописаны в самом классе виджета)
            new_widget.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Window)
            new_widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

            # 3. Сохраняем ссылку на главное окно в кастомный атрибут,
            # чтобы контекстное меню могло его найти
            new_widget.main_app = self

            # 4. Позиционирование
            if x is not None and y is not None:
                new_widget.move(x, y)
            else:
                new_widget.move(self.x() + 100, self.y() + 100)

            new_widget.show()
            self.widgets.append(new_widget)

            if hasattr(new_widget, 'deleteRequest'):
                new_widget.deleteRequest.connect(self.on_widget_closed)

            return new_widget
        except Exception as e:
            print(f"Ошибка спавна: {e}")

    def on_widget_closed(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
            self.save_session()

    def clear_all_widgets(self):
        for widget in self.widgets[:]:
            widget.close()
        self.widgets.clear()
        self.save_session()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().toRectF()
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 20, 20)
        painter.fillPath(path, QtGui.QColor(30, 30, 30, 240))
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 30), 1)
        painter.setPen(pen)
        painter.drawPath(path)

    # --- СЕССИЯ ---
    def save_session(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        session_data = {
            "main_window": {"x": self.x(), "y": self.y()},
            "opened_widgets": []
        }
        for widget in self.widgets:
            # Проверка на живой объект (sip)
            from PyQt6 import sip
            if sip.isdeleted(widget): continue

            pos = widget.pos()
            data = {
                "type": widget.__class__.__name__,
                "x": pos.x(),
                "y": pos.y()
            }
            if hasattr(widget, 'get_content'):
                data["content"] = widget.get_content()

            session_data["opened_widgets"].append(data)

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)

    def load_session(self):
        if not os.path.exists(self.config_path): return

        widget_map = {"ColorPicker": ColorPicker, "LinkWidget": LinkWidget}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "main_window" in data:
                m = data["main_window"]
                self.move(m.get("x", 100), m.get("y", 100))

            for item in data.get("opened_widgets", []):
                w_type = item.get("type")
                if w_type in widget_map:
                    new_w = self.spawn_widget(widget_map[w_type], item.get("x"), item.get("y"))
                    if new_w and "content" in item and hasattr(new_w, 'load_content'):
                        new_w.load_content(item["content"])

        except Exception as e:
            print(f"Ошибка загрузки сессии: {e}")

    def closeEvent(self, event):
        self.save_session()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    translator = QTranslator(app)
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator.load(QLocale("ru_RU"), "qtbase", "_", path)
    app.installTranslator(translator)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())